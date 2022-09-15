from audioop import add
import boto3
import re
import logging
import json
from sessions import Sessions
from users import Users
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    print(path)

    if not path.startswith('/users'):
        response = buildResponse(404, 'Not Found')
        return response

    users = Users('FocusTrackerUsers')
    sessions = Sessions('FocusTrackerSessions')

    # GET /users
    if httpMethod == 'GET' and path == '/users':
        responseBody = users.get_all()
        return buildResponse(200, responseBody)

    # POST /users
    if httpMethod == 'POST' and path == '/users':
        response = users.create(json.loads(event['body']))
        return buildResponse(200, response)

    # GET /users/{userId}
    if httpMethod == 'GET' and re.search(r'/users/([a-f0-9]+)$', path):
        user_id = event['pathParameters']['userId']
        user = users.get(user_id)
        if user is not None:
            return buildResponse(200, user)
        else:
            return buildResponse(403, "Not Found")

    # PUT /users/{userId}
    if httpMethod == 'PUT' and re.search(r'/users/([a-f0-9]+)$', path):
        user_id = event['pathParameters']['userId']
        requestBody = json.loads(event['body'])
        requestBody['UserId'] = user_id
        response = users.update(requestBody)
        if response is None:
            return buildResponse(403, "user not found")
        return buildResponse(200, response)

    # DELETE /users/{userId}
    if httpMethod == 'DELETE' and re.search(r'/users/([a-f0-9]+)$', path):
        user_id = event['pathParameters']['userId']
        user = users.remove(user_id)
        if user is not None:
            return buildResponse(200, user)
        else:
            return buildResponse(403, "Not Found")

    # Get /users/{userId}/sessions
    if httpMethod == 'GET' and re.search(r'/users/([a-f0-9]+)/sessions$', path):
        user_id = event['pathParameters']['userId']
        responseBody = sessions.get_by_user(user_id)
        return buildResponse(200, responseBody)

    # GET /users/{userId}/sessions/{sessionId}
    if httpMethod == 'GET' and re.search(r'/users/([a-f0-9]+)/sessions/([a-f0-9]+)$', path):
        user_id = event['pathParameters']['userId']
        session_id = event['pathParameters']['sessionId']
        session = sessions.get(user_id, session_id)
        return buildResponse(200, session)

     # POST /sessions
    if httpMethod == 'POST' and re.search(r'/users/([a-f0-9]+)/sessions$', path):
        session = json.loads(event['body'])
        session['UserId'] = event['pathParameters']['userId']
        response = sessions.create(session)
        return buildResponse(200, response)

     # PUT /users/{userId}/sessions/{sessionId}
    if httpMethod == 'PUT' and re.search(r'/users/([a-f0-9]+)/sessions/([a-f0-9]+)$', path):
        session_id = event['pathParameters']['sessionId']
        updated_item = json.loads(event['body'])
        updated_item['SessionId'] = session_id
        response = sessions.update(updated_item)
        if response is None:
            return buildResponse(403, "session not found")
        return buildResponse(200, response)

     # DELETE /users/{userId}/sessions/{sessionId}
    if httpMethod == 'DELETE' and re.search(r'/users/([a-f0-9]+)/sessions/([a-f0-9]+)$', path):
        session_id = event['pathParameters']['sessionId']
        session = sessions.remove(session_id)
        if session is None:
            return buildResponse(403, "Session not found")
        return buildResponse(200, session)


def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response
