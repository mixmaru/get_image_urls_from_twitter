from requests_oauthlib import OAuth1Session
from .twitter_api_interface import TwitterApiInterface


class TwitterApi(TwitterApiInterface):
    def __init__(self, consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str):
        self.__consumer_key = consumer_key
        self.__consumer_secret = consumer_secret
        self.__access_token = access_token
        self.__access_token_secret = access_token_secret

    def exec_search(self, query, max_id=None, since_id=None):
        twitter = OAuth1Session(self.__consumer_key, self.__consumer_secret, self.__access_token, self.__access_token_secret)
        url = "https://api.twitter.com/1.1/search/tweets.json"
        params = {
            'q': query,
            'count': 100,
        }
        if max_id is not None:
            params['max_id'] = max_id
        if since_id is not None:
            params['since_id'] = since_id
        return twitter.get(url, params=params)
