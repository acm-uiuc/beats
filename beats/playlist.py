from db import Playlist, PlaylistItem, Song, Session, engine
from sqlalchemy.sql import select

def create_playlist(user, name):
    session = Session()
    playlist = Playlist(user=user, name=name)
    session.add(playlist)
    session.commit()
    return get_playlist(playlist.id)

def get_playlists_for_user(user):
    playlists = Playlist.__table__
    conn = engine.connect()
    s = select([playlists.c.id, playlists.c.name]) \
            .where(playlists.c.user == user) \
            .order_by(playlists.c.name)
    res = [{'id': row[0], 'name': row[1]} for row in conn.execute(s)]
    conn.close()
    return {'user': user, 'playlists': res}

def get_playlist(playlist_id):
    session = Session()
    playlist = session.query(Playlist).get(playlist_id)
    songs = session.query(Song) \
            .join(PlaylistItem) \
            .filter(PlaylistItem.playlist_id == playlist_id) \
            .order_by(PlaylistItem.index).all()
    session.commit()
    songs_list = [song.dictify() for song in songs]
    return {'id': playlist_id, 'user': playlist.user, 'name': playlist.name, 'songs': songs_list}

def rename_playlist(playlist_id, new_name):
    session = Session()
    playlist = session.query(Playlist).get(playlist_id)
    playlist.name = new_name
    session.commit()
    return get_playlist(playlist_id)

def add_song_to_playlist(playlist_id, song_id):
    session = Session()
    append_index = session.query(PlaylistItem) \
            .filter_by(playlist_id=playlist_id) \
            .count()
    item = PlaylistItem(playlist_id=playlist_id, song_id=song_id, index=append_index)
    session.add(item)
    session.commit()
    return get_playlist(playlist_id)
