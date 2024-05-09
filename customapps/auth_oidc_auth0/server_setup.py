import os
from requests import Request

import streamsync.serve
import streamsync.auth

DOMAINS = os.getenv('AUTH_DOMAINS', '').split(' ')
CLIENT_ID = os.getenv('AUTH_AUTH0_CLIENT_ID', None)
CLIENT_SECRET = os.getenv('AUTH_AUTH0_CLIENT_SECRET', None)
AUTH0_DOMAIN = os.getenv('AUTH_AUTH0_DOMAIN', None)

oidc = streamsync.auth.Auth0(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    domain=AUTH0_DOMAIN,
    host_url=f"https://{os.getenv('APP')}.osc-fr1.scalingo.io/auth_oidc_auth0"
)

def callback(request: Request, session_id: str, userinfo: dict):
    authorized = False
    for domain in DOMAINS:
        if userinfo['email'].endswith(domain):
            authorized = True
            break

    if not authorized:
        raise streamsync.auth.Unauthorized()

streamsync.serve.register_auth(oidc, callback=callback)
