"""
This is an implementation of packet-by-packet Generalized Processor Sharing, as
described in the following paper:

Abhay K. Parekh and Robert G. Gallager. 1993. A generalized processor sharing
approach to flow control in integrated services networks: the single-node case.
IEEE/ACM Trans. Netw. 1, 3 (June 1993), 344-357. DOI=10.1109/90.234856
http://dx.doi.org/10.1109/90.234856
"""

from db import Session, Song, Packet, Vote
from sqlalchemy import func, distinct
from sqlalchemy.exc import IntegrityError
import threading
import time

SCHEDULER_INTERVAL_SEC = 0.25
"""Interval at which to run the scheduler loop"""

class Scheduler(object):
    virtual_time = 0.0

    active_sessions = 0
    """Number of users with currently queued songs"""

    def __init__(self):
        self._update_active_sessions()

    def vote_song(self, user, song_id):
        """Vote for a song"""
        session = Session()
        packet = session.query(Packet).filter_by(song_id=song_id).first()
        if packet:
            if user == packet.user:
                session.rollback()
                raise Exception('User ' + user + ' has already voted for this song')
            try:
                packet.additional_votes.append(Vote(user=user))
                session.commit()
            except IntegrityError:
                session.rollback()
                raise Exception('User ' + user + ' has already voted for this song')
        else:
            packet = Packet(song_id=song_id,
                    user=user,
                    arrival_time=self.virtual_time)
            session.add(packet)
            session.commit()
            self._update_active_sessions()

    def num_songs_queued(self):
        """Returns the number of songs that are queued"""
        session = Session()
        num_songs = session.query(Packet).count()
        session.commit()
        return num_songs

    def empty(self):
        """Returns true if there are no queued songs"""
        # If there are no queued songs, there are also no active sessions
        return self.active_sessions == 0

    def _update_active_sessions(self):
        """Updates the active_sessions member variable"""
        session = Session()
        self.active_sessions = session.query(Packet.user).distinct().count()
        session.commit()

    def _increment_virtual_time(self):
        """Increments the virtual time"""
        if not self.empty():
            self.virtual_time += SCHEDULER_INTERVAL_SEC / self.active_sessions

    def _scheduler_thread(self):
        """Main scheduler loop"""
        while True:
            self._increment_virtual_time()
            time.sleep(SCHEDULER_INTERVAL_SEC)

    def start(self):
        """Starts the scheduler"""
        thread = threading.Thread(target=self._scheduler_thread)
        thread.daemon = True
        thread.start()

if __name__ == '__main__':
    s = Scheduler()
    s.start()
    if s.empty():
        s.vote_song('klwang3', 1);
        s.vote_song('klwang3', 2);
        s.vote_song('bezault2', 3);
        s.vote_song('bezault2', 2);
    while True:
        print 'Virtual time: %.3f\tActive sessions: %d' % (s.virtual_time, s.active_sessions)
        time.sleep(SCHEDULER_INTERVAL_SEC)
