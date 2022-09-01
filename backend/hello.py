import boto3
import re
import logging
import json


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    print(path)

    # GET /users
    if httpMethod == 'GET' and path == '/users':
        # responseBody = users.get_all()
        return buildResponse(200, path)

    # POST /users
    if httpMethod == 'POST' and path == '/users':
        # responseBody = users.get_all()
        return buildResponse(200, [path, json.loads(event['body'])])

    # GET /users/{userId}
    if httpMethod == 'GET' and re.search(r'/users/(\d+)$', path):
        user_id = re.search(r'/users/(\d+)', path)[1]
        return buildResponse(200, [user_id, 'get', event['pathParameters']['userId']])

    # PUT /users/{userId}
    if httpMethod == 'PUT' and re.search(r'/users/(\d+)$', path):
        user_id = re.search(r'/users/(\d+)', path)[1]
        return buildResponse(200, [user_id, 'put', event['pathParameters']['userId'], json.loads(event['body'])])

    # DELETE /users/{userId}
    if httpMethod == 'DELETE' and re.search(r'/users/(\d+)$', path):
        user_id = re.search(r'/users/(\d+)', path)[1]
        return buildResponse(200, [user_id, 'delete', event['pathParameters']['userId']])

    # Get /users/{userId}/sessions
    if httpMethod == 'GET' and re.search(r'/users/(\d+)/sessions$', path):
        return buildResponse(200, [path, event['pathParameters']['userId']])
 # GET /users/{userId}/sessions/{sessionId}
    if httpMethod == 'GET' and re.search(r'/users/(\d+)/sessions/\d+$', path):
        return buildResponse(200, [path, event['pathParameters']['userId'], event['pathParameters']['sessionId']])

     # POST /users
    if httpMethod == 'POST' and re.search(r'/users/(\d+)/sessions$', path):
        # responseBody = users.get_all()
        return buildResponse(200, [path, json.loads(event['body'])])

     # PUT /users/{userId}/sessions/{sessionId}
    if httpMethod == 'PUT' and re.search(r'/users/(\d+)/sessions/\d+$', path):
        return buildResponse(200, [path, event['pathParameters']['userId'], event['pathParameters']['sessionId'], json.loads(event['body'])])

     # DELETE /users/{userId}/sessions/{sessionId}
    if httpMethod == 'DELETE' and re.search(r'/users/(\d+)/sessions/\d+$', path):
        return buildResponse(200, [path, event['pathParameters']['userId'], event['pathParameters']['sessionId']])


def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    return response
