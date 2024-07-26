import boto3
import base64
import uuid
from flask import Flask, redirect, url_for, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import math

import requests
from workflow_apis.api.api_helpers import generate_3D_from_2D
from workflow_apis.actions.prompt_to_image import prompt_to_image
from workflow_apis.actions.image_to_image import prompt_image_to_image
from workflow_apis.api.load_workflow import load_workflow
import os

ALLOWED_EXTENSIONS = {'png', 'jpeg'}
fclip_api_url = "http://34.240.213.100:5004/search"
T2I_WORKFLOW_PATH = 'workflow_apis/workflows/T2I_workflow.json'
R2I_WORKFLOW_PATH = 'workflow_apis/workflows/Ref2ImageAPI.json'
S2I_WORKFLOW_PATH = 'workflow_apis/workflows/S2I_workflow.json'
I23D_WORKFLOW_PATH = 'workflow_apis/workflows/I23D_workflow.json'
LA2I_WORKFLOW_PATH = 'workflow_apis/workflows/LA2I_workflow.json'
IN2I_WORKFLOW_PATH = 'workflow_apis/workflows/IN2I_workflow.json'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy()

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255))
    filename = db.Column(db.String(255))
    bucket = db.Column(db.String(255))
    region = db.Column(db.String(255))

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config["IMAGE_BUCKET"] = "image-flask-project"

    CORS(app)
    db.init_app(app)

    @app.route("/api/save-image", methods=["POST"])
    def save_image():
        try:
            bucket_name = "image-flask-project"
            data = request.get_json()
            
            image_data = data["imageData"]
            uploaded_filename = data.get('originalFilename', 'image.png')

            if not allowed_file(uploaded_filename):
                return jsonify({"error": "File type not allowed"}), 400

            extension = uploaded_filename.rsplit('.', 1)[1].lower()
            new_filename = f"{uuid.uuid4().hex}.{extension}"

            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]  

            image_data = base64.b64decode(image_data)

            s3_client = boto3.client('s3')
            response = s3_client.put_object(
                Body=image_data,
                Bucket=app.config["IMAGE_BUCKET"],
                Key=new_filename,
                ContentType=f"image/{extension}"
            )

            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                file = File(
                    original_filename=uploaded_filename,
                    filename=new_filename,
                    bucket=bucket_name,
                    region="eu-north-1"
                )
                db.session.add(file)
                db.session.commit()
                return jsonify({'message': 'image saved successfully'}), 200

        except Exception as e:
            print(f"Error uploading image: {e}")
            return jsonify({"error": f"Error uploading image: {str(e)}"}), 500

    @app.route("/api/get-images", methods=["GET"])
    def get_images():
        folder = request.args.get('folder', '') 

        if not folder:
            return jsonify({"error": "Folder parameter is required"}), 400

        try:
            s3_client = boto3.client("s3")
            response = s3_client.list_objects_v2(Bucket=app.config["IMAGE_BUCKET"], Prefix=folder)

            images = []
            for content in response.get("Contents", []):
                if not content['Key'].endswith('/'):
                    image_url = f"https://{app.config['IMAGE_BUCKET']}.s3.amazonaws.com/{content['Key']}"
                    images.append({"url": image_url})

            return jsonify({"images": images})

        except Exception as e:
            print(f"Error getting images from S3: {e}")
            return jsonify({"error": "Failed to retrieve images"}), 500


    @app.route("/api/update-image", methods=["POST"])
    def update_image():
        try:
            data = request.get_json()
            image_data = data["imageData"]
            image_id = data.get("id")
            s3_client = boto3.client("s3")
            s3_client.put_object(
                Body=image_data,
                Bucket=app.config["IMAGE_BUCKET"],
                Key=image_id
            )
            return jsonify({"message": "Image updated successfully"}), 200

        except Exception as e:
            print(f"Error updating image: {e}")
            return jsonify({"error": "Failed to update image"}), 500

    @app.route("/api/delete-image/<image_id>", methods=["DELETE"])
    def delete_image(image_id):
        try:
            image = File.query.filter_by(id=image_id).first()

            if not image:
                return jsonify({"error": "Image not found"}), 404

            s3_client = boto3.client("s3")
            s3_client.delete_object(Bucket=app.config["IMAGE_BUCKET"], Key=image.filename)

            db.session.delete(image)
            db.session.commit()

            return jsonify({"message": "Image deleted successfully"}), 200

        except Exception as e:
            print(f"Error deleting image: {e}")
            return jsonify({"error": "Failed to delete image"}), 500
        

    @app.route("/api/get-paginated-images", methods=["GET"])
    def get_paginated_images():
        try:
            page = int(request.args.get("page", 0))  
            images_per_page = int(request.args.get("imagesPerPage", 4))

            s3_client = boto3.client("s3")
            response = s3_client.list_objects_v2(Bucket=app.config["IMAGE_BUCKET"])

            images = []
            for content in response.get("Contents", []):
                image_url = f"https://{app.config['IMAGE_BUCKET']}.s3.amazonaws.com/{content['Key']}"
                images.append({"url": image_url})

            start_index = page * images_per_page
            end_index = min(start_index + images_per_page, len(images))
            paginated_images = images[start_index:end_index]

            return jsonify({"images": paginated_images, "totalPages": math.ceil(len(images) / images_per_page)})

        except Exception as e:
            print(f"Error getting images from S3: {e}")
            return jsonify({"error": "Failed to retrieve images"}), 500
    
    @app.route("/api/generate-image-from-prompt", methods=["POST"])
    def generate_image_from_prompt():
        try:
            if request.content_type != 'application/json':
                return jsonify({"error": "Content-Type must be application/json"}), 415

            data = request.get_json()
            print("generate_image_from_prompt Data: " + str(data))
            positive_prompt = data.get("positive_prompt", "")

            if not positive_prompt:
                return jsonify({"error": "positive_prompt is required"}), 400

            workflow_json = load_workflow(T2I_WORKFLOW_PATH)
            print("Workflow loaded successfully!")
            if workflow_json is None:
                return jsonify({"error": "Failed to load workflow"}), 500

            encoded_images = prompt_to_image(workflow_json, positive_prompt)
            if not encoded_images:
                return jsonify({"error": "Image generation failed"}), 500

            return jsonify({"message": "Image generation successful", "images": encoded_images})

        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return jsonify({"error": "Failed to generate image"}), 500

    @app.route("/api/generate-image-from-reference", methods=["POST"])
    def generate_image_from_reference():
        try:
            data = request.get_json()
            if not data or 'image' not in data or 'positive_prompt' not in data:
                return jsonify({'error': 'Invalid input'}), 400

            image_base64 = data['image']
            prompt_text = data['positive_prompt']

            # Decode the base64 image
            try:
                input_image_data = base64.b64decode(image_base64)
            except Exception as e:
                return jsonify({'error': f'Failed to decode image: {e}'}), 500

            workflow = load_workflow(R2I_WORKFLOW_PATH)
            if workflow is None:
                return jsonify({"error": "Failed to load workflow"}), 500

            encoded_images = prompt_image_to_image(workflow, input_image_data, prompt_text, sketch = False)
            if not encoded_images:
                return jsonify({'error': 'Failed to generate image'}), 500

            return jsonify({'images': encoded_images}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to generate image: {e}"}), 500

    @app.route("/api/generate-image-from-sketch", methods=["POST"])
    def generate_image_from_sketch():
        try:
            data = request.get_json()
            if not data or 'image' not in data or 'positive_prompt' not in data:
                return jsonify({'error': 'Invalid input'}), 400

            image_base64 = data['image']
            prompt_text = data['positive_prompt']

            # Decode the base64 image
            try:
                input_image_data = base64.b64decode(image_base64)
            except Exception as e:
                return jsonify({'error': f'Failed to decode image: {e}'}), 500

            workflow = load_workflow(S2I_WORKFLOW_PATH)
            if workflow is None:
                return jsonify({"error": "Failed to load workflow"}), 500

            encoded_images = prompt_image_to_image(workflow, input_image_data, prompt_text, sketch = True)
            if not encoded_images:
                return jsonify({'error': 'Failed to generate image'}), 500

            return jsonify({'images': encoded_images}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to generate image: {e}"}), 500
        

    @app.route("/api/generate-image-from-lineart", methods=["POST"])
    def generate_image_from_lineart():
        try:
            data = request.get_json()
            if not data or 'image' not in data or 'positive_prompt' not in data:
                return jsonify({'error': 'Invalid input'}), 400

            image_base64 = data['image']
            prompt_text = data['positive_prompt']

            # Decode the base64 image
            try:
                input_image_data = base64.b64decode(image_base64)
            except Exception as e:
                return jsonify({'error': f'Failed to decode image: {e}'}), 500

            workflow = load_workflow(LA2I_WORKFLOW_PATH)
            if workflow is None:
                return jsonify({"error": "Failed to load workflow"}), 500

            encoded_images = prompt_image_to_image(workflow, input_image_data, prompt_text, sketch = True)
            if not encoded_images:
                return jsonify({'error': 'Failed to generate image'}), 500

            return jsonify({'images': encoded_images}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to generate image: {e}"}), 500
        
    @app.route("/api/generate-image-from-inpainting", methods=["POST"])
    def generate_image_from_inpainting():
        try:
            data = request.get_json()
            if not data or 'image' not in data or 'positive_prompt' not in data:
                return jsonify({'error': 'Invalid input'}), 400

            image_base64 = data['image']
            prompt_text = data['positive_prompt']

            # Decode the base64 image
            try:
                input_image_data = base64.b64decode(image_base64)
            except Exception as e:
                return jsonify({'error': f'Failed to decode image: {e}'}), 500

            workflow = load_workflow(IN2I_WORKFLOW_PATH)
            if workflow is None:
                return jsonify({"error": "Failed to load workflow"}), 500

            encoded_images = prompt_image_to_image(workflow, input_image_data, prompt_text, sketch = True)
            if not encoded_images:
                return jsonify({'error': 'Failed to generate image'}), 500

            return jsonify({'images': encoded_images}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to generate image: {e}"}), 500
        
    # @app.route("/api/generate-3D-from-2D", methods=["POST"])
    # def generate_2d_from_3d():
    #     try:
    #         data = request.get_json()
    #         if 'image' not in data:
    #             return jsonify({'error': 'Invalid input'}), 400

    #         image_base64 = data['image']

    #         # Decode the base64 image
    #         try:
    #             input_image_data = base64.b64decode(image_base64)
    #         except Exception as e:
    #             return jsonify({'error': f'Failed to decode image: {e}'}), 500

    #         workflow = load_workflow(I23D_WORKFLOW_PATH)
    #         if workflow is None:
    #             return jsonify({"error": "Failed to load workflow"}), 500

    #         video = generate_3D_from_2D(workflow, input_image_data)
    #         if not video:
    #             return jsonify({'error': 'Failed to generate video'}), 500

    #         return jsonify({'video': video}), 200
    #     except Exception as e:
    #         return jsonify({"error": f"Failed to generate video: {e}"}), 500


    @app.route('/api/get-sorted-indices', methods=['POST'])
    def get_sorted_indices():
        query = request.json.get('query')
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400
        
        try:
            print('Sending Request')
            response = requests.post(fclip_api_url, json={"query": query}, timeout=60)
            response.raise_for_status()
            print('Response Received')
            data = response.json()
            print('Data Extracted')

            sorted_indices = data.get('sorted_indices')
            if sorted_indices is None:
                return jsonify({"error": "sorted_indices not found in the API response"}), 400

            return jsonify({"sorted_indices": sorted_indices})

        except requests.exceptions.RequestException as e:
            return jsonify({"error": str(e)}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
