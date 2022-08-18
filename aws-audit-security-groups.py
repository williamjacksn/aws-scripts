"""
This tool will check all security groups in all regions for an AWS account, looking for inbound rules for 0.0.0.0/0.
If you want to look for a different range, specify the range as the first command line argument.
The range search is exact, i.e. if you search for 1.2.3.4/32, it will not find 1.2.3.4/31 or anything else.
"""

import argparse
import boto3
import botocore.exceptions
import logging
import os
import sys

log = logging.getLogger(__name__)


class Settings:
    def __init__(self):
        self.log_format = os.getenv('LOG_FORMAT', '%(levelname)s [%(name)s] %(message)s')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.version = os.getenv('IMAGE_VERSION', 'unknown')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('target_range', nargs='?', default='0.0.0.0/0')
    return parser.parse_args()


def get_available_regions():
    session = boto3.session.Session()
    return session.get_available_regions('ec2')


def search_for_range(region, sg, target_range: str):
    for perm in sg.ip_permissions:
        for ip_range in perm.get('IpRanges'):
            cidr_ip = ip_range.get('CidrIp')
            if cidr_ip == target_range:
                description = ip_range.get('Description')
                log.info(f'{region} {sg.id} {sg.group_name} {cidr_ip} {description}')


def main():
    settings = Settings()
    logging.basicConfig(format=settings.log_format, level='DEBUG', stream=sys.stdout)
    log.debug(f'audit-security-groups {settings.version}')
    if not settings.log_level == 'DEBUG':
        log.debug(f'Changing log level to {settings.log_level}')
    logging.getLogger().setLevel(settings.log_level)

    args = parse_args()

    log.info(f'Searching for inbound rules for {args.target_range}')
    for region in get_available_regions():
        ec2 = boto3.resource('ec2', region_name=region)
        try:
            for sg in ec2.security_groups.all():
                search_for_range(region, sg, args.target_range)
        except botocore.exceptions.ClientError:
            log.warning(f'Skipping region {region}')


if __name__ == '__main__':
    main()
