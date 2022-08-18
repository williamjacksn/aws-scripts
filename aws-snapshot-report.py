import boto3
import botocore.exceptions
import csv
import logging
import os
import pathlib
import sys

from typing import Dict

log = logging.getLogger(__name__)


class Settings:
    def __init__(self):
        self.log_format = os.getenv('LOG_FORMAT', '%(levelname)s [%(name)s] %(message)s')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.output_file = pathlib.Path(os.getenv('OUTPUT_FILE', '/data/snapshots.csv')).resolve()
        self.owner_id = os.getenv('OWNER_ID')
        self.version = os.getenv('IMAGE_VERSION', 'unknown')


def get_available_regions():
    session = boto3.session.Session()
    return session.get_available_regions('ec2')


def tag_list_to_dict(tag_list):
    if tag_list is None:
        return {}
    return {t.get('Key'): t.get('Value') for t in tag_list}


def get_snapshot_data(region, snapshot) -> Dict:
    tags = tag_list_to_dict(snapshot.tags)
    return {
        'data_encryption_key_id': snapshot.data_encryption_key_id,
        'description': snapshot.description,
        'encrypted': snapshot.encrypted,
        'kms_key_id': snapshot.kms_key_id,
        'owner_alias': snapshot.owner_alias,
        'owner_id': snapshot.owner_id,
        'progress': snapshot.progress,
        'snapshot_id': snapshot.id,
        'start_time': snapshot.start_time,
        'state': snapshot.state,
        'state_message': snapshot.state_message,
        'volume_id': snapshot.volume_id,
        'volume_size_gb': snapshot.volume_size,
        'tag_NAME': tags.get('NAME'),
        'tag_OWNEREMAIL': tags.get('OWNEREMAIL'),
        'region': region
    }


def main():
    settings = Settings()
    logging.basicConfig(format=settings.log_format, level='DEBUG', stream=sys.stdout)
    log.debug(f'aws-snapshot-report {settings.version}')
    if not settings.log_level == 'DEBUG':
        log.debug(f'Changing log level to {settings.log_level}')
    logging.getLogger().setLevel(settings.log_level)

    log.info(f'Writing data to {settings.output_file}')

    csv_field_names = [
        'snapshot_id', 'data_encryption_key_id', 'description', 'encrypted', 'kms_key_id', 'owner_alias', 'owner_id',
        'progress', 'start_time', 'state', 'state_message', 'volume_id', 'volume_size_gb', 'tag_NAME', 'tag_OWNEREMAIL',
        'region'
    ]

    with settings.output_file.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_field_names)
        writer.writeheader()
        for region in get_available_regions():
            ec2 = boto3.resource('ec2', region_name=region)
            try:
                for v in ec2.snapshots.filter(OwnerIds=[settings.owner_id]):
                    writer.writerow(get_snapshot_data(region, v))
            except botocore.exceptions.ClientError:
                log.warning(f'Skipping region {region}')


if __name__ == '__main__':
    main()
