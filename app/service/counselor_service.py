import uuid
import boto3
from flask import jsonify, request
from botocore.exceptions import ClientError
from app.models.counselor_models import counselor_table

s3 = boto3.client('s3')
S3_BUCKET = 'counselor-bucket-wgc'


def create_counselor(data, files):
    counselor_id = str(uuid.uuid4())
    name = data.get('name')
    education_history = data.get('education_history')
    experience = data.get('experience')
    about = data.get('about')
    specialization = data.get('specialization')
    mailid = data.get('mailid')
    contact_number = data.get('contact_number')

    if not name or not mailid:
        return {'error': 'Required fields are missing.'}, 400

    counselor_details = {
        'counselorId': counselor_id,
        'name': name,
        'education_history': education_history,
        'experience': experience,
        'about': about,
        'specialization': specialization,
        'mailid': mailid,
        'contact_number': contact_number
    }

    try:
    
        # Check if a photo file was uploaded and process it
        if 'PhotoURL' in files:
            photo_file = files['PhotoURL']
            if photo_file and (photo_file.filename.endswith('.JPEG') or photo_file.filename.endswith('.pdf')):
                photo_filename = f"{counselor_id}/{photo_file.filename}"
                s3.upload_fileobj(photo_file, S3_BUCKET, photo_filename)
                photo_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{photo_filename}"
                counselor_details['PhotoURL'] = photo_url
            else:
                return {'error': 'Invalid file type. Only JPEG or PDF files are allowed.'}, 400
        # Insert the counselor details into the DynamoDB table
        response = counselor_table.put_item(Item=counselor_details)

        return {
            'message': 'Counselor created successfully.',
            'counselorId': counselor_id,
            'counselor': counselor_details
        }, 201
    except ClientError as e:
        print(f"Error inserting item: {e}")
        return {'error': 'Error creating counselor.'}, 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {'error': 'Unexpected error occurred.'}, 500


def get_all_counselors():
    try:
        response = counselor_table.scan()
        counselors = response.get('Items', [])
        return {'counselors': counselors}, 200
    except ClientError as e:
        print(f"Error retrieving counselors: {e}")
        return {'error': 'Error retrieving counselors.'}, 500


def get_counselor_by_id(counselor_id):
    try:
        response = counselor_table.get_item(Key={'counselorId': counselor_id})
        counselor = response.get('Item')
        if counselor:
            return {'counselorId': counselor_id, 'counselor': counselor}, 200
        else:
            return {'error': 'Counselor not found.'}, 404
    except ClientError as e:
        print(f"Error retrieving counselor: {e}")
        return {'error': 'Error retrieving counselor.'}, 500


def update_counselor(counselor_id, data):
    update_expression = "SET "
    expression_attribute_values = {}
    expression_attribute_names = {}

    for key, value in data.items():
        if key == "name":
            expression_attribute_names["#name"] = key
            update_expression += "#name = :name, "
            expression_attribute_values[":name"] = value
        else:
            update_expression += f"{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value

    update_expression = update_expression.rstrip(', ')

    try:
        response = counselor_table.update_item(
            Key={'counselorId': counselor_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ReturnValues="ALL_NEW"
        )
        updated_counselor = response.get('Attributes')
        return {
            'message': 'Counselor updated successfully.',
            'counselorId': counselor_id,
            'counselor': updated_counselor
        }, 200
    except ClientError as e:
        print(f"Error updating counselor: {e}")
        return {'error': 'Error updating counselor.'}, 500


def delete_counselor(counselor_id):
    try:
        response = counselor_table.delete_item(
            Key={'counselorId': counselor_id},
            ConditionExpression="attribute_exists(counselorId)"
        )
        return {'message': f'Counselor with ID {counselor_id} deleted successfully.'}, 200
    except ClientError as e:
        print(f"Error deleting counselor: {e}")
        return {'error': f'Error deleting counselor with ID {counselor_id} or counselor not found.'}, 500
