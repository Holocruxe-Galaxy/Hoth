from utils import MongoDBConnection
from bson.objectid import ObjectId
from utils import SMTPMailSender
import os

def contact_info(body:dict)-> dict:
    """
    Handles contact information submission.
    This function processes the contact information provided by a user.
    It expects a dictionary with the user's name, email, phone number, and message.
    It returns a confirmation message indicating the status of the operation.

    Args:
        body (dict): 
            - name (str): Name of the person.
            - email (str): Email address of the person.
            - phone (str): Phone number of the person.
            - message (str): Message to be sent.
    Returns:
        dict: 
            - status (str): Status of the operation.
            - message (str): Confirmation message.
    """
    
    if not isinstance(body, dict):
        return {"status": "error", "message": "Invalid input format. Expected a dictionary."}

    required_fields = ["name", "email", "phone", "message"]
    for field in required_fields:
        if field not in body or not body[field]:
            return {"status": "error", "message": f"Missing required field: {field}"}

    mongo = MongoDBConnection(f"mongo_db_secret_{os.getenv('STAGE')}", os.getenv('STAGE'))
    mongo.connect()
    if not mongo.is_connected():
        return {"status": "error", "message": "Database connection failed."}
    
    #DB connection and information storage
    mongo.insert_one("landing_contact_info", {
        "name": body["name"],
        "email": body["email"],
        "phone": body["phone"],
        "message": body["message"]
    })
    mongo.disconnect()

    # Send welcome email to contact@holocruxe.com
    template_path = os.path.join(os.path.dirname(__file__), '../templates/contact.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    contacto_html = template.replace('{{name}}', body['name'])
    contacto_html = contacto_html.replace('{{email}}', body['email'])
    contacto_html = contacto_html.replace('{{message}}', body['message'])
    smtp = SMTPMailSender(
        smtp_host=os.getenv('SMTP_HOST'),
        smtp_port=int(os.getenv('SMTP_PORT', 587)),
        username=os.getenv('SMTP_USER'),
        password=os.getenv('SMTP_PASS'),
        from_email=os.getenv('SMTP_FROM'),
        use_tls=False,
        use_ssl=True
    )
    print("Sending welcome email to " + os.getenv('SMTP_FROM'))
    smtp.send(os.getenv('SMTP_FROM'), contacto_html, subject="¡Bienvenido a Holocruxe!")
    
    return {
        "status": "success",
        "message": f"Thank you {body['name']}! Your message has been received."
    }

# Example usage:
# body = {
#     "name": "John Doe",
#     "email": "jhon@doe.com",
#     "phone": "+1234567890",
#     "message": "Hello, I would like to know more about your services."
# }
# response = contact_info(body)
# print(response)
# Output: {'status': 'success', 'message': 'Thank you John Doe! Your message has been received.'}
