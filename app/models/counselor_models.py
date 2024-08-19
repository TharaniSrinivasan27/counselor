from config import COUNSELOR_TABLE_NAME
from app.utils.databaseutils import create_table_if_not_exists

# Define table parameters
counselor_table = create_table_if_not_exists(
    COUNSELOR_TABLE_NAME,
    [{ 'AttributeName':'counselorId',
      'KeyType':'HASH'}],
    [{
        'AttributeName':'counselorId',
        'AttributeType':'S'
    }]
)

