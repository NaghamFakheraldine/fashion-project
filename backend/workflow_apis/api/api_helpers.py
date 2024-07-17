import base64
from workflow_apis.api.websocket_apis import queue_prompt, get_history, get_image
# from workflow_apis.api.api_helpers import upload_image
from workflow_apis.api.websocket_connection import open_websocket_connection
import json, os
from requests_toolbelt import MultipartEncoder
from PIL import Image
import io

def generate_image_by_prompt(prompt, output_path, save_previews=False):
    print("Inside generate_image_by_prompt")
    ws = None
    try:
        ws, server_address, client_id = open_websocket_connection()
        prompt_id = queue_prompt(prompt, client_id, server_address)['prompt_id']
        print("Prompt ID: ", prompt_id)
        track_progress(prompt, ws, prompt_id)
        images = get_images(prompt_id, server_address, save_previews)
        print(f"Number of images retrieved: {len(images)}")
        encoded_images = save_image(images, output_path, save_previews)
        return encoded_images
    except ConnectionResetError as e:
        print(f"Connection was reset by the remote host: {e}")
        return []
    except Exception as e:
        print(f"An error occurred in generate_image_by_prompt: {e}")
        return []
    finally:
        if ws:
            ws.close()

# Send Image as base64
def save_image(images, output_path, save_previews):
    print("Inside save_image")
    encoded_images = []
    for i, image_dict in enumerate(images):
        try:
            # Assuming image_dict has a key 'image_data' with binary image data
            image_data = image_dict.get('image_data')
            if image_data is None:
                print(f"Error: 'image_data' key not found in image {i}")
                continue

            # Save the image and encode in base64
            image = Image.open(io.BytesIO(image_data))
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            encoded_image_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
            encoded_images.append({
                'file_name': image_dict['file_name'],
                'encoded_image_data': encoded_image_data
            })
            print(f"Image processed: {image_dict['file_name']}")
        except Exception as e:
            print(f"Failed to process image {image_dict['file_name']}: {e}")
    return encoded_images


def track_progress(prompt, ws, prompt_id):
    # print('Inside Track Progress')
    node_ids = list(prompt.keys())
    finished_nodes = []

    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'progress':
                data = message['data']
                current_step = data['value']
                print('In K-Sampler -> Step: ', current_step, ' of: ', data['max'])
            if message['type'] == 'execution_cached':
                data = message['data']
                for itm in data['nodes']:
                    if itm not in finished_nodes:
                        finished_nodes.append(itm)
                        print('Progess: ', len(finished_nodes), '/', len(node_ids), ' Tasks done')
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] not in finished_nodes:
                    finished_nodes.append(data['node'])
                    print('Progess: ', len(finished_nodes), '/', len(node_ids), ' Tasks done')

                if data['node'] is None and data['prompt_id'] == prompt_id:
                    print("Execution completed")
                    break  # Execution is done
        else:
            continue
    return

def get_images(prompt_id, server_address, allow_preview=False):
    print('Inside Get Images')
    output_images = []
    history = get_history(prompt_id, server_address).get(prompt_id, {})
    print(f"History for prompt_id {prompt_id}: {history}")

    if not history:
        print("No history found for this prompt_id.")
        return output_images

    for node_id in history.get('outputs', {}):
        node_output = history['outputs'][node_id]
        for image in node_output.get('images', []):
            output_data = {}
            try:
                print(f"Retrieving image: {image['filename']} from {image['subfolder']}")
                image_data = get_image(image['filename'], image['subfolder'], image['type'], server_address)
                output_data['image_data'] = image_data
                output_data['file_name'] = image['filename']
                output_data['type'] = image['type']
                output_images.append(output_data)
                print(f"Retrieved image data for: {image['filename']}")
            except Exception as e:
                print(f"Failed to retrieve image {image['filename']}: {e}")

    return output_images

