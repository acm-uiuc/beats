import vlc
from song import get_song, urlify

instance = vlc.Instance('--no-video')
player = instance.media_player_new()
now_playing = None

def play(mrl):
    m = instance.media_new(mrl)
    player.set_media(m)
    player.play()
    return get_status()

def play_id(song_id):
    song = get_song(song_id)
    if song:
        return play_song(song)
    return get_status()

def play_song(song):
    play(urlify(song['path']))
    global now_playing
    now_playing = song
    return get_status()

def pause():
    player.pause()
    return get_status()

def stop():
    player.stop()
    now_playing = None
    return get_status()

def get_status():
    media = player.get_media()
    status = {'state': str(player.get_state())}
    if media:
        status['media'] = vlc.bytes_to_str(media.get_mrl())
        status['current_time'] = player.get_time()
        status['duration'] = media.get_duration()
    else:
        status['media'] = 'none'
    return status

def get_vlc_version():
    return vlc.libvlc_get_version()
