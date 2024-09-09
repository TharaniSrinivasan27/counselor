import boto3
from botocore.exceptions import ClientError
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION
dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

def create_table_if_not_exists(table_name, key_schema, attribute_definitions):
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()
        print(f"Table {table_name} created successfully.")
        return table
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print(f"Table {table_name} already exists.")
        return dynamodb.Table(table_name)
    except ClientError as e:
        print(f"Failed to create table {table_name}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while creating table {table_name}: {e}")
        return None
