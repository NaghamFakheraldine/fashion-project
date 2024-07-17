from workflow_apis.api.api_helpers import generate_image_by_prompt
import json
import random

def prompt_to_image(workflow, positive_prompt):
    try:
        print("Inside prompt_to_image")
        prompt = json.loads(workflow)
        id_to_class_type = {id: details['class_type'] for id, details in prompt.items()}
        k_sampler = [key for key, value in id_to_class_type.items() if value in ['KSampler', 'KSamplerAdvanced']]
        prompt["103"]["inputs"]["seed"] = random.randint(10**14, 10**15 - 1)

        # Fill in text inputs for nodes 39 and 104
        prompt["39"]["inputs"]["text"] = "bged, " + positive_prompt
        prompt["104"]["inputs"]["text"] = positive_prompt

        print("Heading to generate_image_by_prompt")
        image_paths = generate_image_by_prompt(prompt)
        print("image paths: " + str(image_paths))
        return image_paths
    except Exception as e:
        print(f"Error in prompt_to_image: {e}")
        return []
