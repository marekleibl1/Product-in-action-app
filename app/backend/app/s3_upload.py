
"""
To download all generated images:
aws s3 cp s3://finetuningsd/generated ~/generated/ --recursive
"""

import logging
import boto3
from botocore.config import Config
from dotenv import dotenv_values

logger = logging.getLogger(__name__)


bucket_name = 'finetuningsd'

def _get_aws_keys():
    env_path = "/workspace/app/backend/.env"
    secrets = dotenv_values(env_path)

    if 'AWS_ACCESS_KEY' not in secrets:
        raise ValueError(f'Put your AWS keys into {env_path}')

    return secrets


def _create_s3_client():

    secrets = _get_aws_keys()

    aws_access_key_id = secrets['AWS_ACCESS_KEY']
    aws_secret_access_key = secrets['AWS_SECRET_KEY']
    region_name = secrets['REGION_NAME']


    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    
    # Note that acceleration needs to be enabled on the bucket
    s3 = session.client('s3', config=Config(s3={'use_accelerate_endpoint': True}))

    return s3


_s3_client = _create_s3_client()


# --- PUBLIC 


def upload_to_s3(local_file_path, s3_file_name):
    s3_file_name = 'generated/' + s3_file_name
    _s3_client.upload_file(local_file_path, bucket_name, s3_file_name)


