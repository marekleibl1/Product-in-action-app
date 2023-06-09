import os 
import streamlit as st
from PIL import Image

from image_generation import upscale_image
from s3_download import download_from_s3


def contact_us():
    st.markdown('<a href="mailto:jack@interactivepixels.ai">Contact us</a>', unsafe_allow_html=True)

def how_it_works():
    st.markdown("""
        ##### How to use the app
        - Choose a product from the dropdown menu.
        - Based on the product selected, choose an action (situation in which you want to see the product).
        - You can also use 'Custom' and describe the action / situation yourself 
        - Based on the selected product and action a number of images are generated 
        - Then you can select the one you like the most or generate more images
        ---

        ##### How to add a product
        - We spend 10 minutes with your product to capture it from all angles 
        - Create a customized AI model for your product 
        - Then you can start generating images of your product in different situations!
        ---

        ##### This is not just a background replacement
        - Our AI can generate you model in Action: someone holding, wearing or using your product  
        - For example if your product are glasses, we can generate a picture of someone wearing them
        - That's not possible with just background replacements tools 
        ---

        ##### Why not just use few images of the product?
        - A customized model can be created from few pictures of your product, but the quality won't be great
        - With the right way to capture your product we can provide higher quality content
        - In most cases not recognizable from the real photo

        """)


def selection_compoment(text, options, images):
    col1, col2 = st.columns(2)

    with col1:
        selected_option = st.selectbox(text, options)

    with col2:
        img = images[selected_option]
        
        if os.path.exists(img):
            st.image(img, width=80)

    return selected_option
