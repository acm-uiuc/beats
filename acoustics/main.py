from flask import Flask, request, jsonify
import player

app = Flask(__name__)
app.debug = True

@app.route('/v1/player/play', methods=['PUT'])
def play():
    mrl = request.args.get('mrl')
    return jsonify(player.play(mrl))

@app.route('/v1/player/pause', methods=['PUT'])
def pause():
    return jsonify(player.pause())

@app.route('/v1/player/status', methods=['GET'])
def player_status():
    return jsonify(player.get_status())

if __name__ == '__main__':
    print 'Acoustics Media Player'
    print 'VLC version: ' + player.get_vlc_version()
    app.run()
