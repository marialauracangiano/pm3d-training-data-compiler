# src/analytics_pipeline/google_drive/auth.py

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from analytics_pipeline.config.config import get_google_auth_paths
from analytics_pipeline.config.logging_config import logger

SCOPES = ["https://www.googleapis.com/auth/drive"]


def authenticate_google_api() -> Credentials:
    """
    Returns authenticated Google Drive credentials.
    """
    paths = get_google_auth_paths()
    credentials_path = paths["credentials_path"]
    token_path = paths["token_path"]

    logger.info(
        "Using Google credentials from %s",
        credentials_path,
    )

    creds = None

    if token_path.exists():
        logger.info("Loading cached Google credentials.")
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing Google access token.")
            creds.refresh(Request())
        else:
            logger.info("Running Google OAuth flow.")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with token_path.open("w") as token:
            token.write(creds.to_json())

    logger.info("Google Drive authentication successful.")
    return creds
