import base64
import io
import json
import random
from PIL import Image
from workflow_apis.api.api_helpers import generate_image_by_prompt_and_image

def prompt_image_to_image(workflow, input_image_data, positive_prompt, sketch):
    prompt = json.loads(workflow)
    
    # Updating prompt to use base64 encoded image
    input_image_base64 = base64.b64encode(input_image_data).decode('utf-8')

    if not sketch:
        prompt["132"]['inputs']['image'] = input_image_base64
        prompt["103"]["inputs"]["seed"] = random.randint(10**14, 10**15 - 1)
        prompt["39"]["inputs"]["text"] = "bged, " + positive_prompt
        prompt["104"]["inputs"]["text"] = positive_prompt
    else:
        prompt["202"]['inputs']['image'] = input_image_base64
        prompt["158"]["inputs"]["seed"] = random.randint(10**14, 10**15 - 1)
        prompt["150"]["inputs"]["text"] = "bged, " + positive_prompt
        prompt["159"]["inputs"]["text"] = positive_prompt

    encoded_images = generate_image_by_prompt_and_image(prompt, input_image_data)

    return encoded_images
