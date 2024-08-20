import uuid
import boto3
from flask import jsonify, request
from botocore.exceptions import ClientError
from app.models.counselor_models import counselor_table
from datetime import datetime

s3 = boto3.client('s3')
S3_BUCKET = 'counselor-bucket-wgc'

from datetime import datetime

def create_counselor(data, files,  current_user):
    counselor_id = str(uuid.uuid4())
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    gender = data.get('gender')
    mailid = data.get('mailid')
    contact_number = data.get('contact_number')
    alternate_contact_number = data.get('alternate_contact_number')
    history = data.get('history')
    experience = data.get('experience')
    date_of_birth = data.get('date_of_birth')
    address = data.get('address')
    country = data.get('country')
    state = data.get('state')
    district = data.get('district')
    city = data.get('city')
    pincode = data.get('pincode')
    price = data.get('price')
    specialization = data.get('specialization')
    qualification = data.get('qualification')
    language_spoken = data.get('language_spoken')
    achievements = data.get('achievements')
    date_of_joining = data.get('date_of_joining')
    rating = data.get('rating', 0)  # Default to 0 if not provided
    isActive = data.get('isActive', True)  # Default to True if not provided
    linkedinURL = data.get('linkedinURL', '')

    # Check if all required fields are present and not empty
    required_fields = [
        firstName, lastName, gender, mailid, contact_number, alternate_contact_number,
        experience, date_of_birth, address, country, state, district, city, pincode,
        price, specialization, qualification, language_spoken, achievements, date_of_joining
    ]

    if any(field is None or field == '' for field in required_fields):
        return {'error': 'All fields are required.'}, 400

    counselor_details = {
        'counselorId': counselor_id,
        'firstName': firstName,
        'lastName': lastName,
        'gender': gender,
        'mailid': mailid,
        'contact_number': contact_number,
        'alternate_contact_number': alternate_contact_number,
        'history': history,
        'experience': experience,
        'date_of_birth': date_of_birth,
        'address': address,
        'country': country,
        'state': state,
        'district': district,
        'city': city,
        'pincode': pincode,
        'price': price,
        'specialization': specialization,
        'qualification': qualification,
        'language_spoken': language_spoken,
        'achievements': achievements,
        'date_of_joining': date_of_joining,
        'rating': rating,
        'isActive': isActive,
        'linkedinURL': linkedinURL,
        'createdBy': current_user,  
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt':  current_user,
        'updatedBy': datetime.utcnow().isoformat(),
        'deletedAt': None,
        'deletedBy': None
    }

    try:
        # Check if a photo file was uploaded and process it
        if 'PhotoURL' in files:
            photo_file = files['PhotoURL']
            if photo_file and (photo_file.filename.endswith('.JPEG') or photo_file.filename.endswith('.pdf') or photo_file.filename.endswith('.jpg')):
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


def update_counselor(counselor_id, data, files):
    # Fetch current counselor details from DynamoDB
    try:
        current_counselor = counselor_table.get_item(Key={'counselorId': counselor_id}).get('Item')
        if not current_counselor:
            return {'error': 'Counselor not found.'}, 404
    except ClientError as e:
        print(f"Error fetching counselor: {e}")
        return {'error': 'Error fetching counselor details.'}, 500

    update_expression = "SET "
    expression_attribute_values = {}
    expression_attribute_names = {}

    # Process FormData fields and compare with current values
    for key, value in data.items():
        if value and current_counselor.get(key) != value:  # Update only if the value has changed
            expression_attribute_names[f"#{key}"] = key
            update_expression += f"#{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value

    # Handle file upload
    if 'PhotoURL' in files:
        photo_file = files['PhotoURL']
        if photo_file and (photo_file.filename.endswith('.JPEG') or photo_file.filename.endswith('.pdf')):
            photo_filename = f"{counselor_id}/{photo_file.filename}"
            s3.upload_fileobj(photo_file, S3_BUCKET, photo_filename)
            photo_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{photo_filename}"
            if current_counselor.get("PhotoURL") != photo_url:  
                update_expression += "PhotoURL = :photo_url, "
                expression_attribute_values[":photo_url"] = photo_url

    # Remove trailing comma and space
    update_expression = update_expression.rstrip(', ')

    # Ensure there's at least one field to update
    if not expression_attribute_values:
        return {'message': 'No fields to update; all values are unchanged.'}, 200

    try:
        # Conditionally include ExpressionAttributeNames if it is not empty
        update_item_params = {
            'Key': {'counselorId': counselor_id},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_attribute_values,
            'ReturnValues': "ALL_NEW"
        }

        if expression_attribute_names:  # Only add if there are names to map
            update_item_params['ExpressionAttributeNames'] = expression_attribute_names

        response = counselor_table.update_item(**update_item_params)
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
