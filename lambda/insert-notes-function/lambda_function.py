import json
import boto3
import time
from decimal import Decimal

# This function updates the notes with the new content
# updating the corresponding note in the dynamodb table

def lambda_handler(event, context):
    print(event)
    if isinstance(event, str):
        event = json.loads(event)
    user_id = event['userId']
    note_id = int(event['noteId'])
    note_content = event['content']
    float_timestamp = time.time()
    current_timestamp = Decimal(str(float_timestamp))
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('UserNotes')

    try:
        item = {
            'userId': user_id,
            'noteId': note_id,
            'content': note_content,
            'updated_ts': current_timestamp
        }
        response = table.put_item(
            Item=item
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'noteId': str(note_id), 'message': 'Note created successfully'})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }