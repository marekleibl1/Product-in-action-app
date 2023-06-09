

import os
import time
import boto3
import streamlit as st
from streamlit.logger import get_logger
from botocore.config import Config

logger = get_logger(__name__)

bucket_name = 'finetuningsd'


def _create_s3_client():

    secrets =  st.secrets

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

def download_from_s3(img_name):
    
    tmp_dir ='tmp/generated_images'
    os.makedirs(tmp_dir, exist_ok=True)

    local_img_path = os.path.join(tmp_dir, img_name) 

    s3_file_name = 'generated/' + img_name

    logger.info(f"""
    Getting image from s3 ... 
    s3_file_name {s3_file_name} bucket_name {bucket_name} 
    """)

    max_attempts = 100
    wait_s = 0.1

    for _ in range(max_attempts):
        try:
            _s3_client.download_file(bucket_name, s3_file_name, local_img_path)
            logger.info('Image downloaded ')
            return local_img_path
        except:
            time.sleep(wait_s)

    logger.info('Image not downloaded ')
    return None



def check_url(url):
    """Check if the URL exists."""
    try:
        response = request.head(url)
        return response.status_code == 200
    except Exception as e:
        print(f"Error encountered: {e}")
        return False
        

def wait_for_image(url, max_wait_time=20, check_interval=0.1):
    """Wait for the image to be available at the URL."""
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        if check_url(url):
            return True
        time.sleep(check_interval)  # wait before checking again
    return False


def get_link_from_s3(s3_file_name):
    """
    This should be faster compared to downloading images first. 

    This way we transfer the image directly to the client.  
    """
    from streamlit.logger import get_logger
    logger = get_logger(__name__)

    s3_file_name = 'generated/' + s3_file_name

    logger.info(f"""
    Getting image from s3 ... 
    s3_file_name {s3_file_name} bucket_name {bucket_name} 
    """)

    expiration= 9999999 # 3600
    url = _s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': s3_file_name},
                                                    ExpiresIn=expiration)

    logger.info(f'Generated url: {url} ')
    return url

