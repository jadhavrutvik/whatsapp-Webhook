import json
import logging
from datetime import datetime
from functools import wraps
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from rest_framework.response import Response
from webhook.models import Message
from rest_framework.decorators import api_view
from webhook.service import WhatsAppService
import asyncio  # For async features

# This is the token you set up in your Meta Developer Console
VERIFY_TOKEN = "get_verify"  # Replace with your actual token

# Enable logging to inspect incoming requests
logger = logging.getLogger(__name__)






def asyncapi_view(http_method_names=None):
    def decorator(view_func):
        @wraps(view_func)
        async def _wrapped_view(request, *args, **kwargs):
            try:
                # Call the async view function and await its result
                result = await view_func(request, *args, **kwargs)
                # Ensure the result is a valid Response object
                if isinstance(result, Response):
                    return result
                elif isinstance(result, dict):
                    return JsonResponse(result)
                else:
                    raise TypeError("View must return a Response or dict.")
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        return _wrapped_view
    return decorator

@csrf_exempt
async def webhook(request):
    """
    Handles GET requests for webhook verification and POST requests for processing incoming WhatsApp messages.
    """
    if request.method == 'GET':
        token_sent = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        # Log the token and challenge values
        logger.info(f"Token Sent: {token_sent}, Challenge: {challenge}")

        if token_sent == VERIFY_TOKEN:
            logger.info("Webhook verified successfully.")
            return HttpResponse(challenge)  # Send challenge value back to Meta
        else:
            logger.error("Token mismatch or missing.")
            return HttpResponse("Verification failed", status=403)

    elif request.method == 'POST':
        # Handle incoming messages
        try:
            data = json.loads(request.body.decode('utf-8'))
            logger.info(f"Received message data: {json.dumps(data, indent=2)}")

            # Process the entries in the received data
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    messages = change['value'].get('messages', [])
                    for msg in messages:
                        sender = msg.get('from')  # Sender's phone number
                        message_body = msg.get('text', {}).get('body')  # Message content
                        timestamp = msg.get('timestamp')  # Message timestamp (UNIX)
                        dt_object = datetime.utcfromtimestamp(int(timestamp))  # Convert to datetime

                        exists = await asyncio.to_thread(
                            Message.objects.filter(mobile_no=sender).exists
                        )

                        if exists:
                            # Log duplicate mobile_no and proceed to save other data
                            logger.info(f"Mobile_no {sender} already exists. Adding other details.")
                            await asyncio.to_thread(
                                Message.objects.create,
                                sender="Rutvik",
                                receiver=sender,
                                content=message_body,
                                timestamp=dt_object,
                                mobile_no=None,  # Nullify mobile_no to avoid duplication
                            )
                        else:
                            # Save the message with all details, including mobile_no
                            await asyncio.to_thread(
                                Message.objects.create,
                                sender="Rutvik",
                                receiver=sender,
                                content=message_body,
                                timestamp=dt_object,
                                mobile_no=sender,
                            )

                        # Log the incoming message details
                        logger.info(f"Received message from {sender}: {message_body} at {dt_object}")

            return JsonResponse({"status": "success"})

        except Exception as e:
            logger.exception("Error processing incoming message.")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    else:
        return HttpResponse("Invalid request method", status=405)


import asyncio

@csrf_exempt
async def reply_to_user(request):
    try:
        # Parse incoming JSON data
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        
        # Get mobile numbers and message from the incoming data
        mobile_no_list = data.get('mobile', '').split(",")  # Split the comma-separated list
        msg = data.get('msg', '')

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    # Check if mobile numbers or message are missing
    if not mobile_no_list or not msg:
        return Response(
            {"status": "error", "message": "Mobile numbers and message are required."},
            status=400,
        )

    whatsapp_service = WhatsAppService()

    # Log for debugging
    logger.info("Calling send_message function asynchronously")
    
    try:
        # Create a list of tasks to be executed concurrently
        tasks = []

        for mobile_no in mobile_no_list:
            mobile_no = mobile_no.strip()  # Remove any extra spaces or characters
            logger.info(f"Preparing to send message to: {mobile_no}")
            
            # Make sure the phone number includes the country code (e.g., +91 for India)
            if not mobile_no.startswith('+'):
                mobile_no = '+' + mobile_no

            # Add each task to the list
            tasks.append(whatsapp_service.send_message(mobile_no, msg))

        # Wait for all tasks to complete concurrently
        results = await asyncio.gather(*tasks)

        # Check the results and handle errors if any
        for result, mobile_no in zip(results, mobile_no_list):
            success, response = result
            if not success:
                logger.error(f"Failed to send message to {mobile_no}: {response}")
                return JsonResponse({"status": "failed", "mobile_no": mobile_no, "error": response}, status=500)

        # If all messages are successfully sent, return a success response
        return JsonResponse({"status": "success", "message": "Messages sent successfully."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



def admin_interface(request):
    messages = Message.objects.all()
    msg = []
    mobile_list=[]
    for message in messages:
        msg1 = {
            "sender": message.sender,
            "receiver": message.receiver,
            "content": message.content,
            "timestamp": message.timestamp,
            "status": True,
        }
        msg.append(msg1)
        if message.mobile_no:
            mobile_dict={"mobile_no": message.mobile_no}
            mobile_list.append(mobile_dict)
    return render(request, "admin_interface.html", {"messages": msg,"mobile_dict":mobile_list})