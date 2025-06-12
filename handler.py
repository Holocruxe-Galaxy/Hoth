import json
from function.contact import contact_info

def CORS_response(status_code:int, body:dict ):
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS, POST, GET",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": 3600,
    }

def contact_handler(event, context):
    try:
        body = event.get("body")
        if isinstance(body, str):
            body = json.loads(body)
        result = contact_info(body)
        if result['status'] == "error":
            return CORS_response(400, result)
        return CORS_response(200 if result.get("status") == "success" else 400, result)
    except Exception as e:
        return CORS_response(500, {"status": "error", "message": str(e)})
