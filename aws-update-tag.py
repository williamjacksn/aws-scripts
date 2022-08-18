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
        self.new_value = os.getenv('NEW_VALUE')
        self.old_value = os.getenv('OLD_VALUE')
        self.tag_name = os.getenv('TAG_NAME')
        self.version = os.getenv('IMAGE_VERSION', 'unknown')


def get_available_regions():
    session = boto3.session.Session()
    return session.get_available_regions('ec2')


def main():
    settings = Settings()
    logging.basicConfig(format=settings.log_format, level='DEBUG', stream=sys.stdout)
    log.debug(f'update-tag {settings.version}')
    if not settings.log_level == 'DEBUG':
        log.debug(f'Changing log level to {settings.log_level}')
    logging.getLogger().setLevel(settings.log_level)
    log.info(f'Changing {settings.tag_name} from {settings.old_value} to {settings.new_value}')
    for region in get_available_regions():
        ec2 = boto3.resource('ec2', region_name=region)
        try:
            filters = [{'Name': 'tag-key', 'Values': [settings.tag_name]}]
            tags = [{'Key': settings.tag_name, 'Value': settings.new_value}]
            instances = ec2.instances.filter(Filters=filters)
            instances.create_tags(Tags=tags)
            for image in ec2.images.filter(Filters=filters):
                image.create_tags(Tags=tags)
        except botocore.exceptions.ClientError:
            log.warning(f'Skipping region {region}')


if __name__ == '__main__':
    main()
