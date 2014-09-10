import pafy
import isodate

def get_youtube_video_details(url):
    try:
        video = pafy.new(url)
    except IOError:
        raise Exception('Bad video url')

    return {'title': video.title, 'length': video.length}

def get_art_uri(url):
    videoid = url.split('?v=')[1]
    uri = "http://img.youtube.com/vi/" + videoid + "/0.jpg"
    return uri


class YouTubeVideo(object):
    def __init__(self, packet):
        self.url = packet.video_url
        self.title = packet.video_title
        self.length = packet.video_length

    def mrl(self):
        video = pafy.new(self.url)
        return video.audiostreams[0].url

    def dictify(self):
        return {'url': self.url,
                'title': self.title,
                'artist': 'YouTube video',
                'length': self.length,
                'art_uri': get_art_uri(self.url)}
