import json
import boto3
from boto3.dynamodb.conditions import Attr
import time
from datetime import datetime, timezone

dynamodb = boto3.resource('dynamodb')
client = boto3.client("dynamodb")
    
def lambda_handler(event, context):
    table = dynamodb.Table('UserNotes')
    period = event['period']
    cutoff_time = int(time.time()) - period
    try:
        response = table.scan(
            IndexName='UpdateTimeIndex',
            FilterExpression=Attr('updated_ts').lt(cutoff_time)
        )
        items = response.get('Items', [])
        i = 0
        while i<len(items):
            trans_archive_notes(items[i:i+12])
            i = i+12
    except Exception as e:
        print(f"Archive failed: {str(e)}")
        if hasattr(e, 'response'):
            # This will print the actual "Message" for each failed item
            reasons = e.response.get('CancellationReasons', [])
            for i, reason in enumerate(reasons):
                if reason.get('Code') != 'None':
                    print(f"Item {i} failed with {reason.get('Code')}: {reason.get('Message')}")
        raise e

def trans_archive_notes(notes):
    actions = []

    for note in notes:
        print("current note is: ", note)
        archived_ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        actions.append({
            "Put": {
                "TableName": "UserNotesArchive",
                "Item": {
                    "userId": {"S": note["userId"]},
                    "archived_ts#noteId": {"S": f"{archived_ts}#{note['noteId']}"},
                    "noteId": {"S": note['noteId']},
                    "content": {"S": note["content"]},
                    "title": {"S": note["title"]},
                    "updated_ts": {"N": str(note["updated_ts"])}
                },
                "ConditionExpression": "attribute_not_exists(userId)"
            }
        })
        actions.append({
            "Delete": {
                "TableName": "UserNotes",
                "Key": {
                    "userId": {"S": note["userId"]},
                    "noteId": {"S": note["noteId"]}
                }
            }
        })

    client.transact_write_items(TransactItems=actions)