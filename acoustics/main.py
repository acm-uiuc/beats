from flask import Flask, request, jsonify, Response
from functools import wraps
from crossdomain import crossdomain
from song import Song, search_songs
from youtube import YTVideo
from queue import Queue
from config import config
import player
import user

AUTHENTICATION_ENABLED = config.getboolean('Authentication', 'enabled')

app = Flask(__name__)
app.debug = True

queue = Queue()

def login_required(f):
    if not AUTHENTICATION_ENABLED:
        return f

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.form.get('token')
        if token is None:
            return jsonify({'message': 'No SSO token provided'}), 401
        if not user.valid_session(token):
            return jsonify({'message': 'Invalid SSO token: ' + token}), 401
        return f(*args, **kwargs)

    return decorated_function

@app.route('/v1/player/play_next', methods=['POST'])
@login_required
@crossdomain(origin='*')
def play_next():
    return jsonify(queue.play_next(force=True) or {})

@app.route('/v1/player/pause', methods=['POST'])
@login_required
@crossdomain(origin='*')
def pause():
    return jsonify(player.pause())

@app.route('/v1/player/status', methods=['GET'])
@crossdomain(origin='*')
def player_status():
    return jsonify(player.get_status())

@app.route('/v1/songs/<song_id>', methods=['GET'])
@crossdomain(origin='*')
def show_song(song_id):
    try:
        return jsonify(Song(song_id).dictify())
    except Exception, e:
        return jsonify({'message': str(e)}), 404

@app.route('/v1/songs/search', methods=['GET'])
@crossdomain(origin='*')
def search():
    query = request.args.get('q')
    limit = request.args.get('limit')
    if limit and int(limit) != 0:
        return jsonify(search_songs(query, int(limit)))
    return jsonify(search_songs(query))


@app.route('/v1/queue', methods=['GET'])
@crossdomain(origin='*')
def show_queue():
    return jsonify(queue.get_queue())

@app.route('/v1/queue/<int:pos>', methods=['DELETE'])
@login_required
@crossdomain(origin='*')
def queue_remove(pos):
    return jsonify(queue.remove(pos))

@app.route('/v1/queue', methods=['DELETE'])
@login_required
@crossdomain(origin='*')
def queue_clear():
    return jsonify(queue.clear())

@app.route('/v1/queue/add', methods=['POST'])
@login_required
@crossdomain(origin='*')
def queue_add():
    if request.form.get('id'):
        song_id = request.form.get('id')
        try:
            return jsonify(queue.add(Song(song_id)))
        except Exception, e:
            return jsonify({'message': str(e)}), 404
    elif request.form.get('url'):
        url = request.form.get('url')
        return jsonify(queue.add(YTVideo(url)))
    return jsonify({'message': 'No id or url parameter'}), 400

@app.route('/v1/now_playing', methods=['GET'])
@crossdomain(origin='*')
def now_playing():
    return jsonify(queue.now_playing() or {})

@app.route('/v1/user', methods=['GET'])
@crossdomain(origin='*')
def get_user():
    r = user.get_user()
    return jsonify(r.json()), r.status_code

@app.route('/v1/session', methods=['POST'])
@crossdomain(origin='*')
def create_session():
    """For Crowd SSO support, save the token in a cookie with name 'crowd.token_key'."""
    username = request.form.get('username')
    password = request.form.get('password')
    r = user.create_session(username, password)
    return jsonify(r.json()), r.status_code

@app.route('/v1/session/<token>', methods=['GET'])
@crossdomain(origin='*')
def get_session(token):
    r = user.get_session(token)
    return jsonify(r.json()), r.status_code

@app.route('/v1/session/<token>', methods=['DELETE'])
@crossdomain(origin='*')
def delete_session(token):
    r = user.delete_session(token)
    return Response(status=r.status_code)

if __name__ == '__main__':
    print 'Acoustics Media Player'
    print 'VLC version: ' + player.get_vlc_version()
    queue.start_autoplay()
    app.run()
