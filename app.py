from os import environ as env

from flask import Flask, request, url_for, session, redirect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

app = Flask(__name__)

app.secret_key = env.get('SECRET_KEY')
app.config['SESSION_COOKIE_NAME'] = 'projects cookie'

@app.route('/')
def index():
    spoti_oauth = create_spotify_oauth()
    auth_url = spoti_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redir')
def redir():
    spoti_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = spoti_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('getTopSongs', _external=True))

@app.route('/getTopSongs')
def getTopSongs():
    try:
        token_info = get_token()
    except:
        return redirect('/')
    sp = spotipy.Spotify(auth=token_info['access_token'])
    return sp.current_user_playlists(limit=50, offset=0)['items']

def get_token():
    token_info = session.get('token_info', None)
    if not token_info:
        raise 'Exception'
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        spoti_oauth = create_spotify_oauth()
        token_info = spoti_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

# always try to create a new auth when trying to use it
def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=env.get('CLIENT_ID'),
        client_secret=env.get('CLIENT_SECRET'),
        redirect_uri=url_for('redir', _external=True),
        scope='playlist-read-collaborative'
    )

if __name__ == '__main__':
    app.run()
