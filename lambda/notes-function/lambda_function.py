import json
import boto3

def lambda_handler(event, context):
    # This function retrieves notes for a particular user
    print("running notes function")
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
