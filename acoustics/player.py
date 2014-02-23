import vlc
from song import Song, urlify

instance = vlc.Instance('--no-video')
player = instance.media_player_new()
now_playing = None

def play(mrl):
    m = instance.media_new(mrl)
    player.set_media(m)
    player.play()
    return get_status()

def play_id(song_id):
    song = Song(song_id)
    if song:
        return play_song(song)
    return get_status()

def play_media(media):
    play(media.mrl())
    global now_playing
    now_playing = media
    return get_status()

def pause():
    player.pause()
    return get_status()

def stop():
    player.stop()
    global now_playing
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
