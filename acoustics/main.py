from flask import Flask, request, jsonify
from song import get_song
import player

app = Flask(__name__)
app.debug = True

@app.route('/v1/player/play', methods=['PUT'])
def play():
    song_id = request.args.get('id')
    return jsonify(player.play_id(song_id))

@app.route('/v1/player/pause', methods=['PUT'])
def pause():
    return jsonify(player.pause())

@app.route('/v1/player/status', methods=['GET'])
def player_status():
    return jsonify(player.get_status())

@app.route('/v1/songs/<song_id>')
def show_song(song_id):
    song = get_song(song_id)
    return jsonify(song or {})

if __name__ == '__main__':
    print 'Acoustics Media Player'
    print 'VLC version: ' + player.get_vlc_version()
    app.run()
