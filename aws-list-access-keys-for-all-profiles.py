import boto3
import csv
import notch
import sys
import util

log = notch.make_log('aws_list_access_keys_for_all_profiles')


rows = []

for profile_name in util.aws_profiles():
    log.info(f'Checking profile {profile_name}')
    s = boto3.Session(profile_name=profile_name)

    iam_r = s.resource('iam')
    iam_c = s.client('iam')

    for user in iam_r.users.all():
        key_count = 0
        for key in user.access_keys.all():
            key_count += 1
            key_last_used = iam_c.get_access_key_last_used(AccessKeyId=key.id)
            key_last_used_date = key_last_used.get('AccessKeyLastUsed', {}).get('LastUsedDate')
            rows.append({
                'profile_name': profile_name,
                'user_arn': user.arn,
                'user_name': user.user_name,
                'password_last_used': user.password_last_used,
                'access_key_id': key.id,
                'access_key_status': key.status,
                'access_key_last_used': key_last_used_date
            })
        if key_count == 0:
            rows.append({
                'profile_name': profile_name,
                'user_arn': user.arn,
                'user_name': user.user_name,
                'password_last_used': user.password_last_used,
                'access_key_id': None,
                'access_key_status': None,
                'access_key_last_used': None
            })

writer = csv.DictWriter(sys.stdout, fieldnames=rows[0].keys())
writer.writeheader()
writer.writerows(rows)
