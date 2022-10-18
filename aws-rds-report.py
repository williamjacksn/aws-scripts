import boto3
import botocore.exceptions
import notch

log = notch.make_log('aws_rds_owners')

with open('rds.csv', 'w') as f:
    f.write('profile,region,arn,db_instance_identifier,engine,engine_version,owner_email\n')
    profiles = boto3.Session().available_profiles
    for i, profile in enumerate(profiles, start=1):
        log.info(f'Checking {profile} ({i} of {len(profiles)})')
        s = boto3.Session(profile_name=profile)
        for region in s.get_available_regions('rds'):
            log.info(f'Checking {region}')
            rds = s.client('rds', region_name=region)
            try:
                dbs = rds.describe_db_instances()
                for db in dbs.get('DBInstances'):
                    arn = db.get('DBInstanceArn')
                    db_instance_identifier = db.get('DBInstanceIdentifier')
                    engine = db.get('Engine')
                    engine_version = db.get('EngineVersion')
                    tags = db.get('TagList', [])
                    owner = ''
                    for tag in tags:
                        if tag.get('Key') == 'OWNEREMAIL':
                            owner = tag.get('Value')
                    f.write(f'{profile},{region},{arn},{db_instance_identifier},{engine},{engine_version},{owner}\n')
            except botocore.exceptions.ClientError as e:
                log.debug(e)
