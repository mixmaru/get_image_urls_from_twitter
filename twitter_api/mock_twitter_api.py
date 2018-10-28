import json

from requests import Response
from .twitter_api_interface import TwitterApiInterface


# twitter search apiのラッパーのモック。
# 3で割り切れるtweet_idのデータには画像urlが2つ({tweet_id}_1.jpg,{tweet_id}_2.jpg)存在する
class MockTwitterApi(TwitterApiInterface):
    def __init__(self):
        self.__query = None
        self.__once_getting_num = 10
        self.__maximum_id = 100
        self.__minimum_id = 0

    def set_once_getting_num(self, num: int):
        self.__once_getting_num = num

    # 取得できる最大idを指定
    def set_maximum_id(self, id: int):
        self.__maximum_id = id

    # 取得できる最小idを指定
    def set_minimum_id(self, id: int):
        self.__minimum_id = id

    def exec_search(self, query, max_id=None):
        if self.__minimum_id > self.__maximum_id:
            raise Exception("maximum_idよりもminimu_idに大きな値がセットされています")

        self.__query = query

        response = Response()
        response.status_code = 200
        response._content = self.__create_content(max_id)
        return response

    def __create_content(self, max_id: int=None):
        if max_id is None:
            max_id = self.__maximum_id

        ret_data = {'statuses': []}

        for i in range(self.__once_getting_num):
            id = max_id - i
            if id < self.__minimum_id:
                break

            ret_data['statuses'].append({
                'id': id,
            })

            if id % 3 == 0:
                ret_data['statuses'][i]['extended_entities'] = {
                    'media': [
                        {'media_url_https': 'https://{0}_1.jpg'.format(id)},
                        {'media_url_https': 'https://{0}_2.jpg'.format(id)},
                    ]
                }
        return json.dumps(ret_data).encode()
