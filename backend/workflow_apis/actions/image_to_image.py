from workflow_apis.api.websocket_apis import generate_image_by_prompt_and_image
import random, json

def prompt_image_to_image(workflow, input_path, positve_prompt, save_previews=False):
  prompt = json.loads(workflow)
  id_to_class_type = {id: details['class_type'] for id, details in prompt.items()}
  k_sampler = [key for key, value in id_to_class_type.items() if value == 'KSampler' or value == 'KSamplerAdvanced'][0]

  prompt["103"]["inputs"]["seed"] = random.randint(10**14, 10**15 - 1)

  prompt["39"]["inputs"]["text"] = "bged, " + positve_prompt

  image_loader = [key for key, value in id_to_class_type.items() if value == 'LoadImage'][0]
  filename = input_path.split('/')[-1]
  prompt.get(image_loader)['inputs']['image'] = filename

  generate_image_by_prompt_and_image(prompt, './output', input_path, filename, save_previews)


  