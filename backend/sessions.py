import logging
import time
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class StorageError(Exception):
    pass


tableName = 'FocusTrackerSessions'


class Sessions:
    """
    Encapsulates sessions storage in a DynamoDB table.
    """

    def __init__(self, tableName):
        """
        :param table: An existing DynamoDB table.
        :param ddb_resource: A Boto3 DynamoDB resource.
        """
        dynamodb = boto3.resource('dynamodb')
        self.table = dynamodb.Table(tableName)
        self.tableName = tableName

    def create(self, item):
        try:
            now = int(time.time())
            item['SessionId'] = uuid.uuid4().hex
            item['CreatedAt'] = now
            self.table.put_item(Item=item)
        except ClientError as err:
            logger.exception(
                "Couldn't add or update item %s in table %s.", item, self.tableName)
            raise StorageError(err)

    def update(self, updated_item):
        try:
            result = self.table.query(
                KeyConditionExpression=Key('SessionId').eq(updated_item['SessionId']))

            if result['Count'] == 1:
                current_item = result['Items'][0]
                current_item['StartedAt'] = updated_item['StartedAt']
                current_item['EndedAt'] = updated_item['EndedAt']
                current_item['Title'] = updated_item['Title']
                self.table.put_item(Item=current_item)
                return current_item
            else:
                return None
        except ClientError as err:
            logger.exception(
                "Couldn't add or update item %s in table %s.", updated_item, self.tableName)
            raise StorageError(err)

    def get_all(self):
        try:
            response = self.table.scan()
            return response['Items']
        except ClientError as err:
            logger.exception(
                "Couldn't get items from table %s.", self.tableName)
            raise StorageError(err)

    def get_by_user(self, user_id):
        try:
            result = self.table.query(
                # Add the name of the index you want to use in your query.
                IndexName="UserIdIndex",
                KeyConditionExpression=Key('UserId').eq(user_id),
            )

            return result['Items']

        except ClientError as err:
            logger.exception(
                "Couldn't get items with key %s from table %s.", user_id, self.tableName)
            raise StorageError(err)

    def get(self, user_id, session_id):
        try:
            result = self.table.query(
                # Add the name of the index you want to use in your query.
                KeyConditionExpression=Key('SessionId').eq(session_id),
            )

            if result['Count'] == 1:
                return result['Items'][0]
            else:
                return None

        except ClientError as err:
            logger.exception(
                "Couldn't get items with key %s from table %s.", user_id, self.tableName)
            raise StorageError(err)

    def remove(self, session_id):
        try:
            result = self.table.query(
                KeyConditionExpression=Key('SessionId').eq(session_id))
            if result['Count'] == 1:
                item = result['Items'][0]
                self.table.delete_item(
                    Key={'SessionId': session_id})

                return item
            else:
                return None
        except ClientError as err:
            logger.exception(
                "Couldn't add or update item %s in table %s.", item, self.tableName)
            raise StorageError(err)
