import boto3

from typing import Iterator

def aws_profiles() -> Iterator[str]:
    """Yield all profile names that can be found in the current config file."""
    s = boto3.Session()
    yield from s.available_profiles

def tag_list_to_dict(tags: list[dict]) -> dict:
    """Convert a list of AWS resource tags to a plain dict."""
    if tags is None:
        return {}
    return {tag.get('Key'): tag.get('Value') for tag in tags}
