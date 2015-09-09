import pafy
from urlparse import parse_qs, urlparse


def get_youtube_video_details(url):
    try:
        video = pafy.new(url)
    except IOError:
        raise Exception('Bad video url')

    try:
        video.audiostreams[0].url
    except IndexError:
        raise Exception('Invalid video, potentially live stream')

    youtube_id = parse_qs(urlparse(url).query)['v'][0]
    art_uri = 'https://img.youtube.com/vi/' + youtube_id + '/hqdefault.jpg'

    return {'title': video.title, 'length': video.length, 'stream_id': youtube_id, 'art_uri': art_uri}


class YouTubeVideo(object):
    def __init__(self, packet):
        self.url = packet.stream_url
        self.title = packet.stream_title
        self.length = packet.stream_length
        self.id = packet.stream_id
        self.art_uri = packet.art_uri

    def mrl(self):
        video = pafy.new(self.url)
        return video.audiostreams[0].url

    def dictify(self):
        return {
            'url': self.url,
            'title': self.title,
            'artist': 'YouTube video',
            'length': self.length,
            'art_uri': self.art_uri,
            'id': self.id
        }
