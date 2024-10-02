"""
This is a simple application to help our team to review contribution.

>>> python apps/reviewapp.py

Runs this application in public and requires authentication.

>>> export HOST=0.0.0.0; export BASICAUTH=admin:admin; python apps/reviewapp.py
"""
import base64
import os
import time
from typing import List

import uvicorn
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles

import writer.serve

HOST = os.getenv('HOST', 'localhost')
PORT = int(os.getenv('PORT', '8000'))
print(f"listen on {HOST}:{PORT}")

# this application is located in ./apps/reviewapp.py
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))


def list_apps() -> List[str]:
    apps_dir = os.path.join(os.path.dirname(__file__))
    apps = []
    for d in os.listdir(apps_dir):
        if os.path.isdir(os.path.join(apps_dir, d)) and os.path.isdir(os.path.join(apps_dir, d, '.wf')):
            apps.append(d.strip('/'))
    return sorted(apps)

def app_path(app_name: str) -> str:
    return os.path.join(os.path.dirname(__file__), app_name)

root_asgi_app = FastAPI(lifespan=writer.serve.lifespan)
root_asgi_app.mount("/storybook", StaticFiles(directory=os.path.join(ROOT_DIR, "src/ui/storybook-static"), html=True), name="storybook")

for app in list_apps():
    sub_asgi_app = writer.serve.get_asgi_app(app_path(app), "edit", enable_remote_edit=True, enable_server_setup=True)
    root_asgi_app.mount(f"/{app}/", sub_asgi_app)


@root_asgi_app.get("/")
async def init():
    links = [f'<li><a href="/{a}">{a}</a></li>' for a in list_apps()]
    links += [f'<li><a href="/storybook/index.html">storybook</a></li>']

    return HTMLResponse("""
        <h1>Writer review app</h1>
        <ul>
        """ + "\n".join(links) + """
        </ul>
        """, status_code=200)



@root_asgi_app.middleware("http")
async def valid_authentication(request, call_next):
    """
    Secures access to the review application using basic auth

    The username and password is stored in the BASICAUTH environment variable.
    The authentication process is sequential and when it's wrong it take one second to try again. This protection
    is sufficient to limit brute force attack.
    """
    if HOST == 'localhost':
        """
        Locally, you can launch the review application without needing to authenticate.
        
        The application bypass the authentication middleware.
        """
        return await call_next(request)

    _auth = request.headers.get('Authorization')
    if not check_permission(_auth):
        return HTMLResponse("", status.HTTP_401_UNAUTHORIZED, {"WWW-Authenticate": "Basic"})
    return await call_next(request)


def check_permission(auth) -> bool:
    """
    Secures access to the review application using basic auth

    >>> is_valid_token = check_permission('Basic dXNlcm5hbWU6cGFzc3dvcmQ=')
    """
    if auth is None:
        return False

    scheme, data = (auth or ' ').split(' ', 1)
    if scheme != 'Basic':
        return False

    username, password = base64.b64decode(data).decode().split(':', 1)
    basicauth = os.getenv('BASICAUTH')
    if auth is None:
        raise ValueError('BASICAUTH environment variable is not set')

    basicauth_part = basicauth.split(':')
    if len(basicauth_part) != 2:
        raise ValueError('BASICAUTH environment variable is not set')

    basicauth_username, basicauth_password = basicauth_part

    if username == basicauth_username and password == basicauth_password:
        return True
    else:
        time.sleep(1)
        return False


uvicorn.run(root_asgi_app,
    host=HOST,
    port=PORT,
    log_level="warning",
    ws_max_size=writer.serve.MAX_WEBSOCKET_MESSAGE_SIZE,
    reload=False,
    workers=1)