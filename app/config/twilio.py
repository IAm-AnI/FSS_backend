from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.config.settings import settings
from app.config.logger import logger

try:
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
except Exception as e:
    logger.error(f"Failed to initialize Twilio client: {e}")
    client = None

def send_sms(to_number: str, body: str) -> bool:
    if not client:
        logger.error("Twilio client is not initialized. Cannot send SMS.")
        return False
        
    try:
        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_number
        )
        logger.info(f"Message sent to {to_number} with SID: {message.sid}")
        return True
    except TwilioRestException as e:
        logger.error(f"Twilio error sending SMS to {to_number}: {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending SMS: {e}")
        return False