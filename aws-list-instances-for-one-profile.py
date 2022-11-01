import boto3
import botocore.exceptions
import notch

log = notch.make_log('aws_list_instances_for_one_profile')

s = boto3.Session()
log.info(f'Using profile {s.profile_name}')

count = 0

for region in s.get_available_regions('ec2'):
    ec2 = s.resource('ec2', region)
    try:
        for instance in ec2.instances.all():
            log.info(f'{region} / {instance.id}')
            count += 1
    except botocore.exceptions.ClientError as e:
        log.warning(f'Skipping {region}')

log.info(f'Found {count} instances total')
