import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    # This function retrieves notes for a particular user
    print(event)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('UserNotes')
    userId = event['userId']    
    print(userId)
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(userId)
        )
        items = response['Items']
        if items:
            for item in items:
                if 'updated_ts' in item:
                    # 1. Convert epoch (float/int) to datetime object
                    # Note: if your epoch is in milliseconds, divide by 1000 first
                    dt_object = datetime.fromtimestamp(float(item['updated_ts']))
                    
                    # 2. Format as a string (e.g., "2025-12-16 14:30:05")
                    item['updated_ts'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')
            return {
                'statusCode': 200,
                'body': json.dumps(items, default=lambda x: str(x))
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Item not found.')
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps('Error: ' + str(e))
        }
