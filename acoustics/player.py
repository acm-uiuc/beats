import vlc

class Player:
    def __init__(self):
        self.instance = vlc.Instance('--no-video')
        self.player = self.instance.media_player_new()

    def play(self, mrl):
        m = self.instance.media_new(mrl)
        self.player.set_media(m)
        self.player.play()
        return self.get_status()

    def pause(self):
        self.player.pause()
        return self.get_status()

    def get_status(self):
        media = self.player.get_media()
        status = {'state': str(self.player.get_state())}
        if media:
            status['media'] = vlc.bytes_to_str(media.get_mrl())
            status['current_time'] = self.player.get_time()
            status['duration'] = media.get_duration()
        else:
            status['media'] = 'none'
        return status

    def get_vlc_version(self):
        return vlc.libvlc_get_version()
