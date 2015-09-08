from flask import Flask, request, jsonify, Response
from gevent.wsgi import WSGIServer
from functools import wraps
from crossdomain import crossdomain
from scheduler import Scheduler
from config import config
import song
import player
import user

AUTHENTICATION_ENABLED = config.getboolean('Authentication', 'enabled')
if not AUTHENTICATION_ENABLED:
    TEST_USERNAME = config.get('Authentication', 'test_username')

app = Flask(__name__)
#app.debug = True

scheduler = Scheduler()
scheduler.start()


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


@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': str(error)}), 404


@app.errorhandler(500)
def not_found(error):
    return jsonify({'message': str(error)}), 500


@app.route('/v1/player/play_next', methods=['POST'])
@login_required
@crossdomain(origin='*')
def play_next():
    return jsonify(scheduler.play_next(skip=True) or {})


@app.route('/v1/player/pause', methods=['POST'])
@login_required
@crossdomain(origin='*')
def pause():
    return jsonify(player.pause())


@app.route('/v1/player/volume', methods=['POST'])
@login_required
@crossdomain(origin='*')
def player_set_volume():
    if request.form.get('volume'):
        vol = int(request.form.get('volume'))
        if 0 <= vol <= 100:
            return jsonify(player.set_volume(vol))
        else:
            return jsonify({
                'message': 'Volume must be between 0 and 100',
            }), 400
    return jsonify({'message': 'No volume parameter'}), 400


@app.route('/v1/songs/<song_id>', methods=['GET'])
@crossdomain(origin='*')
def show_song(song_id):
    try:
        return jsonify(song.Song(song_id).dictify())
    except Exception, e:
        return jsonify({'message': str(e)}), 404


@app.route('/v1/songs/search', methods=['GET'])
@crossdomain(origin='*')
def search():
    query = request.args.get('q')
    if query.startswith('album:'):
        return jsonify(song.get_album(query[6:].lstrip()))
    elif query.startswith('artist:'):
        return jsonify(song.get_albums_for_artist(query[7:].lstrip()))
    elif query.startswith('play-history'):
        try:
            limit = int(query[13:])
            return jsonify(song.get_history(limit=limit))
        except ValueError:
            return jsonify(song.get_history())
    elif query.startswith('top-songs'):
        try:
            limit = int(query[10:])
            return jsonify(song.top_songs(limit=limit))
        except ValueError:
            return jsonify(song.top_songs())
    else:
        limit = request.args.get('limit')
        if limit and int(limit) != 0:
            return jsonify(song.search_songs(query, limit=int(limit)))
        return jsonify(song.search_songs(query))


@app.route('/v1/songs/random', methods=['GET'])
@crossdomain(origin='*')
def random_songs():
    limit = request.args.get('limit')
    if limit and int(limit) != 0:
        return jsonify(song.random_songs(limit=int(limit)))
    return jsonify(song.random_songs())


@app.route('/v1/songs/history', methods=['GET'])
@crossdomain(origin='*')
def get_history():
    limit = request.args.get('limit')
    if limit and int(limit) != 0:
        return jsonify(song.get_history(limit=int(limit)))
    return jsonify(song.get_history())


@app.route('/v1/songs/top_songs', methods=['GET'])
@crossdomain(origin='*')
def top_songs():
    limit = request.args.get('limit')
    if limit and int(limit) != 0:
        return jsonify(song.top_songs(limit=int(limit)))
    return jsonify(song.top_songs())


@app.route('/v1/songs/top_artists', methods=['GET'])
@crossdomain(origin='*')
def top_artists():
    limit = request.args.get('limit')
    if limit and int(limit) != 0:
        return jsonify(song.top_artists(limit=int(limit)))
    return jsonify(song.top_artists())


@app.route('/v1/queue', methods=['GET'])
@crossdomain(origin='*')
def show_queue():
    queue_user = request.args.get('user')
    if queue_user:
        return jsonify(scheduler.get_queue(user=queue_user))
    return jsonify(scheduler.get_queue())


@app.route('/v1/queue/<int:song_id>', methods=['DELETE'])
@login_required
@crossdomain(origin='*')
def queue_remove(song_id):
    return jsonify(scheduler.remove_song(song_id))


@app.route('/v1/queue', methods=['DELETE'])
@login_required
@crossdomain(origin='*')
def queue_clear():
    return jsonify(scheduler.clear())


@app.route('/v1/queue/add', methods=['POST'])
@login_required
@crossdomain(origin='*')
def queue_add():
    token = request.form.get('token')
    if not AUTHENTICATION_ENABLED:
        username = TEST_USERNAME
    else:
        session = user.get_session(token)
        username = session.json()['user']['name']
    if request.form.get('id'):
        try:
            song_id = int(request.form.get('id'))
        except ValueError:
            return jsonify({'message': 'Invalid id'}), 400
        try:
            return jsonify(scheduler.vote_song(username, song_id=song_id))
        except Exception, e:
            return jsonify({'message': str(e)}), 400
    elif request.form.get('url'):
        url = request.form.get('url')
        try:
            return jsonify(scheduler.vote_song(username, video_url=url))
        except Exception, e:
            return jsonify({'message': str(e)}), 400
    elif request.form.get('scurl'):  # soundcloud url
        scurl = request.form.get('scurl')
        try:
            return jsonify(scheduler.vote_song(username, soundcloud_url=scurl))
        except Exception, e:
            return jsonify({'message': str(e)}), 400
    return jsonify({'message': 'No id or url parameter'}), 400


@app.route('/v1/now_playing', methods=['GET'])
@crossdomain(origin='*')
def now_playing():
    return jsonify(player.get_now_playing() or {})


@app.route('/v1/session', methods=['POST'])
@crossdomain(origin='*')
def create_session():
    """Login.

    For Crowd SSO support, save the token in a cookie with name
    'crowd.token_key'.
    """
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


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


if __name__ == '__main__':
    print 'Beats by ACM'
    print 'VLC version: ' + player.get_vlc_version()
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
