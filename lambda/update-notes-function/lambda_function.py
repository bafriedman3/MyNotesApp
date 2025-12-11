import json
import boto3

# This function updates the notes with the new content
# updating the corresponding note in the dynamodb table

def lambda_handler(event, context):
    print(event)
    if isinstance(event, str):
        event = json.loads(event)
    user_id = event['userId']
    note_id = int(event['noteId'])

    new_content = event['content']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('UserNotes')

    try:
        response = table.update_item(
            Key={
                'userId': user_id,
                'noteId': note_id
            },
            UpdateExpression="SET content = :content",
            ExpressionAttributeValues={
                ':content': new_content
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
