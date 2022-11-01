import boto3
import botocore.exceptions
import csv
import notch
import os
import util

log = notch.make_log('aws_report_image_snapshots')

images_fieldnames = [
    'image_id', 'region', 'name', 'description', 'creation_date', 'aws_account_number', 'platform', 'tag:NAME',
    'tag:OWNEREMAIL', 'snapshot_id'
]
images_csv = open('images.csv', 'w')
images_writer = csv.DictWriter(images_csv, fieldnames=images_fieldnames)
images_writer.writeheader()

snapshots_fieldnames = ['snapshot_id']
snapshots_csv = open('snapshots.csv', 'w')
snapshots_writer = csv.DictWriter(snapshots_csv, fieldnames=snapshots_fieldnames)
snapshots_writer.writeheader()

included_profiles = os.getenv('INCLUDED_PROFILES', '').split()

if not included_profiles:
    log.warning('Please specify a space-delimited list of profiles in the environment variable INCLUDED_PROFILES')

for profile_name in util.aws_profiles():
    if profile_name not in included_profiles:
        continue

    log.info(f'Checking profile {profile_name}')
    s = boto3.Session(profile_name=profile_name)
    for region in s.get_available_regions('ec2'):
        ec2 = s.resource('ec2', region)
        try:
            for image in ec2.images.filter(Owners=['self']):
                tags = util.tag_list_to_dict(image.tags)
                row = {
                    'image_id': image.id,
                    'region': region,
                    'name': image.name,
                    'description': image.description,
                    'creation_date': image.creation_date,
                    'aws_account_number': image.owner_id,
                    'platform': image.platform,
                    'tag:NAME': tags.get('NAME'),
                    'tag:OWNEREMAIL': tags.get('OWNEREMAIL'),
                    'snapshot_id': None
                }
                for m in image.block_device_mappings:
                    if 'Ebs' in m:
                        row.update({
                            'snapshot_id': m.get('Ebs').get('SnapshotId')
                        })
                images_writer.writerow(row)
        except botocore.exceptions.ClientError as e:
            log.warning(f'Skipping {region}')
