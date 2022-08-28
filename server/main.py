import json
from hashlib import sha256

import httpx
from flask import Flask, redirect, render_template, request, session

from utils import SECRETS_DIR, error, get_logger, merge_params, random_string
from utils import save_bot_token


logger = get_logger(__name__)


AUTH_BASE_URL = 'https://twitter.com/i/oauth2/authorize'
ACCESS_TOKEN_URL = 'https://api.twitter.com/2/oauth2/token'
REDIRECT_URI = 'http://localhost:5000/callback/'

with open(SECRETS_DIR / 'hashed_password') as f:
    MAIN_PASSWORD = f.read()

with open(SECRETS_DIR / 'keys.json') as f:
    SECRETS = json.load(f)


app = Flask(__name__, static_folder='static')
app.secret_key = SECRETS['SECRET_KEY']


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/update_bot/')
def update_bot():
    password = request.args.get('password')

    if (
        not password or
        MAIN_PASSWORD != sha256(str(password).encode()).hexdigest()
    ):
        logger.warn(f'wrong password:\n{password}')
        return error('Invalid Password!')

    state = random_string()
    code_challenge = random_string()

    session['state'] = state
    session['code_challenge'] = code_challenge

    scopes = [
        'users.read', 'offline.access',
        'tweet.read', 'tweet.write'
    ]

    params = {
        'response_type': 'code',
        'client_id': SECRETS['CLIENT_ID'],
        'redirect_uri': REDIRECT_URI,
        'scope': '+'.join(scopes),
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'plain',
    }

    url = merge_params(AUTH_BASE_URL, params)

    return redirect(url)


@app.get('/callback/')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')

    session_state = session.get('state')
    code_challenge = session.get('code_challenge')

    if (not session_state or not code_challenge or state != session_state):
        return error('Invalid Data!')

    headers = {'Authorization': f'Basic {SECRETS["BASIC_TOKEN"]}'}

    params = {
        'grant_type': 'authorization_code',
        'client_id': SECRETS['CLIENT_ID'],
        'code': code,
        'code_verifier': code_challenge,
        'redirect_uri': REDIRECT_URI
    }

    response = httpx.post(ACCESS_TOKEN_URL, params=params, headers=headers)

    if response.status_code != 200:
        return error('Invalid Login!')

    try:
        save_bot_token(response.json())
    except Exception:
        return error('Faild to Save the Info!')

    return redirect('/')
