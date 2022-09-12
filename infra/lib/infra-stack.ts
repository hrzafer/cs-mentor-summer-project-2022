import * as cdk from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as apigw from "aws-cdk-lib/aws-apigateway";
import * as path from "path";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";

export class InfraStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const usersTable = new dynamodb.Table(this, "Users", {
      tableName: "FocusTrackerUsers",
      partitionKey: { name: "UserId", type: dynamodb.AttributeType.STRING },
      sortKey: { name: "CreatedAt", type: dynamodb.AttributeType.NUMBER },
      // UserName
      // CreatedAt
      // Email
    });

    const sessionsTable = new dynamodb.Table(this, "Sessions", {
      tableName: "FocusTrackerSessions",
      partitionKey: { name: "SessionId", type: dynamodb.AttributeType.STRING },
      // StartedAt
      // EndedAt
      // UserId (global secondary index)
      // Name
    });

     // 👇 add global secondary index
     sessionsTable.addGlobalSecondaryIndex({
      indexName: 'UserIdIndex',
      partitionKey: {name: 'UserId', type: dynamodb.AttributeType.STRING},
      sortKey: {name: 'StartedAt', type: dynamodb.AttributeType.STRING},      
    });

    // defines an AWS Lambda resource
    const lambda_function = new lambda.Function(this, "FocusTrackerLambda", {
      functionName: "FocusTrackerLambda",
      runtime: lambda.Runtime.PYTHON_3_9, // execution environment
      code: lambda.Code.fromAsset("../backend"), // code loaded from "lambda" directory
      handler: "lambda.handler", // file is "lambda.py", function is "handler"
    });

    // defines an API Gateway REST API resource backed by our "lambda" function.
    const api = new apigw.LambdaRestApi(this, "FocusTrackerApi", {
      handler: lambda_function,
      proxy: false,
    });

     // grant the lambda role read/write permissions to our table
     usersTable.grantReadWriteData(lambda_function);

     // grant the lambda role read/write permissions to our table
     sessionsTable.grantReadWriteData(lambda_function);

    // # POST /Users body: {}
    // # PUT /Users/:id body: {} //Update user info
    // # DELETE /Users/:id
    // # GET /Users/:id/Sessions


    // # GET /Users/:id/Sessions/:id
    // # POST /Users/:id/Sessions
    // # PUT /Users/:id/Sessions/:id //update session info
    // # DELETE /Users/:id/Sessions/:id

    // /users
    const users = api.root.addResource("users");
    users.addMethod("GET");   // Get all users
    users.addMethod("POST");  // Add a users
    
    // /users/{userId}
    const user = users.addResource("{userId}");
    user.addMethod("GET");    // Get a single user
    user.addMethod("PUT");    // Update a user
    user.addMethod("DELETE"); // Delete a user

    // /users/{userId}/sessions
    const sessions = user.addResource("sessions");
    sessions.addMethod("GET");  // Get all sessions of a user
    sessions.addMethod("POST"); // Add a session to a user
    
    
    // /users/{userId}/sessions
    const session = sessions.addResource("{sessionId}");
    session.addMethod("GET");   // Get a single session of a user
    session.addMethod("PUT");   // Update a session of a user
    session.addMethod("DELETE");// Delete a session of a user 
    

    new cdk.CfnOutput(this, "apiUrl", { value: api.url });
  }
}
