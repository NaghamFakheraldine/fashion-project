import io
from PIL import Image
from workflow_apis.api.api_helpers import generate_image_by_prompt_and_image
import random, json

def prompt_image_to_image(workflow, input_image_data, positive_prompt):
    print('Inside Prompt Image to Image')
    prompt = json.loads(workflow)
    print('Prompt: ', prompt)
    id_to_class_type = {id: details['class_type'] for id, details in prompt.items()}
    k_sampler = [key for key, value in id_to_class_type.items() if value in ['KSampler', 'KSamplerAdvanced']][0]

    prompt["103"]["inputs"]["seed"] = random.randint(10**14, 10**15 - 1)

    prompt["39"]["inputs"]["text"] = "bged, " + positive_prompt
    prompt["104"]["inputs"]["text"] = positive_prompt

    image_loader = [key for key, value in id_to_class_type.items() if value == 'LoadImage'][0]
    
    # Save the input image data as a temporary file
    input_image_path = './temp_input_image.png'
    with open(input_image_path, 'wb') as f:
        f.write(input_image_data)
    
    # Pass the image path to the workflow
    prompt[image_loader]['inputs']['image'] = input_image_path

    encoded_images = generate_image_by_prompt_and_image(prompt, input_image_data, input_image_path)
    return encoded_images
