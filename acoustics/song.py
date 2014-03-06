import db
from media import Media
from bson.objectid import ObjectId
from os import walk
from os.path import splitext, join
import re
from mutagen.mp3 import EasyMP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4

class Song(Media):
    def __init__(self, song_id):
        try:
            song = db.songs.find_one(ObjectId(song_id))
        except Exception:
            raise
        if song is None:
            raise Exception('Song does not exist: ' + song_id)
        song['_id'] = str(song['_id'])
        self.song = song

    def mrl(self):
        return urlify(self.song['path'])

    def dictify(self):
        return self.song

    def __eq__(self, other):
        return other is not None and self.song['_id'] == other.song['_id']

def urlify(path):
    return 'file://' + path

def pathify(mrl):
    return re.sub(r'^file://', '', mrl)

def remove_songs_in_dir(path):
    pattern = re.compile('^%s.*' % path)
    return db.songs.remove({'path': pattern})['n']

def add_songs_in_dir(path):
    remove_songs_in_dir(path)
    songs = []
    for root, _, files in walk(path):
        for f in files:
            ext = splitext(f)[1]
            filepath = join(root, f)
            if ext in {'.mp3', '.flac', '.ogg', '.m4a', '.mp4'}:
                try:
                    if ext == '.mp3':
                        song = EasyMP3(filepath)
                    elif ext == '.flac':
                        song = FLAC(filepath)
                    elif ext == '.ogg':
                        song = OggVorbis(filepath)
                    elif ext in {'.m4a', '.mp4'}:
                        song = MP4(filepath)
                except IOError, e:
                    print e
                    continue

                # Required tags
                try:
                    if ext in {'.m4a', '.mp4'}:
                        title = song.tags['\xa9nam'][0]
                        artist = song.tags['\xa9ART'][0]
                        album = song.tags['\xa9alb'][0]
                    else:
                        title = song.tags['title'][0]
                        artist = song.tags['artist'][0]
                        album = song.tags['album'][0]
                except Exception:
                    print 'Skipped: ' + filepath
                    continue

                song_obj = {'title': title,
                    'artist': artist,
                    'album': album,
                    'length': song.info.length,
                    'path': filepath}

                try:
                    if ext in {'.m4a', '.mp4'}:
                        song_obj['tracknumber'] = song.tags['trkn'][0][0]
                    else:
                        song_obj['tracknumber'] = int(song.tags['tracknumber'][0])
                except Exception:
                    pass

                songs.append(song_obj)
    if not songs:
        return 0
    db.songs.insert(songs)
    return len(songs)

def search_songs(query, limit=20):
    songs = []
    if query:
        pattern = re.compile('.*%s.*' % query, re.IGNORECASE)
        res = db.songs.find(
                {"$or":[
                    {"title": pattern},
                    {"artist": pattern},
                    {"album": pattern}
                    ]
                    }
                ).limit(limit)
        for song in res:
            song['_id'] = str(song['_id'])
            songs.append(song)
    return {'query': query, 'limit': limit, 'results': songs}
