

import torch
import logging
from diffusers import StableDiffusionPipeline, EulerAncestralDiscreteScheduler
from lora_diffusion import tune_lora_scale, patch_pipe

logger = logging.getLogger(__name__)


# Frontend name -> backend name
model_names_dict = {
    'Sephora': 'sephora', 
    'Clippers': 'clippers', 
    'Shoe': 'shoe'
}



# --- PUBLIC


def initialize_pipe(gpu_id):
    """
    Initialize base stable diffusion model on the given GPU. 
    """

    model_id = "stabilityai/stable-diffusion-2-1-base"

    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to(f"cuda:{gpu_id}")
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

    return pipe


def load_lora_model(pipe, model_name):
    """
    Switch finetuned lora model. 
    """

    if model_name not in model_names_dict:
        raise ValueError(f'unsupported model name {model_name}')

    file_name = model_names_dict[model_name]
    model_path = f'/workspace/app/backend/models/{file_name}.safetensors'

    patch_pipe(pipe, model_path, patch_text=True, patch_ti=True,patch_unet=True)

    tune_lora_scale(pipe.unet, 1.0 )
    tune_lora_scale(pipe.text_encoder, 1.0)


def generate_image(pipe, prompt=""):
    
    base_prompt = """a detailed advertising realistic photo of <s1><s2> in the center, best quality"""
    negative_prompt = "cheap, distorted, blur, painting, cropped, cartoon, cropped, poor lighting, deformed, duplicate, low quality, lowres, ugly"
    prompt = f"{base_prompt}, {prompt}"

    logger.info(f'Generating image for prompt: {prompt}')
    image = pipe(prompt, num_inference_steps=50, guidance_scale=7, negative_prompt=negative_prompt).images[0]
    return image
