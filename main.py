import os, json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def get_youtube():
    TOKEN_JSON = os.environ.get("TOKEN_JSON")
    creds = Credentials.from_authorized_user_info(json.loads(TOKEN_JSON))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)