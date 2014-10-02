from os.path import join, splitext
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from config import config

ART_DIR = config.get('Artwork', 'art_path')


def index_art(song):
    ext = splitext(song['path'])[1]

    art_uri = ''
    if ext == '.mp3':
        art_uri = index_mp3_art(song)
    elif ext == '.flac':
        art_uri = index_flac_art(song)

    return art_uri


def index_mp3_art(song):
    try:
        tags = MP3(song['path'])
    except:
        return False
    data = ''
    for tag in tags:
        if tag.startswith('APIC'):
            data = tags[tag].data
            break

    path = write_art(song, data)

    return path


def index_flac_art(song):
    try:
        tags = FLAC(song['path'])
    except:
        return False
    data = ''
    if tags.pictures[0].data:
        data = tags.pictures[0].data

    path = write_art(song, data)

    return path


def write_art(song, data):
    if not data:
        return None

    filepath = get_art(song['checksum'])

    out = open(filepath, 'w')
    out.write(data)
    out.close()


def get_art(checksum):
    if not checksum:
        return None
    filepath = join('.' + ART_DIR + checksum + ".jpg")

    return filepath
