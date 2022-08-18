import boto3
import botocore.exceptions
import notch

log = notch.make_log('aws_rds_owners')

for profile_name in boto3.Session().available_profiles:
    log.info(f'Checking {profile_name}')
    s = boto3.Session(profile_name=profile_name)
    for region_name in s.get_available_regions('rds'):
        log.info(f'Checking {region_name}')
        rds = s.client('rds', region_name=region_name)
        try:
            dbs = rds.describe_db_instances()
            for db in dbs.get('DBInstances'):
                db_instance_identifier = db.get('DBInstanceIdentifier')
                tags = db.get('TagList', [])
                owner_email = ''
                for tag in tags:
                    if tag.get('Key') == 'OWNEREMAIL':
                        owner_email = tag.get('Value')
                log.info(f'{profile_name} / {region_name} / {db_instance_identifier} / {owner_email}')
        except botocore.exceptions.ClientError as e:
            log.debug(e)
