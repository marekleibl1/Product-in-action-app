import os
import torch
from multiprocessing import Process, Queue
import logging 

from app.s3_upload import upload_to_s3
from app.img_generator import generate_image, initialize_pipe, load_lora_model

logger = logging.getLogger(__name__)


# where the generated images are stored (before uploading to S3)
_local_export_dir = '/workspace/generated_images'

# tasks for workers 
_task_queue = Queue()

# process for each gpu worker
_processes = []


def _worker(task_queue: Queue, gpu_id: int):
    """
    The main worker loop: generate an image or wait for new tasks. 
    """

    # put stable diffusion on the given gpu
    pipe = initialize_pipe(gpu_id)

    # current lora model
    current_model = None

    while True:
        # Get new task from queue
        logger.info(f'Worker {gpu_id}: waiting ... ')
        task = task_queue.get()  
        logger.info(f'Worker {gpu_id}: received new task: {task}')

        img_name, model_name, prompt = task

        # load new lora model if needed
        if model_name != current_model:
            current_model = model_name
            logger.info(f'Worker {gpu_id}: Loading model...')
            load_lora_model(pipe, current_model)
            logger.info(f'Worker {gpu_id}: Loading model - done')

        # generate image
        logger.info(f'Worker {gpu_id}: Generating image for promt: {prompt}')
        image = generate_image(pipe, prompt)

        # save the image locally
        # note: might be faster to upload directly to S3? 
        os.makedirs(_local_export_dir, exist_ok=True)
        local_img_path = os.path.join(_local_export_dir, img_name)
        image.save(local_img_path)
        
        # upload to s3
        try:
            logger.info(f'Worker {gpu_id}: Uploading {img_name} to s3 ...')
            upload_to_s3(local_img_path, img_name)
            logger.info(f'Worker {gpu_id}: Uploading {img_name} to s3 - done')
        except Exception as e:
            logger.warning(f'Error uploading to s3: {e}')


# --- PUBLIC


def start_workers():
    """
    Initialize and start worker for each gpu. 
    """

    # Detect available GPUs
    num_gpus = torch.cuda.device_count()
    
    logger.info(f'Starting workers (num_gpus: {num_gpus})')

    # Create a worker process for each GPU
    for gpu_id in range(num_gpus):
        logger.info(f'Creating worker {gpu_id}')
        process = Process(target=_worker, args=(_task_queue, gpu_id))
        _processes.append(process)
        
    for process in _processes:
        process.start()

    return num_gpus


def add_task_to_queue(img_name: str, model_name: str, prompt: str):
    """
    Add task to the queue: 
     - img_name ... future name on S3
     - model_name ... name of the finetuned model = product name
     - prompt ... prompt for stable diffusion 
    """
    task = (img_name, model_name, prompt)
    _task_queue.put(task)


