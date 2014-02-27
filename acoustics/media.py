from abc import ABCMeta, abstractmethod

class Media(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def mrl(self):
        pass

    @abstractmethod
    def dictify(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass
