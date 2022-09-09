import boto3
import notch

log = notch.make_log('aws-describe-security-group-rules')

count = 0

ec2 = boto3.client('ec2', 'us-west-2')
sgr_paginator = ec2.get_paginator('describe_security_group_rules')
for page in sgr_paginator.paginate():
    rules = page.get('SecurityGroupRules')
    for rule in rules:
        count += 1
        rule_id = rule.get('SecurityGroupRuleId')
        log.info(f'{count} Found a security group rule: {rule_id}')
