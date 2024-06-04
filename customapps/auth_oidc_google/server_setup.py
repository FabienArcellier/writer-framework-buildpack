import os
from requests import Request

import writer.serve
import writer.auth

DOMAINS = os.getenv('AUTH_DOMAINS', '').split(' ')
CLIENT_ID = os.getenv('AUTH_GOOGLE_CLIENT_ID', None)
CLIENT_SECRET = os.getenv('AUTH_GOOGLE_CLIENT_SECRET', None)

oidc = writer.auth.Google(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    host_url=f"https://{os.getenv('APP')}.osc-fr1.scalingo.io/auth_oidc_google"
)

def callback(request: Request, session_id: str, userinfo: dict):
    authorized = False
    for domain in DOMAINS:
        if userinfo['email'].endswith(domain):
            authorized = True
            break

    if not authorized:
        raise writer.auth.Unauthorized()

writer.serve.register_auth(oidc, callback=callback)
