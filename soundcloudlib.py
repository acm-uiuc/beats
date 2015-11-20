import soundcloud
import json
from config import config

sc_client = soundcloud.Client(client_id=config.get('SoundCloud', 'soundcloud_key'))

def get_soundcloud_music_details(url):
    track_obj = sc_client.get('/resolve', url=url)
    track_data = json.loads(track_obj.raw_data)
    return {'title': track_data['title'],
            'length': track_data['duration'] / 1000.,  # reported in milliseconds
            'stream_id': track_data['id'],
            'art_uri': track_data['artwork_url'],
            'artist': track_data['user']['username']}


class SoundCloudMusic(object):
    def __init__(self, packet):
        self.url = packet.stream_url
        self.title = packet.stream_title
        self.length = packet.stream_length
        self.id = packet.stream_id
        self.art_uri = packet.art_uri
        self.uploader = packet.artist

    def mrl(self):
        # get stream url
        stream_obj = sc_client.get('/tracks/{0}/stream'.format(self.id),
                                   allow_redirects=False)
        stream_data = json.loads(stream_obj.raw_data)
        return stream_data['location']

    def dictify(self):
        return {
            'url': self.url,
            'title': self.title,
            'artist': self.uploader,
            'length': self.length,
            'art_uri': self.art_uri,
            'id': self.id
        }
