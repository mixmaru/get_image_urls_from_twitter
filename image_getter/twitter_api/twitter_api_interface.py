import abc


class TwitterApiInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def exec_search(self, query, max_id=None):
        pass
