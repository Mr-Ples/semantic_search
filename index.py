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
        return f(*args, **kwargs)
        #     return redirect("/login")
        # return redirect("/login")

    return decorated_function


@app.route('/search', methods=['GET', 'POST'])
@token_required
def search():
    print("search", request.method)
    print(request.__dict__)
    print(request.query_string)

    datas = {collect.lower().replace(" ", ''): cache.get(collect.lower().replace(" ", '')) or {} for collect in constants.COLLECTIONS}
    [datas[collect.lower().replace(" ", '')].update({'selected': False, 'col_id': collect.lower().replace(" ", ''), 'col_name': collect, 'tab_id': collect.lower().replace(" ", '') + "y"}) for collect in constants.COLLECTIONS]

    if not request.query_string:
        return render_template('search.html', collections=[datas.get(collect.lower().replace(" ", '')) for collect in constants.COLLECTIONS], query="")

    query = str(request.query_string.decode('ascii')).split('&')[0]
    collection = unquote(str(request.query_string.decode('utf-8')).split('&')[-1])
    selected_collection = collection.lower().replace(" ", '')
    query = base64.b64decode(query).decode('ascii')
    print(query, selected_collection)

    if cache.get(request.query_string):
        datas[selected_collection] = cache.get(request.query_string)
    else:
        results, doc_results = semantic_search([query], selected_collection)
        datas[selected_collection].update(dict(query=query, results=results, nr_results=len(results), doc_results=doc_results, selected=True))
        cache.set(selected_collection, datas[selected_collection])
        cache.set(request.query_string, datas[selected_collection])

    return render_template('search.html', collections=[datas.get(collect.lower().replace(" ", '')) for collect in constants.COLLECTIONS], query=query)


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
