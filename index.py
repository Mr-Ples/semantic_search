import base64
import os
import traceback
from functools import wraps
from urllib.parse import unquote

import requests
from flask import (
    redirect,
    session,
    Flask,
    render_template,
    request,
)
from requests_oauthlib import OAuth2Session
from flask_caching import Cache

import constants
import dirty_auth
from semantic_search import main as semantic_search

config = {
    "PORT": 8089,
    "HOST": "0.0.0.0",
    "DEBUG": False,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
app.secret_key = os.urandom(24)
cache = Cache(app)

# Set up GitLab OAuth2 configuration
GITLAB_CLIENT_ID = dirty_auth.GITLAB_CLIENT_ID
GITLAB_CLIENT_SECRET = dirty_auth.GITLAB_CLIENT_SECRET
GITLAB_REDIRECT_URI = "https://semantic-search.jprq.live/callback"
GITLAB_AUTHORIZATION_BASE_URL = "https://gitlab.com/oauth/authorize"
GITLAB_TOKEN_URL = "https://gitlab.com/oauth/token"
GITLAB_USER_INFO_URL = "https://gitlab.com/api/v4/user"

# Set up the OAuth2 session
oauth = OAuth2Session(GITLAB_CLIENT_ID, redirect_uri=GITLAB_REDIRECT_URI)


# run_with_lt(
#     app,
#     # subdomain='semantic-search-bro-bro'
# )


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.query_string:
            cache.set("request_path", request.path + '?' + request.query_string.decode('utf-8'))
        else:
            cache.set("request_path", request.path)
        auth_token = session.get('auth_token')
        if auth_token:
            try:
                resp = oauth.get(GITLAB_USER_INFO_URL).json()
            except:
                return redirect("/login")
            if not isinstance(resp, str):
                return f(*args, **kwargs)
            return redirect("/login")
        return redirect("/login")

    return decorated_function


@app.route('/search', methods=['GET', 'POST'])
@token_required
def search():
    def pack_collection(collection = ""):
        collect_data = []
        for collect in constants.COLLECTIONS:
            print(collect, collection, collection in collect)
            if collection.lower().replace(" ", '') in collect.lower().replace(" ", ''):
                collect_data.append((collect, True))
            else:
                collect_data.append((collect, False))
        return collect_data

    print("search", request.method)
    print(request.__dict__)
    print(request.query_string)
    if not request.query_string:
        return render_template('search.html', query='Search', results=cache.get('docs') or {}, nr_results=0, doc_results=cache.get('realtalks') or {}, nr_doc_results=0, collections=pack_collection())
    query = str(request.query_string.decode('ascii')).split('&')[0]
    collection = unquote(str(request.query_string.decode('utf-8')).split('&')[-1])
    query = base64.b64decode(query).decode('ascii')
    print(query, collection.lower().replace(" ", ''))

    if cache.get(request.query_string):
        results, doc_results = cache.get(request.query_string)
    else:
        results, doc_results = semantic_search([query], collection.lower().replace(" ", ''))
        cache.set(request.query_string, (results, doc_results))
        cache.set(collection.lower().replace(" ", ''), (results, doc_results))
    return render_template('search.html', query=query, results=results or cache.get('docs'), nr_results=len(results), doc_results=doc_results or cache.get('realtalks'), nr_doc_results=len(doc_results), collections=pack_collection(collection))


@app.route('/')
@token_required
def root():
    print("Root", request.method)
    print(request.__dict__)
    return render_template('index.html', query="", collections=constants.COLLECTIONS)


@app.route("/login")
def login():
    authorization_url, state = oauth.authorization_url(GITLAB_AUTHORIZATION_BASE_URL)
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    try:
        token = oauth.fetch_token(GITLAB_TOKEN_URL, client_secret=GITLAB_CLIENT_SECRET, authorization_response=request.url.replace("http:", "https:"))
    except:
        traceback.print_exc()
        return redirect("/login")

    user_info = oauth.get(GITLAB_USER_INFO_URL).json()

    # Check if the user is a member of the cos-search project
    user_id = user_info['id']
    try:
        member_response = requests.get(
            "https://gitlab.com/api/v4/projects/{}/members/{}".format(constants.GITLAB_COS_SEARCH_PROJECT_ID, user_id),
            headers={'Authorization': 'Bearer ' + token['access_token']}
        )
    except:
        traceback.print_exc()
        try:
            member_response = requests.get(
                "https://gitlab.com/api/v4/projects/{}/members/{}".format(constants.GILTAB_COS_DOCUMENTATION_PROJECT_ID, user_id),
                headers={'Authorization': 'Bearer ' + token['access_token']}
            )
        except:
            traceback.print_exc()
            return "User not a member of the CoS Search or CoS Documentation projects", 403

    print(member_response)
    if member_response.status_code == 200:
        session['auth_token'] = token
        if cache.get("request_path"):
            return redirect(cache.get("request_path"))
        return redirect("/")
    else:
        try:
            member_response = requests.get(
                "https://gitlab.com/api/v4/projects/{}/members/{}".format(constants.GILTAB_COS_DOCUMENTATION_PROJECT_ID, user_id),
                headers={'Authorization': 'Bearer ' + token['access_token']}
            )
            if member_response.status_code == 200:
                session['auth_token'] = token
                if cache.get("request_path"):
                    return redirect(cache.get("request_path"))
                return redirect("/")
        except:
            traceback.print_exc()
            return "User not a member of the CoS Search or CoS Documentation projects", 403
        return "User not a member of the CoS Search or CoS Documentation projects", 403


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=8089,
        # debug=True,
        # use_reloader=True
    )
