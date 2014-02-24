import db
from media import Media
from bson.objectid import ObjectId
from os.path import basename, splitext
from os import walk
import re
from mutagen.easyid3 import EasyID3FileType

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
    db.songs.remove({'path': {'$regex':'^%s.*' % path}})

def add_songs_in_dir(path, required={"title", "artist", "album"}):
    remove_songs_in_dir(path)
    metadata = EasyID3FileType()
    songs = []
    filepath = ""
    values = {}
    for root, dirs, files in walk(path):
        for mp3 in files:
            if splitext(mp3)[1] == ".mp3":
                filepath = root + "/" + mp3
                metadata.load(filepath)
                for tag in required:
                    try:
                        values[tag] = metadata[tag][0]
                    except:
                        values[tag] = ""
                if not values["title"]:
                    values['title'] = splitext(basename(filepath))[0]
                songs.append({'title': values['title'],
                    'artist': values['artist'],
                    'album': values['album'],
                    'path': filepath})
    db.songs.insert(songs)
    return len(songs)
