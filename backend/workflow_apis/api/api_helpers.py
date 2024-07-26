import base64
import json
from PIL import Image
import io, boto3
from workflow_apis.api.websocket_apis import queue_prompt, upload_image, get_history, get_image
from workflow_apis.api.websocket_connection import open_websocket_connection
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

BUCKET_NAME = 'image-flask-project'
FOLDER_NAME = 'HistoryData/'


def generate_3D_from_2D(workflow, input_image_data):
    try:
        ws, server_address, client_id = open_websocket_connection()
        prompt = json.loads(workflow)
        
        # Updating prompt to use base64 encoded image
        input_image_base64 = base64.b64encode(input_image_data).decode('utf-8')

        upload_image(input_image_base64, 'input_image.png', server_address)
        print('Done with upload Image')

        prompt_response = queue_prompt(prompt, client_id, server_address)
        prompt_id = prompt_response.get('prompt_id')
        if not prompt_id:
            raise ValueError("Failed to get prompt_id from queue_prompt response")

        print('Done with prompt_response')

        track_progress(prompt, ws, prompt_id)
        print('Done with track_progress')

        # Get the generated video
        video = get_video(prompt_id, server_address)
        print('Done with get_video')

        if video:
            upload_to_s3(video, 'generated_video.mp4')
            print('Done with upload_to_s3 test')

        print('video: ' + str(video))
        return base64.b64encode(video).decode('utf-8') if video else None
    except Exception as e:
        print(f"Error in generate_3D_from_2D: {e}")
        return None
    finally:
        if ws:
            ws.close()

def generate_image_by_prompt_and_image(prompt, input_image_bytes):
    ws = None
    try:
        ws, server_address, client_id = open_websocket_connection()

        upload_image(input_image_bytes, 'input_image.png', server_address)

        prompt_response = queue_prompt(prompt, client_id, server_address)
        prompt_id = prompt_response.get('prompt_id')
        if not prompt_id:
            raise ValueError("Failed to get prompt_id from queue_prompt response")

        track_progress(prompt, ws, prompt_id)
        images = get_images(prompt_id, server_address)

        encoded_images = [{'file_name': img['file_name'], 'encoded_image_data': base64.b64encode(img['image_data']).decode('utf-8')} for img in images]
        
        # Upload images to S3
        for img in images:
            upload_to_s3(img['image_data'], img['file_name'])

        return encoded_images
    finally:
        if ws:
            ws.close()

def generate_image_by_prompt(prompt):
    print("Inside generate_image_by_prompt")
    ws = None
    try:
        ws, server_address, client_id = open_websocket_connection()
        prompt_id = queue_prompt(prompt, client_id, server_address)['prompt_id']
        print("Prompt ID: ", prompt_id)
        track_progress(prompt, ws, prompt_id)
        images = get_images(prompt_id, server_address)
        print(f"Number of images retrieved: {len(images)}")
        encoded_images = save_image(images)
        
        # Upload images to S3
        for img in images:
            upload_to_s3(img['image_data'], img['file_name'])

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

def save_image(images):
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
    output_images = []
    history = get_history(prompt_id, server_address).get(prompt_id, {})

    if not history:
        print("No history found for this prompt_id.")
        return output_images

    for node_id in history.get('outputs', {}):
        node_output = history['outputs'][node_id]
        for image in node_output.get('images', []):
            output_data = {}
            try:
                image_data = get_image(image['filename'], image['subfolder'], image['type'], server_address)
                output_data['image_data'] = image_data
                output_data['file_name'] = image['filename']
                output_data['type'] = image['type']
                output_images.append(output_data)
            except Exception as e:
                print(f"Failed to retrieve image {image['filename']}: {e}")
    return output_images


def upload_to_s3(image_data, file_name):
    try:
        s3_client = boto3.client('s3')
        s3_key = f"{FOLDER_NAME}{file_name}"
        s3_client.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=image_data, ContentType='image/png')
        print(f"Successfully uploaded {file_name} to S3 in folder {FOLDER_NAME}.")
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Credentials error while uploading {file_name} to S3: {e}")
    except Exception as e:
        print(f"Failed to upload {file_name} to S3: {e}")


def get_video(prompt_id, server_address):
    output_video = None
    history = get_history(prompt_id, server_address).get(prompt_id, {})

    if not history:
        print("No history found for this prompt_id.")
        return output_video

    for node_id in history.get('outputs', {}):
        node_output = history['outputs'][node_id]
        if 'video' in node_output:
            try:
                video_data = get_image(node_output['video']['filename'], node_output['video']['subfolder'], node_output['video']['type'], server_address)
                output_video = video_data
                print(f"Video data retrieved: {len(video_data)} bytes")
            except Exception as e:
                print(f"Failed to retrieve video {node_output['video']['filename']}: {e}")
            break

    return output_video

