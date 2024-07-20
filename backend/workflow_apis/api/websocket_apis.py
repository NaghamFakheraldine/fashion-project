import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
import os
import random
from requests_toolbelt import MultipartEncoder
from PIL import Image
import io
import boto3
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def queue_prompt(prompt, client_id, server_address):
    print('Inside queue_prompt')
    
    # Ensure prompt is a dictionary and serializable
    if not isinstance(prompt, dict):
        raise TypeError("Prompt must be a dictionary")
    
    p = {"prompt": prompt, "client_id": client_id}
    headers = {'Content-Type': 'application/json'}
    
    # Convert to JSON bytes
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data, headers=headers)
    
    try:
        response = urllib.request.urlopen(req)
        response_data = response.read()
        print(f"Response: {response_data}")
        return json.loads(response_data)
    except Exception as e:
        print(f"Error queuing prompt: {e}")
        raise

def get_history(prompt_id, server_address):
    print(f'Get History for prompt_id {prompt_id}')
    with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())

def get_image(filename, subfolder, folder_type, server_address):
    print(f'Inside Get Image for {filename} in {subfolder}')
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
        return response.read()

def upload_image(input_image_bytes, name, server_address, image_type="input", overwrite=False):
    print('Inside upload_image')
    multipart_data = MultipartEncoder(
        fields={
            'image': (name, input_image_bytes, 'image/png'),
            'type': image_type,
            'overwrite': str(overwrite).lower()
        }
    )

    headers = {'Content-Type': multipart_data.content_type}
    request = urllib.request.Request(f"http://{server_address}/upload/image", data=multipart_data.to_string(), headers=headers)
    with urllib.request.urlopen(request) as response:
        return response.read()
