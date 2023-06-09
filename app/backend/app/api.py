
import numpy as np
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.workers import add_task_to_queue, start_workers 

logger = logging.getLogger(__name__)


app = FastAPI()


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

_workers_initialized = False


@app.get("/generate-images/{model_name}/{prompt}/{n_images}", response_class=JSONResponse)
async def generate_images(model_name: str, prompt: str, n_images:int):
    """
    Create new tasks for workers and return the future location of images on S3.
    """

    global _workers_initialized

    # first call: initialize workers 
    # note: this takes longer if models is not downloaded yet ->  
    # might be better to download models on the server start or add to docker image 
    if not _workers_initialized:
        start_workers()
        _workers_initialized = True

    # generate random names for the output images
    img_names = [f"{model_name}_{np.random.randint(0, int(1e7)-1)}.jpg" 
                 for _ in range(n_images)]

    # Send tasks to all workers
    for img_name in img_names:
        add_task_to_queue(img_name, model_name, prompt)

    # return future names of images on S3
    return {"status": "ok", 'image_names': img_names}
