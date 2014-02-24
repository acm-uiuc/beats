import db
from media import Media
from bson.objectid import ObjectId
from os.path import basename, splitext
from os import walk
import re
from mutagen.mp3 import EasyMP3

class Song(Media):
    def __init__(self, song_id):
        song = db.songs.find_one(ObjectId(song_id))
        if song is None:
            raise Exception('Song does not exist')
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

def add_song(path, title='', artist='', album=''):
    if not title:
        title = splitext(basename(path))[0]
    song = {'title': title, 'artist': artist, 'album': album, 'path': path}
    return str(db.songs.insert(song))

def remove_songs_in_dir(path):
    pattern = re.compile('^%s.*' % path)
    return db.songs.remove({'path': pattern})['n']

def add_songs_in_dir(path, required={"title", "artist", "album"}):
    remove_songs_in_dir(path)
    songs = []
    for root, dirs, files in walk(path):
        for f in files:
            if splitext(f)[1] == ".mp3":
                filepath = root + "/" + f
                mp3 = EasyMP3(filepath)
                values = {}
                for tag in required:
                    try:
                        values[tag] = mp3.tags[tag][0]
                    except Exception:
                        values[tag] = ""
                if not values["title"]:
                    values['title'] = splitext(basename(filepath))[0]
                songs.append({'title': values['title'],
                    'artist': values['artist'],
                    'album': values['album'],
                    'length': mp3.info.length,
                    'path': filepath})
            # TODO Add support for other audio file formats
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
