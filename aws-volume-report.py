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
        self.output_file = pathlib.Path(os.getenv('OUTPUT_FILE', '/data/volumes.csv')).resolve()
        self.version = os.getenv('IMAGE_VERSION', 'unknown')


def get_available_regions():
    session = boto3.session.Session()
    return session.get_available_regions('ec2')


def tag_list_to_dict(tag_list):
    if tag_list is None:
        return {}
    return {t.get('Key'): t.get('Value') for t in tag_list}


def get_volume_data(region, volume) -> Dict:
    attachment_count = len(volume.attachments)
    if attachment_count > 0:
        attachment = volume.attachments[0]
    else:
        attachment = {}
    tags = tag_list_to_dict(volume.tags)
    return {
        'volume_id': volume.id,
        'attachment_count': attachment_count,
        'attachment_time': attachment.get('AttachTime'),
        'attachment_device': attachment.get('Device'),
        'attachment_instance_id': attachment.get('InstanceId'),
        'attachment_state': attachment.get('State'),
        'attachment_delete_on_termination': attachment.get('DeleteOnTermination'),
        'availability_zone': volume.availability_zone,
        'create_time': volume.create_time,
        'encrypted': volume.encrypted,
        'fast_restored': volume.fast_restored,
        'iops': volume.iops,
        'kms_key_id': volume.kms_key_id,
        'multi_attach_enabled': volume.multi_attach_enabled,
        'outpost_arn': volume.outpost_arn,
        'size_gb': volume.size,
        'snapshot_id': volume.snapshot_id,
        'state': volume.state,
        'volume_type': volume.volume_type,
        'tag_NAME': tags.get('NAME'),
        'tag_OWNEREMAIL': tags.get('OWNEREMAIL'),
        'region': region
    }


def main():
    settings = Settings()
    logging.basicConfig(format=settings.log_format, level='DEBUG', stream=sys.stdout)
    log.debug(f'aws-volume-report {settings.version}')
    if not settings.log_level == 'DEBUG':
        log.debug(f'Changing log level to {settings.log_level}')
    logging.getLogger().setLevel(settings.log_level)

    log.info(f'Writing data to {settings.output_file}')

    csv_field_names = [
        'volume_id', 'attachment_count', 'attachment_time', 'attachment_device', 'attachment_instance_id',
        'attachment_state', 'attachment_delete_on_termination', 'availability_zone', 'create_time', 'encrypted',
        'fast_restored', 'iops', 'kms_key_id', 'multi_attach_enabled', 'outpost_arn', 'size_gb', 'snapshot_id', 'state',
        'volume_type', 'tag_NAME', 'tag_OWNEREMAIL', 'region'
    ]

    with settings.output_file.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_field_names)
        writer.writeheader()
        for region in get_available_regions():
            ec2 = boto3.resource('ec2', region_name=region)
            try:
                for v in ec2.volumes.all():
                    writer.writerow(get_volume_data(region, v))
            except botocore.exceptions.ClientError:
                log.warning(f'Skipping region {region}')


if __name__ == '__main__':
    main()
