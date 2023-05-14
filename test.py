import os
from flask import (
    request,
    render_template,
    Flask,
    redirect,
    session,
)
from requests_oauthlib import OAuth2Session

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Set up GitLab OAuth2 configuration
GITLAB_CLIENT_ID = os.environ.get("GITLAB_CLIENT_ID")
GITLAB_CLIENT_SECRET = os.environ.get("GITLAB_CLIENT_SECRET")
GITLAB_REDIRECT_URI = "https://mr-ples.jprq.live/callback"
GITLAB_AUTHORIZATION_BASE_URL = "https://gitlab.com/oauth/authorize"
GITLAB_TOKEN_URL = "https://gitlab.com/oauth/token"
GITLAB_USER_INFO_URL = "https://gitlab.com/api/v4/user"

# Set up the OAuth2 session
oauth = OAuth2Session(GITLAB_CLIENT_ID, redirect_uri=GITLAB_REDIRECT_URI)

from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token = session.get('auth_token')
        if auth_token:
            resp = oauth.get(GITLAB_USER_INFO_URL).json()
            if not isinstance(resp, str):
                return f(*args, **kwargs)
            return redirect("/login")
        return redirect("/login")

    return decorated_function


@app.route("/")
@token_required
def index():
    return render_template("index.html")


@app.route("/login")
def login():

    authorization_url, state = oauth.authorization_url(GITLAB_AUTHORIZATION_BASE_URL)
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    token = oauth.fetch_token(GITLAB_TOKEN_URL, client_secret=GITLAB_CLIENT_SECRET, authorization_response=request.url.replace("http:", "https:"))
    session['auth_token'] = token
    user_info = oauth.get(GITLAB_USER_INFO_URL).json()
    return render_template("index.html", user_info=user_info)


if __name__ == "__main__":
    app.run(port=5005, debug=False)
