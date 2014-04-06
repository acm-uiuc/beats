from db import Song, PlayHistory, Session, engine
from os import walk
from os.path import splitext, join
from mutagen.mp3 import EasyMP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import or_, func

def remove_songs_in_dir(path):
    session = Session()
    session.query(Song).filter(Song.path.like(path + '%')).delete(synchronize_session='fetch')
    session.commit()

def add_songs_in_dir(path):
    remove_songs_in_dir(path)
    table = Song.__table__
    conn = engine.connect()
    num_songs = 0
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
                    else:
                        title = song.tags['title'][0]
                        artist = song.tags['artist'][0]
                except Exception:
                    print 'Skipped: ' + filepath
                    continue

                song_obj = {'title': title,
                    'artist': artist,
                    'length': song.info.length,
                    'path': filepath}

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
                        song_obj['tracknumber'] = int(song.tags['tracknumber'][0])
                except Exception:
                    song_obj['tracknumber'] = None

                print filepath
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
            Song.album.like('%' + query + '%'))) \
                    .limit(limit).all()
        session.commit()
        songs = [song.dictify() for song in res]
    return {'query': query, 'limit': limit, 'results': songs}

def random_songs(limit=20):
    session = Session()
    res = session.query(Song).order_by(func.rand()).limit(limit).all()
    session.commit()
    songs = [song.dictify() for song in res]
    return {'query': '', 'limit': limit, 'results': songs}

def get_album(album):
    songs = []
    if album:
        session = Session()
        res = session.query(Song).filter_by(album=album).order_by(Song.tracknumber, Song.path).all()
        session.commit()
        songs = [song.dictify() for song in res]
    return {'query': album, 'results': songs}

def get_history(limit=20):
    session = Session()
    history_items = session.query(PlayHistory).order_by(PlayHistory.id.desc()).limit(limit).all()
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
    s = select([songs.c.id, func.count(play_history.c.id).label('play_count')]) \
            .select_from(songs.join(play_history)) \
            .group_by(songs.c.id) \
            .order_by('play_count DESC') \
            .limit(limit)
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
    s = select([songs.c.artist, func.count(play_history.c.id).label('play_count')]) \
            .select_from(songs.join(play_history)) \
            .group_by(songs.c.artist) \
            .order_by('play_count DESC') \
            .limit(limit)
    res = [{'artist': row[0], 'play_count': row[1]} for row in conn.execute(s)]
    conn.close()
    return {'limit': limit, 'results': res}
