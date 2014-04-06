from config import config
from urlparse import urlparse, parse_qs
import requests
import isodate

YOUTUBE_API_KEY = config.get('YouTube', 'api_key')

def get_youtube_video_details(url):
    parsed_url = urlparse(url)
    try:
        video_id = parse_qs(parsed_url.query)['v']
        payload = {'part': 'snippet,contentDetails', 'id': video_id, 'key': YOUTUBE_API_KEY}
        details = requests.get('https://www.googleapis.com/youtube/v3/videos', params=payload).json()
        title = details['items'][0]['snippet']['title']
        length = isodate.parse_duration(details['items'][0]['contentDetails']['duration']).total_seconds()
        return {'title': title, 'length': length}
    except (KeyError, IndexError):
        raise Exception('Bad video url')

class YouTubeVideo(object):
    def __init__(self, packet):
        self.url = packet.video_url
        self.title = packet.video_title
        self.length = packet.video_length

    def mrl(self):
        return self.url

    def dictify(self):
        return {'url': self.url,
                'title': self.title,
                'artist': 'YouTube video',
                'length': self.length}
