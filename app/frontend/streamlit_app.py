
"""
A simple streamlit fronted. Will be most likely replaced with React in the future. 

Debugging locally:
cd app/frontend/
streamlit run
"""

import os
import streamlit as st
from streamlit.logger import get_logger
from PIL import Image

from image_generation import generate_image, upscale_image
from components import how_it_works, contact_us, selection_compoment
from s3_download import download_from_s3

logger = get_logger(__name__)

# max number of image upscalings 
nhires_limit = 2 

img_dir = './app/frontend/img' 

# debugging locally
if not os.path.exists(img_dir):
    img_dir = './img'


# --- products & situations

# sample products 
product_names = ['Sephora', 'Clippers', 'Shoe']
product_images = {name: f'{img_dir}/products/{name}.jpg' for name in product_names}

# actions / situations that go well with each product
action_names_dict = dict(
    Sephora = ('Flowers', 'Beach', 'Minimal', 'Custom'),
    Clippers = ('Beach', 'Flowers', 'Minimal', 'Dogs', 'Fire', 'Custom'), 
    Shoe = ('Fire', 'Beach', 'Flowers',  'Custom'),
)

action_images = lambda product_name: {
    action_name: f'{img_dir}/actions/{product_name}/{action_name}.jpg'
        for action_name in action_names_dict[product_name]}

# a bit of prompt engineering
prompts = dict(
        Flowers = 'eden, luxury cosmetics, aesthetic, colorful, flowers, bees, butterflies, ribbons, ornate',
        Beach = 'on the beach, white stones, sunny, ocean, waves, sea, water, sand', 
        Dogs = 'dog, dogs, cute puppy, good boy, animal product, adorable pet', 
        Fire = 'fire in the background, burning wood, hot, on fire, ignited, hell, glowing, extremely hot, torch, action movie poster', 
        Minimal = 'in the city, industrial design, NYC, New York'
    )

    # prompt  = "vibrant mexican restaurant, taco shop, painted in weathered colors of yellow, red, blue, vintage artworks, retro look, delicious food"
    # prompt  = "design interior living room "

# --- GUI

st.markdown("""
<style>
.big-font {
    font-size:50px !important;
}

// background-image does not work
body {
    background-image: url("https://designimages.appypie.com/appbackground/appbackground-55-graphics-art.jpg");
    background-size: cover;
}

</style>
""", unsafe_allow_html=True)


cols = None

def show_image_when_available(i, img_name):
    """
    Add a generated image when it's available. 
    """

    global cols
        
    # wait until the image is available
    local_img_path = download_from_s3(img_name)

    # first image
    if i == 0:
        st.markdown('---')
        st.markdown("## 🎨 Generated Images")
        if cols is None: 
            cols = st.columns(2)

    if local_img_path:
        # generated image
        cols[i % 2].image(local_img_path) 
        
        # upscale image
        if cols[i % 2].button(':arrow_right: Generate High Resolution', key=f'{img_name}_hires'):
            if st.session_state['nhires'] < nhires_limit:
                hires = upscale_image(Image.open(local_img_path))
                st.image(hires)
                st.session_state['nhires'] += 1
            else:
                st.write('You reached free limit. Contact us to get more high-res images!')
                contact_us()


def wait_and_show_generated_images():
    # if 'image_names' in st.session_state:
    for i, img_name in enumerate(st.session_state['image_names']):
        with st.spinner('Generating image ...'):
            show_image_when_available(i, img_name)


def main():

    n_images = st.secrets.get('N_IMAGES', 2)

    st.image(f"{img_dir}/logo.png") 
    st.image(f"{img_dir}/banner_image.jpg", use_column_width=True) 

    st.markdown('---')

    with st.expander("How it works?"):
        how_it_works()
    
    st.markdown("## :star: Step 1: Select Product ")
    st.write('Select product you want to see in generated images.')

    selected_product = selection_compoment('Selected product', 
        product_names, product_images)

    st.markdown('---')

    # alternative emoji 🚀 :arrow_right:
    st.markdown("## :star:  Step 2: Select Action / Situation ")
    st.write('Choose a scene or action for the selected product. ')

    selected_action = selection_compoment('Selected action', 
        action_names_dict[selected_product], action_images(selected_product))

    if selected_action == "Custom":
        prompt = st.text_area('Prompt', 'Winter, snow, ice')
    else: 
        prompt = prompts[selected_action]

    st.markdown('---')

    st.markdown("## :star: Step 3: Generate Images ")
    st.write('This usually takes 3 - 10s depending on the gpu server.')
        
    if st.button(':arrow_right: Generate'):
        generate_image(selected_product, prompt, n_images)    
        st.session_state['generate_clicked'] = True

    if st.session_state['generate_clicked']:
        wait_and_show_generated_images()
        
        if st.button(':arrow_right: Generate more'):
            generate_image(selected_product, prompt, n_images, append=True)
            st.experimental_rerun()

        st.success('Image generation complete!')
        st.success('''If you would like to see images of your product, 
        let us know and will create a customized model for you!
        
        ''')

        contact_us()
        

if __name__ == '__main__':
    # initialize session vars on the first call 
    if 'generate_clicked' not in st.session_state:
        st.session_state['generate_clicked'] = False 
        st.session_state['images_generated'] = False
        st.session_state['nhires'] = 0

    main()

        