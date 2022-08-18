import boto3

for p in sorted(boto3.Session().available_profiles):
    print(p)
