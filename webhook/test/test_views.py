import os
from django.conf import settings
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE","whatsapp_webhook.settings")
django.setup()

from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
import pytest


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def valid_data():
    return  {
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "457525804121298",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15551828990",
              "phone_number_id": "551602171364742"
            },
            "statuses": [
              {
                "id": "wamid.HBgMOTE4MjY1MDU3NDY0FQIAERgSMzRFNjc5OTc3RUZENTA2NUJBAA==",
                "status": "sent",
                "timestamp": "1735035178",
                "recipient_id": "918265057464",
                "conversation": {
                  "id": "6bf4c358fc3f286834e3d51b9b818bc1",
                  "expiration_timestamp": "1735117800",
                  "origin": {
                    "type": "service"
                  }
                },
                "pricing": {
                  "billable": True,
                  "pricing_model": "CBP",
                  "category": "service"
                }
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}

def test_webhook_wrong_response(client):
    url=reverse("webhook")
    response=client.get(url)

    assert response.status_code==status.HTTP_403_FORBIDDEN



def test_webhook_receive_data(client,valid_data):
    url=reverse("webhook")
    response=client.post(url,valid_data,format="json")
    assert response.status_code==status.HTTP_200_OK


@pytest.fixture
def valid_data_for_sending():
    return {
        "mobile":918265057464,
        "msg":["hello"]
    }

def test_webhook_send_data(client,valid_data_for_sending):
    url=reverse("reply_to_user")

    response=client.post(url,valid_data_for_sending,format="multipart")
    assert response.status_code==status.HTTP_200_OK


def test_admin_interface(client):
    url=reverse("admin_interface")
    response=client.get(url)