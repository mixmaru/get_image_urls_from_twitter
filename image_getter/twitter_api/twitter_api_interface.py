import abc


class TwitterApiInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def exec_search(self, query, max_id=None, since_id=None):
        pass
