from config import config
from db import Song, PlayHistory, Session, engine
import art
from os import walk
import hashlib
from os.path import split, splitext, join, isfile
from mutagen.mp3 import EasyMP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import or_, func

PLAYER_NAME = config.get('Player', 'player_name')
ART_DIR = config.get('Artwork', 'art_path')


def remove_songs_in_dir(path):
    session = Session()
    session.query(Song).filter(Song.path.like(path + '%')).delete(
        synchronize_session='fetch')
    session.commit()


def md5_for_file(f, block_size=2**20):
    """Returns MD5 checksum for file.

    Reads the file in chunks to limit memory usage.
    Source: http://stackoverflow.com/a/1131255
    """
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest()


def _prune_dir(path, prune_modified=False):
    """Prunes songs in directory and returns set of remaining songs."""
    session = Session()

    songs = session.query(Song).filter(Song.path.like(path + '%')).all()
    remaining_paths = set()
    for song in songs:
        if not isfile(song.path):
            session.delete(song)
            print 'Pruned (deleted): ' + song.path
            continue

        if prune_modified:
            with open(song.path, 'rb') as f:
                if song.checksum != md5_for_file(f):
                    session.delete(song)
                    print 'Pruned (modified or no checksum): ' + song.path
                    continue
                else:
                    remaining_paths.add(song.path)
        else:
            remaining_paths.add(song.path)

    session.commit()
    return remaining_paths


def add_songs_in_dir(path, store_checksum=False):
    """Update database to reflect the contents of the given directory.

    store_checksum: Whether or not to store an MD5 file checksum in order to
    update the song metadata in the database if the file is modified. Disabled
    by default because it makes scanning a lot slower.
    """
    already_added = _prune_dir(path, prune_modified=store_checksum)
    table = Song.__table__
    conn = engine.connect()
    num_songs = 0
    for root, _, files in walk(path):
        for f in files:
            ext = splitext(f)[1]
            filepath = join(root, f).decode('utf-8')
            if ext in {'.mp3', '.flac', '.ogg', '.m4a', '.mp4'}:
                if filepath in already_added:
                    print 'Already added: ' + filepath
                    continue

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
                    else:
                        title = song.tags['title'][0]
                        artist = song.tags['artist'][0]
                except Exception:
                    print 'Missing tags: ' + filepath
                    continue

                song_obj = {
                    'title': title,
                    'artist': artist,
                    'length': song.info.length,
                    'path': filepath,
                }

                # Calculate and store file checksum
                if store_checksum:
                    with open(filepath, 'rb') as song_file:
                        song_obj['checksum'] = md5_for_file(song_file)

                try: # Album optional for singles
                    if ext in {'.m4a', '.mp4'}:
                        song_obj['album'] = song.tags['\xa9alb'][0]
                    else:
                        song_obj['album'] = song.tags['album'][0]
                except Exception:
                    song_obj['album'] = None

                try: # Track number optional
                    if ext in {'.m4a', '.mp4'}:
                        song_obj['tracknumber'] = song.tags['trkn'][0][0]
                    else:
                        song_obj['tracknumber'] = (
                            int(song.tags['tracknumber'][0]))
                except Exception:
                    song_obj['tracknumber'] = None

                # Album art added on indexing
                if not art.get_art(song_obj['artist'], song_obj['album']):
                    art.index_art(song_obj)

                print 'Added: ' + filepath
                conn.execute(table.insert().values(song_obj))
                num_songs += 1

    conn.close()
    return num_songs


def search_songs(query, limit=20):
    songs = []
    if query:
        session = Session()
        res = session.query(Song).filter(or_(
            Song.title.like('%' + query + '%'),
            Song.artist.like('%' + query + '%'),
            Song.album.like('%' + query + '%')
        )).limit(limit).all()
        session.commit()
        songs = [song.dictify() for song in res]
    return {'query': query, 'limit': limit, 'results': songs}


def random_songs(limit=20):
    session = Session()
    res = session.query(Song).order_by(func.rand()).limit(limit).all()
    session.commit()
    songs = [song.dictify() for song in res]
    return {'query': '', 'limit': limit, 'results': songs}


def get_albums_for_artist(artist):
    songs = Song.__table__
    albums = []
    if artist:
        conn = engine.connect()
        cols = [songs.c.album, func.count(songs.c.album).label('num_songs'), songs.c.artist]
        s = (select(cols)
             .where(songs.c.artist == artist)
             .group_by(songs.c.album)
             .order_by(songs.c.album))
        res = conn.execute(s)
        albums = [{'name': row[0], 'num_songs': row[1], 'art_uri': art.get_art(row[2], row[0])} for row in res]
        conn.close()
    return {'query': artist, 'results': albums}


def get_album(album):
    songs = []
    if album:
        session = Session()
        res = (session.query(Song).filter_by(album=album)
               .order_by(Song.tracknumber, Song.path).all())
        session.commit()
        songs = [song.dictify() for song in res]
    return {'query': album, 'results': songs}

def get_history(limit=20):
    session = Session()
    history_items = (session.query(PlayHistory)
                     .filter_by(player_name=PLAYER_NAME)
                     .order_by(PlayHistory.id.desc()).limit(limit).all())
    session.commit()
    songs = []
    for item in history_items:
        song_obj = session.query(Song).get(item.song_id).dictify()
        song_obj['played_at'] = str(item.played_at)
        songs.append(song_obj)
    return {'limit': limit, 'results': songs}


def top_songs(limit=20):
    songs = Song.__table__
    play_history = PlayHistory.__table__
    conn = engine.connect()
    cols = [songs.c.id, func.count(play_history.c.id).label('play_count')]
    s = (select(cols)
         .select_from(songs.join(play_history))
         .group_by(songs.c.id)
         .order_by('play_count DESC')
         .limit(limit))
    res = conn.execute(s)
    conn.close()
    session = Session()
    songs = [session.query(Song).get(song[0]).dictify() for song in res]
    session.commit()
    return {'limit': limit, 'results': songs}


def top_artists(limit=20):
    songs = Song.__table__
    play_history = PlayHistory.__table__
    conn = engine.connect()
    cols = [songs.c.artist, func.count(play_history.c.id).label('play_count')]
    s = (select(cols)
         .select_from(songs.join(play_history))
         .group_by(songs.c.artist)
         .order_by('play_count DESC')
         .limit(limit))
    res = [{'artist': row[0], 'play_count': row[1]} for row in conn.execute(s)]
    conn.close()
    return {'limit': limit, 'results': res}
