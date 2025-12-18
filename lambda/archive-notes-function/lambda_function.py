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
        raise e

def trans_archive_notes(notes):
    actions = []

    for note in notes:
        archived_ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        actions.append({
            "Put": {
                "TableName": "UserNotesArchive",
                "Item": {
                    "PK": {"S": note["userId"]},
                    "SK": {"S": f"{archived_ts}#{note['noteId']}"},
                    "content": {"S": note["content"]},
                    "title": {"S": note["title"]},
                    "updated_ts": {"N": note["updated_ts"]}
                },
                "ConditionExpression": "attribute_not_exists(PK)"
            }
        })
        actions.append({
            "Delete": {
                "TableName": "UserNotes",
                "Key": {
                    "PK": {"S": note["userId"]},
                    "SK": {"S": note["noteId"]}
                }
            }
        })

    client.transact_write_items(TransactItems=actions)