import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'FocusTrackerSessions'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)


class Sessions:
    def get_all(self):
        try:
            response = table.scan()
            result = response['Items']

            while 'LastEvaluatedKey' in response:
                response = table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey'])
                result.extend(response['Items'])

            body = {
                'products': result
            }
            return body
        except:
            logger.exception('Custom Error Message')

    def get(self, sessionId):
        try:
            response = table.get_item(
                Key={
                    'SessionId': sessionId
                }
            )
            if 'Item' in response:
                return response['Item']
            else:
                return {'Message:' 'id: %s not found' % sessionId}
        except:
            logger.exception('Custom Error Message')

    def create(self, requestBody):
        try:
            table.put_item(Item=requestBody)
            body = {
                'Operation': 'SAVE',
                'Message': 'SUCCESS',
                'Item': requestBody
            }
            return body
        except:
            logger.exception('Custom Error Message')

    def add(self, userId, updateKey, updateValue):
        try:
            response = table.update_item(
                Key={
                    'UserId': userId
                },
                UpdateExpression='set %s = :value' % updateKey,
                ExpressionAttributeValues={
                    ':value': updateValue
                },
                ReturnValues='UPDATED_NEW'
            )
            body = {
                'Operation': 'UPDATE',
                'Message': 'SUCCESS',
                'UpdatedAttributes': response
            }
            return body
        except:
            logger.exception('Custom Error Message')

    def remove(self, sessionId):
        try:
            response = table.delete_item(
                Key={
                    'SessionId': sessionId
                },
                ReturnValues='ALL_OLD'
            )
            body = {
                'Operation': 'DELETE',
                'Message': 'SUCCESS',
                'deletedItem': response
            }
            return body
        except:
            logger.exception('Custom Error Message')
