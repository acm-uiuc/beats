import vlc

instance = vlc.Instance('--no-video')
player = instance.media_player_new()

def play(mrl):
    m = instance.media_new(mrl)
    player.set_media(m)
    player.play()
    return get_status()

def pause():
    player.pause()
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
