import boto3
from botocore.exceptions import ClientError
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION

# Initialize DynamoDB resource
dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

def create_table_if_not_exists(table_name, key_schema, attribute_definitions):
    try:
        # Attempt to create the table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        # Wait until the table exists
        table.wait_until_exists()
        print(f"Table {table_name} created successfully.")
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        # Handle the case where the table already exists
        print(f"Table {table_name} already exists.")
        return dynamodb.Table(table_name)
    except ClientError as e:
        # Handle any other client errors
        print(f"Failed to create table {table_name}: {e}")
        return None
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred while creating table {table_name}: {e}")
        return None
