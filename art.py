from os import path, listdir
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4, MP4Tags, MP4Cover
from config import config
import imghdr

ART_DIR = config.get('Artwork', 'art_path')

def index_art(song):
    ext = path.splitext(song['path'])[1]

    try:
        if ext == '.mp3':
            tags = MP3(song['path'])
        elif ext == '.flac':
            tags = FLAC(song['path'])
        elif ext == '.m4a':
            tags = MP4(song['path']).tags
        else:
            return None
    except:
        return None

    data = ''

    if isinstance(tags, FLAC) and tags.pictures:
        data = tags.pictures[0].data
    elif isinstance(tags, MP3):
        for tag in tags:
            if tag.startswith('APIC'):
                data = tags[tag].data
                break
    elif isinstance(tags, MP4Tags) and 'covr' in tags and tags['covr']:
        data = tags['covr'][0]

    if not data:
        directory = find_art(song)
        if directory:
            try:
                afile = open(directory, 'r')
                data = afile.read()
                afile.close()
            except IOError:
                return None
        else:
            return None

    directory = write_art(song, data)

def find_art(song):
    art_strings = ['cover.jpg', 'cover.png', 'folder.jpg', 'folder.png']
    directory = path.dirname(song['path'])
    for s in art_strings:
        if path.isfile(path.join(directory, s)):
            return path.join(directory, s)

    for f in listdir(directory):
        ext = path.splitext(f)[1]
        if ext == '.jpg' or ext == '.png':
            return path.join(directory, f)

    return None


def write_art(song, data):
    if not data or not song['artist'] or not song['album']:
        return None

    image_type = imghdr.what(None, data)
    ext = ''

    if image_type == 'jpeg':
        ext = '.jpg'
    elif image_type == 'png':
        ext = '.png'

    title = u"{0} - {1}".format(song['artist'], song['album'])
    folder = sanitize_folder_name(title)
    filepath = u"{0}{1}{2}".format('.' + ART_DIR, folder, ext)
    out = open(filepath, 'w')
    out.write(data)
    out.close()


def get_art(artist, album):
    if not album or not artist:
        return None
    ext = ['.jpg', '.png']

    name = u"{0} - {1}".format(artist, album)
    folder = sanitize_folder_name(name)

    for e in ext:
        if path.isfile('.' + ART_DIR + folder + e):
            return '.' + ART_DIR + folder + e

    return None

def sanitize_folder_name(name):
    keepcharacters = (' ','.','_','-')
    folder = "".join(c for c in name if c.isalnum() or c in keepcharacters).rstrip()
    return folder
