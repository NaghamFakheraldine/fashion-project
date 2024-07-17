import boto3
import base64
import uuid
from flask import Flask, redirect, url_for, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import math
from workflow_apis.actions.prompt_to_image import prompt_to_image
from workflow_apis.api.load_workflow import load_workflow
import os

ALLOWED_EXTENSIONS = {'png', 'jpeg'}
T2I_WORKFLOW_PATH = 'workflow_apis/workflows/T2I_workflow.json'

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

            # print("Received data:", data)
            
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
        try:
            s3_client = boto3.client("s3")
            response = s3_client.list_objects_v2(Bucket=app.config["IMAGE_BUCKET"])

            images = []
            for content in response.get("Contents", []):
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

            # print("Images:", images)  # Inspect the images data here
            return jsonify({"images": paginated_images, "totalPages": math.ceil(len(images) / images_per_page)})

        except Exception as e:
            print(f"Error getting images from S3: {e}")
            return jsonify({"error": "Failed to retrieve images"}), 500
    
    # Workflows
    
    # WORKFLOW_PATH = 'workflow_apis/workflows/T2I_workflow.json'

    # @app.route("/api/generate-image-from-prompt", methods=["POST"])
    # def generate_image_from_prompt():
    #     try:
    #         # Ensure the request content type is JSON
    #         if request.content_type != 'application/json':
    #             return jsonify({"error": "Content-Type must be application/json"}), 415

    #         data = request.get_json()
    #         print("generate_image_from_prompt Data: " + str(data))
    #         positive_prompt = data.get("positive_prompt", "")
    #         save_previews = data.get("save_previews", False)

    #         if not positive_prompt:
    #             return jsonify({"error": "positive_prompt is required"}), 400

    #         workflow_json = load_workflow(WORKFLOW_PATH)
    #         print("Workflow loaded successfully!")
    #         if workflow_json is None:
    #             return jsonify({"error": "Failed to load workflow"}), 500

    #         image_paths = prompt_to_image(workflow_json, positive_prompt, save_previews)
    #         if not image_paths:
    #             return jsonify({"error": "Image generation failed"}), 500

    #         print('image_paths: ' + str(image_paths))
    #         return jsonify({"message": "Image generation successful", "image_urls": image_paths})

    #     except Exception as e:
    #         print(f"Error generating image: {str(e)}")
    #         return jsonify({"error": "Failed to generate image"}), 500

    @app.route("/api/generate-image-from-prompt", methods=["POST"])
    def generate_image_from_prompt():
        try:
            # Ensure the request content type is JSON
            if request.content_type != 'application/json':
                return jsonify({"error": "Content-Type must be application/json"}), 415

            data = request.get_json()
            print("generate_image_from_prompt Data: " + str(data))
            positive_prompt = data.get("positive_prompt", "")
            save_previews = data.get("save_previews", False)

            if not positive_prompt:
                return jsonify({"error": "positive_prompt is required"}), 400

            workflow_json = load_workflow(T2I_WORKFLOW_PATH)
            print("Workflow loaded successfully!")
            if workflow_json is None:
                return jsonify({"error": "Failed to load workflow"}), 500

            encoded_images = prompt_to_image(workflow_json, positive_prompt, save_previews)
            if not encoded_images:
                return jsonify({"error": "Image generation failed"}), 500

            print('Encoded images: ' + str(encoded_images))
            return jsonify({"message": "Image generation successful", "images": encoded_images})

        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return jsonify({"error": "Failed to generate image"}), 500


    @app.route("/api/generate-image-from-reference", methods=["POST"])
    def generate_image_from_reference():
        try:
            if request.content_type != 'application/json':
                return jsonify({"error": "Content-Type must be application/json"}), 415

            data = request.get_json()
            print("generate_image_from_reference Data: " + str(data))

            


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
