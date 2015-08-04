import threading
import vlc

# Initial player volume
INITIAL_VOLUME = 50

instance = vlc.Instance('--no-video')
player = instance.media_player_new()
has_initialized = False
now_playing = None
volume = 100

# Equalizer functionality (requires libvlc 2.2.0 or newer)

def populate_equalizer_globals(equalizer, preset_idx=0):
    # We intend to change the global variables specified below
    global equalizer_preamp_level
    global equalizer_preset
    global equalizer_band_levels

    # Get preamp level/preset (preamp level value in dB)
    equalizer_preamp_level = vlc.libvlc_audio_equalizer_get_preamp(equalizer)
    equalizer_preset = preset_idx

    # Get band levels (values in dB)
    # Note that num_equalizer_bands must be set at this point
    equalizer_band_levels = [
        vlc.libvlc_audio_equalizer_get_amp_at_index(equalizer, idx)
        for idx in xrange(num_equalizer_bands)]

try:
    # Initialize equalizer
    equalizer = vlc.libvlc_audio_equalizer_new()
    equalizer_enabled = False

    # Populate equalizer band frequencies (values in Hz)
    num_equalizer_bands = vlc.libvlc_audio_equalizer_get_band_count()
    equalizer_band_freqs = tuple(
        vlc.libvlc_audio_equalizer_get_band_frequency(idx)
        for idx in xrange(num_equalizer_bands))

    # Populate equalizer preset names
    num_equalizer_presets = vlc.libvlc_audio_equalizer_get_preset_count()
    equalizer_preset_names = tuple(
        vlc.libvlc_audio_equalizer_get_preset_name(idx)
        for idx in xrange(num_equalizer_presets))

    # Initialize equalizer globals
    populate_equalizer_globals(equalizer)

    # If we get to this stage, we know we have a version of VLC that has
    # equalizer support
    equalizer_supported = True
except NameError:
    # If we reach this exception, we know we have an older version of VLC that
    # does not have equalizer support
    equalizer_supported = False

def play(mrl):
    m = instance.media_new(mrl)
    player.set_media(m)
    player.play()
    return get_status()


def play_media(media):
    play(media.mrl())
    global now_playing
    now_playing = media

    # Initialize the player volume to a non-max value on first play to protect
    # eardrums. The player does not respond to volume changes right after the
    # media loads, so the timer interval below was determined empirically.
    global has_initialized
    if not has_initialized:
        threading.Timer(1, set_volume, (INITIAL_VOLUME,)).start()
        has_initialized = True

    return get_status()


def pause():
    player.pause()
    return get_status()


def stop():
    player.stop()
    global now_playing
    now_playing = None
    return get_status()


def get_status():
    media = player.get_media()
    status = {'state': str(player.get_state()), 'volume': volume}
    if equalizer_supported:
        status['equalizer_enabled'] = equalizer_enabled
        status['equalizer_preset'] = equalizer_preset
        status['equalizer_preamp_level'] = equalizer_preamp_level
        status['equalizer_band_levels'] = equalizer_band_levels
    if media:
        status['media'] = vlc.bytes_to_str(media.get_mrl())
        status['current_time'] = player.get_time()
        status['duration'] = media.get_duration()
    return status


def get_now_playing():
    obj = {'player_status': get_status()}
    if now_playing:
        obj['media'] = now_playing.dictify()
    return obj


def set_volume(vol):
    global volume
    volume = vol
    player.audio_set_volume(vol)
    return get_status()


def get_static_equalizer_info():
    # This routine is useful in that we know right away the number of presets
    # and the number of bands
    info = {'equalizer_supported': equalizer_supported}
    if equalizer_supported:
        info['equalizer_preset_names'] = equalizer_preset_names
        info['equalizer_band_freqs'] = equalizer_band_freqs
    return info


def set_equalizer_enabled(enabled):
    global equalizer_enabled
    if equalizer_enabled != enabled:
        equalizer_enabled = enabled
        player.set_equalizer(equalizer if enabled else None)
    return get_status()


def set_equalizer_preset(idx):
    global equalizer
    vlc.libvlc_audio_equalizer_release(equalizer)
    equalizer = vlc.libvlc_audio_equalizer_new_from_preset(idx)
    populate_equalizer_globals(equalizer, preset_idx=idx)
    if equalizer_enabled:
        player.set_equalizer(equalizer)
    return get_status()


def set_equalizer_preamp(lev):
    global equalizer_preamp_level
    equalizer_preamp_level = lev
    vlc.libvlc_audio_equalizer_set_preamp(equalizer, lev)
    if equalizer_enabled:
        player.set_equalizer(equalizer)
    return get_status()


def set_equalizer_band(idx, lev):
    global equalizer_band_levels
    equalizer_band_levels[idx] = lev
    vlc.libvlc_audio_equalizer_set_amp_at_index(equalizer, lev, idx)
    if equalizer_enabled:
        player.set_equalizer(equalizer)
    return get_status()


def has_ended():
    return player.get_state() in [
        vlc.State.Ended,
        vlc.State.Stopped,
        vlc.State.NothingSpecial,
        vlc.State.Error,
    ]


def is_youtube_video(m=None):
    if m is None:
        m = player.get_media()
    mrl = vlc.bytes_to_str(m.get_mrl())
    return m is not None and 'http://www.youtube.com' in mrl


def get_vlc_version():
    return vlc.libvlc_get_version()
