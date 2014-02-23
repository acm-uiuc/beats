from media import Media

class YTVideo(Media):
    def __init__(self, url):
        self.url = url
        self.title = 'Video'

    def mrl(self):
        return self.url

    def dictify(self):
        return {'url': self.url, 'title': self.title}

    def __eq__(self, other):
        return other is not None and self.url == other.url
