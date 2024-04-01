from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler, AutoencoderKL
import torch
import random
from PIL import Image
import joblib

class imageGenerator:
    def __init__(self, initial_prompt, num_steps = 30, prompt_guidance=9, dimensions=(256,256)):
        self.initial_prompt = initial_prompt
        self.num_steps = num_steps
        self.prompt_guidance = prompt_guidance
        self.dimensions = dimensions
    
    def get_pipe(self):
        self.pipe = DiffusionPipeline.from_pretrained(
            "prompthero/openjourney",
            torch_dtype=torch.float32
        )
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse", torch_dtype=torch.float32)
        return self.pipe
    
    def callImageGenerator(self):
        self.pipe = self.get_pipe()
        prompt = f'(Anime art of {self.initial_prompt}:1.2), masterpiece, 4k, best quality'
        num_variations = 1
        random_seeds = [random.randint(0, 65000) for _ in range(num_variations)]

        images = self.pipe(prompt= num_variations * [prompt],
                    num_inference_steps=self.num_steps,
                    guidance_scale=self.prompt_guidance,
                    height = self.dimensions[0],
                    width = self.dimensions[1],
                    generator = [torch.Generator().manual_seed(i) for i in random_seeds]
                    ).images
        joblib.dump(images[0], "./temp/image_temp.gz")
        return joblib.load("./temp/image_temp.gz")