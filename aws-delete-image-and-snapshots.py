# Given an AWS EC2 image ID, deregister the image and delete any associated snapshots

import argparse
import boto3
import logging
import os
import sys

log = logging.getLogger(__name__)
if __name__ == '__main__':
    log = logging.getLogger('delete_image_and_snapshot')


def parse_args():
    description = 'Deregister an image and delete any associated snapshots'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('image_id', nargs='+')
    return parser.parse_args()


def deregister_image(image_id):
    image_id = image_id.strip(',')
    ec2 = boto3.resource('ec2')
    image = ec2.Image(image_id)
    snapshots = [ec2.Snapshot(m['Ebs']['SnapshotId']) for m in image.block_device_mappings if 'Ebs' in m]
    log.info(f'Deregistering image {image.id!r}')
    image.deregister()
    for snapshot in snapshots:
        log.info(f'Deleting snapshot {snapshot.id!r}')
        snapshot.delete()


def main():
    log_format = os.getenv('LOG_FORMAT', '%(levelname)s [%(name)s] %(message)s')
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logging.basicConfig(format=log_format, level=log_level, stream=sys.stdout)
    log.debug(f'LOG_FORMAT: {log_format}')
    log.debug(f'LOG_LEVEL: {log_level}')
    args = parse_args()
    log.info(args)
    for image_id in args.image_id:
        deregister_image(image_id)


if __name__ == '__main__':
    main()
