import pafy
import isodate
from urlparse import parse_qs, urlparse

def get_youtube_video_details(url):
    try:
        video = pafy.new(url)
    except IOError:
        raise Exception('Bad video url')

    return {'title': video.title, 'length': video.length}


class YouTubeVideo(object):
    def __init__(self, packet):
        self.url = packet.video_url
        self.title = packet.video_title
        self.length = packet.video_length

    def mrl(self):
        video = pafy.new(self.url)
        return video.audiostreams[0].url

    def dictify(self):
        youtube_id = parse_qs(urlparse(self.url).query)['v'][0] 
        return {'url': self.url,
                'title': self.title,
                'artist': 'YouTube video',
                'length': self.length,
                'art_uri': 'http://img.youtube.com/vi/' + youtube_id + '/hqdefault.jpg'}
