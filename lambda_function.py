import json, os, boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLE_NAME", "StudentRecords")
ddb = boto3.resource("dynamodb")
table = ddb.Table(TABLE_NAME)

def _resp(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    method = event.get("httpMethod", "")
    qs = event.get("queryStringParameters") or {}
    body = event.get("body")
    if isinstance(body, str):
        try:
            body = json.loads(body) if body else {}
        except json.JSONDecodeError:
            return _resp(400, {"error": "Invalid JSON"})

    try:
        if method == "POST":  # Create
            if not body or "student_id" not in body:
                return _resp(400, {"error": "student_id required"})
            table.put_item(Item=body)
            return _resp(200, {"message": "Student record added"})

        if method == "GET":  # Read
            sid = (qs or {}).get("student_id")
            if not sid:
                return _resp(400, {"error": "student_id query required"})
            res = table.get_item(Key={"student_id": sid})
            return _resp(200, res.get("Item") or {})

        if method == "PUT":  # Update
            if not body or "student_id" not in body:
                return _resp(400, {"error": "student_id required"})
            table.put_item(Item=body)
            return _resp(200, {"message": "Student record updated"})

        if method == "DELETE":  # Delete
            sid = (qs or {}).get("student_id")
            if not sid:
                return _resp(400, {"error": "student_id query required"})
            table.delete_item(Key={"student_id": sid})
            return _resp(200, {"message": "Student record deleted"})

        if method == "OPTIONS":  # CORS
            return _resp(200, {})

        return _resp(405, {"error": "Method not allowed"})
    except ClientError as e:
        return _resp(500, {"error": str(e)})
