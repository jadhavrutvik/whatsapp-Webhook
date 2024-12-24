import httpx
import logging

# Set up logging
logger = logging.getLogger(__name__)

class WhatsAppService:
    BASE_URL = "https://graph.facebook.com/v14.0/551602171364742/messages"
    ACCESS_TOKEN = "EAAPp0EdFjMYBO78Fij4nv6xJfI5cQJcNquIHmXMZAZAHp0UxQTQ4g2n7SANcoRt26ZBZCguPfEitzP5LKXifAZBtPlSojCPv0iprkS1QBrJoLGxSoBFTgJUPx7hPuHHu2yp2EBEaI4vpUzttsy3m8MDZA8z6PkCpmeZBCiY3v6n8nKNrdDN0nZAhBeMsHcSO7049vdeoMu4I38mZAgZAUFzSbo4JWkreEZD"

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {self.ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    async def send_message(self, mobile_no, message):
        """
        Sends a message asynchronously via the WhatsApp Business API.
        :param mobile_no: Recipient's phone number
        :param message: Message content
        :return: Tuple (success: bool, response: dict)
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": mobile_no,
            "text": {"body": message},
        }

        try:
            logger.info(f"Sending message to {mobile_no}: {message}")
            async with httpx.AsyncClient() as client:
                response = await client.post(self.BASE_URL, json=payload, headers=self.headers)
            print(response.json())
            if response.status_code == 200:
                logger.info(f"Message successfully sent to {mobile_no}")
                return True, response.json()  # Returns a tuple of success and response data
            else:
                logger.error(f"Failed to send message: {response.text}")
                return False, response.json()

        except Exception as e:
            logger.exception("An error occurred while sending the message.")
            return False, {"error": str(e)}