import os
from requests import Request

import streamsync.serve
import streamsync.auth

DOMAINS = os.getenv('AUTH_DOMAINS', '').split(' ')
CLIENT_ID = os.getenv('AUTH_GITHUB_CLIENT_ID', None)
CLIENT_SECRET = os.getenv('AUTH_GITHUB_CLIENT_SECRET', None)

oidc = streamsync.auth.Github(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    host_url=f"https://{os.getenv('APP')}.osc-fr1.scalingo.io/auth_oidc_github"
)

def callback(request: Request, session_id: str, userinfo: dict):
    if userinfo['email'] is None:
        userinfo['email'] = '<N/D for this profile>'

streamsync.serve.register_auth(oidc, callback=callback)
