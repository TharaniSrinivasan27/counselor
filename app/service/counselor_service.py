import uuid
import boto3
from flask import jsonify, request
import requests
from botocore.exceptions import ClientError
from app.models.counselor_models import counselor_table
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

s3 = boto3.client('s3')
S3_BUCKET = 'counselor-bucket-wgc'

def generate_presigned_url(filename, content_type):
    try:
        counselor_id = str(uuid.uuid4())
        file_key = f"{counselor_id}/{filename}"
        response = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': S3_BUCKET, 
                'Key': file_key,
                'ContentType': content_type
            },
            ExpiresIn=3600
        )
        return response, file_key
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None, None

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'.jpeg', '.png', '.jpg', '.pdf'}
    ext = filename.lower().split('.')[-1]
    return f".{ext}" in ALLOWED_EXTENSIONS

def create_counselor(data, current_user):
    counselor_id = str(uuid.uuid4())
    firstName = data['firstName']
    lastName = data['lastName']
    gender = data['gender']
    mailid = data['mailid']
    contact_number = data['contact_number']
    alternate_contact_number = data['alternate_contact_number']
    history = data['history']
    experience = data['experience']
    date_of_birth = data['date_of_birth']
    address = data['address']
    country = data['country']
    state = data['state']
    district = data['district']
    city = data['city']
    pincode = data['pincode']
    price = data['price']
    specialization = data['specialization']
    qualification = data['qualification']
    language_spoken = data['language_spoken']
    achievements = data['achievements']
    date_of_joining = data['date_of_joining']
    rating = Decimal(data['rating']) if 'rating' in data else Decimal('0')
    isActive = data['isActive'] if 'isActive' in data else True
    linkedinURL = data['linkedinURL'] if 'linkedinURL' in data else ''
    availability_status = data['availability_status']
    photo_name = data['PhotoURL'] if 'PhotoURL' in data else ''  
    created_at = datetime.utcnow().isoformat()
    updated_at = created_at

    required_fields = [
        firstName, lastName, gender, mailid, contact_number, alternate_contact_number,
        experience, date_of_birth, address, country, state, district, city, pincode,
        price, specialization, qualification, language_spoken, achievements,
        date_of_joining, availability_status
    ]

    if any(field is None or field == '' for field in required_fields):
        return {'error': 'All fields are required.'}, 400
    presigned_url, file_key = generate_presigned_url(photo_name, 'image/jpeg')  
    if not presigned_url:
        return {'error': 'Error generating presigned URL.'}, 500

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
        'availability_status': availability_status,
        'PhotoURL': file_key,  
        'created_by': current_user,
        'created_at': created_at,
        'updated_by': current_user,
        'updated_at': updated_at,
        'deletedAt': None,
        'deletedBy': None
    }

    try:
        counselor_table.put_item(Item=counselor_details)
        print(f"Presigned URL: {presigned_url}")

        return {
            'message': 'Counselor created successfully.',
            'counselorId': counselor_id,
            'counselor': counselor_details,
            'presigned_url': presigned_url  
        }, 201
    except ClientError as e:
        print(f"Error inserting item into DynamoDB: {e}")
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

def update_counselor(counselor_id, data, current_user):
    try:
        print(f"Updating counselor with ID: {counselor_id}")
        response = counselor_table.get_item(Key={'counselorId': counselor_id})
        print(f"DynamoDB response: {response}")
        
        if 'Item' not in response:
            return {'error': 'Counselor not found'}, 404
        
        counselor = response['Item']
        update_expression = "SET "
        expression_attribute_values = {}
        
        updatable_fields = [
            'firstName', 'lastName', 'gender', 'mailid', 'contact_number',
            'alternate_contact_number', 'history', 'experience', 'date_of_birth',
            'address', 'country', 'state', 'district', 'city', 'pincode',
            'specialization', 'qualification', 'language_spoken',
            'achievements', 'date_of_joining', 'availability_status', 'isActive',
            'linkedinURL'
        ]
        
        for field in updatable_fields:
            if field in data and data[field] != counselor.get(field):
                update_expression += f"{field} = :{field}, "
                expression_attribute_values[f":{field}"] = data[field]
        if 'price' in data:
            try:
                price_value = Decimal(data['price']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if price_value != counselor.get('price'):
                    update_expression += "price = :price, "
                    expression_attribute_values[":price"] = price_value
            except (InvalidOperation, ValueError) as e:
                print(f"Invalid price value: {e}")
                return {'error': 'Invalid price value'}, 400
        if 'rating' in data:
            try:
                rating_value = Decimal(data['rating']).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if rating_value != counselor.get('rating'):
                    update_expression += "rating = :rating, "
                    expression_attribute_values[":rating"] = rating_value
            except (InvalidOperation, ValueError) as e:
                print(f"Invalid rating value: {e}")
                return {'error': 'Invalid rating value'}, 400
            
        new_photo_filename = data.get('PhotoURL')
        if new_photo_filename and allowed_file(new_photo_filename):
            old_photo_url = counselor.get('PhotoURL')
            if old_photo_url:
                try:
                    s3.delete_object(Bucket=S3_BUCKET, Key=old_photo_url)
                    print(f"Old photo {old_photo_url} deleted successfully from S3.")
                except ClientError as e:
                    print(f"Error deleting old photo from S3: {e}")
                    return {'error': 'Failed to delete old photo'}, 500
            
            content_type = 'image/jpeg' if new_photo_filename.lower().endswith('.jpeg') else 'image/png'
            presigned_url, new_file_key = generate_presigned_url(new_photo_filename, content_type)
            
            if not presigned_url:
                return {'error': 'Failed to generate pre-signed URL for the new photo'}, 500
            
            update_expression += "PhotoURL = :PhotoURL, "
            expression_attribute_values[':PhotoURL'] = new_file_key
        update_expression = update_expression.rstrip(', ')
        updated_at = datetime.utcnow().isoformat()
        update_expression += ", updated_by = :updated_by, updated_at = :updated_at"
        expression_attribute_values[":updated_by"] = current_user
        expression_attribute_values[":updated_at"] = updated_at
        
        if not expression_attribute_values:
            return {'error': 'No valid fields provided for update'}, 400
        
        print(f"Update Expression: {update_expression}")
        print(f"Expression Attribute Values: {expression_attribute_values}")

        counselor_table.update_item(
            Key={'counselorId': counselor_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        
        response_data = {
            'message': 'Counselor updated successfully',
            'counselorId': counselor_id
        }
        
        if new_photo_filename:
            response_data['uploadData'] = {
                'presignedUrl': presigned_url,
                'photoUrl': new_file_key
            }

        return response_data, 200
    
    except ClientError as e:
        print(f"Error updating counselor: {e}")
        return {'error': 'Error updating counselor'}, 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {'error': 'Unexpected error occurred'}, 500
          
def delete_counselor(counselor_id, current_user):
    try:
        counselor = counselor_table.get_item(Key={'counselorId': counselor_id}).get('Item')
        if not counselor:
            return {'error': f'Counselor with ID {counselor_id} not found.'}, 404
        photo_url = counselor.get('PhotoURL')
        response = counselor_table.update_item(
            Key={'counselorId': counselor_id},
            UpdateExpression="SET deleted_by = :deleted_by, deletedAt = :deleted_at, isActive = :isActive",
            ExpressionAttributeValues={
                ':deleted_by': current_user,
                ':deleted_at': datetime.utcnow().isoformat(),
                ':isActive': False
            },
            ConditionExpression="attribute_exists(counselorId)",
            ReturnValues="UPDATED_NEW"
        )
        if photo_url:
            try:
                photo_key = photo_url.split(f"https://{S3_BUCKET}.s3.amazonaws.com/")[-1]
                s3.delete_object(Bucket=S3_BUCKET, Key=photo_key)
                print(f"File {photo_key} deleted successfully from S3.")
            except ClientError as e:
                print(f"Error deleting file from S3: {e}")
                return {'error': f'Error deleting photo from S3 for counselor ID {counselor_id}.'}, 500

        return {
            'message': f'Counselor with ID {counselor_id} deleted successfully.',
            'updatedFields': response.get('Attributes')
        }, 200

    except ClientError as e:
        print(f"Error deleting counselor: {e}")
        return {'error': f'Error deleting counselor with ID {counselor_id} or counselor not found.'}, 500