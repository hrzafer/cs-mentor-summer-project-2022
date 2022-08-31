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
    const hello = new lambda.Function(this, "FocusTrackerLambda", {
      functionName: "FocusTrackerLambda",
      runtime: lambda.Runtime.PYTHON_3_9, // execution environment
      code: lambda.Code.fromAsset("../backend"), // code loaded from "lambda" directory
      handler: "hello.handler", // file is "hello", function is "handler"
    });

    // defines an API Gateway REST API resource backed by our "hello" function.
    const api = new apigw.LambdaRestApi(this, "FocusTrackerApi", {

      handler: hello,
    });

    new cdk.CfnOutput(this, "apiUrl", { value: api.url });
  }
}
