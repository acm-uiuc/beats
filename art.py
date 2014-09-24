from os.path import splitext, isfile
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
import hashlib
from config import config

art_path = config.get('Artwork', 'art_path')

def index_art(path):
    ext = splitext(path)[1]

    art_uri = ""
    if ext == ".mp3":
        art_uri = index_mp3_art(path)
    elif ext == ".flac":
        art_uri = index_flac_art(path)
    
    return art_uri

def index_mp3_art(song):
    try:
        tags = MP3(song)
    except:
        return False
    data = ""
    for tag in tags:
        if tag.startswith("APIC"):
            data = tags[tag].data
            break

    path = write_art(data)

    return path

def index_flac_art(song):
    try:
        tags = FLAC(song)
    except:
        return False
    data = ""
    if tags.pictures[0].data:
        data = tags.pictures[0].data

    path = write_art(data)

    return path

def write_art(data):
    if not data:
        return None

    m = hashlib.md5()
    m.update(data)

    filename = m.hexdigest() + ".jpg"

    if not isfile("." + art_path + filename):
        out = open("." + art_path + filename, "w")
        out.write(data)
        out.close()

    return art_path + filename
