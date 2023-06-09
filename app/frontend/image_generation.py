
import os
import streamlit as st
from PIL import Image
from urllib.parse import quote
import requests
from io import BytesIO

from streamlit.logger import get_logger

logger = get_logger(__name__)

local_debug = False

try:
    # this sometimes causes problems when deployed on streamlit server
    # for unknown reason 
    import replicate  
except Exception as e:
    logger.warning(f'Error importing replicate -> image upscaling wont work: {e}')


def _get_preferred_server_number():
    params = st.experimental_get_query_params()

    server_num = 0 

    logger.debug(f'url params {params}')
    
    if 'server' in params:
        try:
            server_num = int(params['server'][0])
            logger.info(f'Requested server num {server_num}')
        except Exception as e:
            logger.info(f'Error parsing url pareters {e}')

    if local_debug:
        st.write(f'url params {params}')
        st.write(f'server_num {server_num}')

    return server_num


def _get_gpu_server_url():
    """
    Get url of the gpu server running on VAST. 
    """

    gpu_server_urls = [
        st.secrets.get('SERVER0'),  # usually 24h gpu server with "slow" GPU
        st.secrets.get('SERVER1'),   # usually 2 gpus, 24GB VRAM
        st.secrets.get('SERVER2')    # usually 4 gpus, >= 24GB VRAM 
    ]

    server_num = _get_preferred_server_number()

    server_url =gpu_server_urls[server_num] if gpu_server_urls[server_num] else gpu_server_urls[0]

    if local_debug:
        st.write(f'server url {server_url}')

    return server_url


server_url = _get_gpu_server_url()


def upscale_image(image):
    """
    Generate 2k variant of the given image.
    Using swin model running on Replicate.
    """
    
    tmp_path = 'img/tmp.jpg'
    image.save(tmp_path)
    image_input = open(tmp_path, "rb")

    # os.environ['REPLICATE_API_TOKEN'] = 'b4a9ebda8e5ab70521bb0f51a5abf750910ebf64'
    os.environ['REPLICATE_API_TOKEN'] = st.secrets['REPLICATE_API_TOKEN']
    
    image_url = replicate.run(
        "mv-lab/swin2sr:a01b0512004918ca55d02e554914a9eca63909fa83a29ff0f115c78a7045574f",
        input={"image": image_input}
    )
    
    # Send a request to fetch the image data
    response = requests.get(image_url)

    # Read the image data from the response
    image_data = response.content

    # Create a PIL Image object from the image data
    image = Image.open(BytesIO(image_data))
    return image


def generate_image(model, option, n_images=1, append=False):
    """
    Send request to the GPU server to generate n images and 
    add the image names into session_state.
    """

    model, option = quote(model), quote(option)

    request = f'http://{server_url}/generate-images/{model}/{option}/{n_images}'
    response = requests.get(request)

    image_names = response.json()['image_names']
    if append:
        st.session_state['image_names'].extend(image_names)
    else:
        st.session_state['image_names'] = image_names
    

