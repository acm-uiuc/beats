from os.path import join, split, splitext
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
import hashlib
from config import config

ART_DIR = config.get('Artwork', 'art_path')

def index_art(path):
    ext = splitext(path)[1]

    art_uri = ''
    if ext == '.mp3':
        art_uri = index_mp3_art(path)
    elif ext == '.flac':
        art_uri = index_flac_art(path)

    return art_uri

def index_mp3_art(song):
    try:
        tags = MP3(song)
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
        tags = FLAC(song)
    except:
        return False
    data = ''
    if tags.pictures[0].data:
        data = tags.pictures[0].data

    path = write_art(song, data)

    return path

def write_art(path, data):
    if not data:
        return None

    filepath = get_art(path)

    out = open(filepath, 'w')
    out.write(data)
    out.close()

def get_art(path):
    m = hashlib.md5()
    m.update(split(path)[0].encode('utf-8'))
    filename = m.hexdigest() + '.jpg'

    filepath = join('.' + ART_DIR + filename)
    print filepath

    return filepath
