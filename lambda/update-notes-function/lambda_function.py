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

    new_content = event['content']
    float_timestamp = time.time()
    current_timestamp = Decimal(str(float_timestamp))
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('UserNotes')

    try:
        response = table.update_item(
            Key={
                'userId': user_id,
                'noteId': note_id
            },
            UpdateExpression="SET content = :content, updated_ts = :ts",
            ExpressionAttributeValues={
                ':content': new_content,
                ':ts': current_timestamp
            },
            ReturnValues="ALL_NEW"
        )

        return {
            "statusCode": 200,
            "body": json.dumps(response["Attributes"], default=lambda x: str(x))
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }
