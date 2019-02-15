import sys
import json
import time

from .twitter_api import twitter_api_interface, twitter_api


class ImageGetter:
    def __init__(self, api: twitter_api_interface):
        self.__api = api
        self.__query = None
        self.out_detail_message = False
        self.__sleep = 1

    def set_sleep(self, seconds: int):
        self.__sleep = seconds

    def set_query(self, query: str):
        self.__query = query

    def get_urls(self):
        if self.__query is None:
            raise Exception('queryがセットされていません')
        ret_urls = []
        for urls_list in self.get_urls_iterator():
            ret_urls.extend(urls_list)
        return ret_urls

    # urlデータリストをapi実行毎にyieldで返してくる
    def get_urls_iterator(self):
        if self.__query is None:
            raise Exception('queryがセットされていません')

        prev_last_id = None
        while True:
            if prev_last_id is None:
                time.sleep(self.__sleep) # apiに負荷をかけないため

            images_list = self.__get_urls_by_once_execution(prev_last_id)
            # 初回実行でない場合は、最初の一つが前回取得済のデータである場合があるので取り除く
            if len(images_list) >= 1 and images_list[0]['id'] == prev_last_id:
                images_list.pop(0)

            if len(images_list) > 0:
                prev_last_id = images_list[-1]['id']
                yield images_list
            else:
                # 空なら終了
                self.__print('これ以上取得できるデータがありません。')
                break

    # api一回実行分のデータを取得し、データを成形して返す
    def __get_urls_by_once_execution(self, max_id: int=None):
        if self.__query is None:
            raise Exception('queryがセットされていません')

        result = self.__get_data_from_api(max_id)
        return self.__create_urls_data_from_api_result_content(result.content)

    # apiを一回実行する
    def __get_data_from_api(self, max_id: int=None):
        while True:
            result = self.__api.exec_search(self.__query, max_id=max_id)
            self.__print('api実行')
            if result.status_code == 200:
                return result
            if result.status_code == 429:
                self.__print('api制限。1分待機')
                time.sleep(60)
                continue
            else:
                msg = "apiへの接続に失敗しました。status code[{0}]".format(result.status_code)
                self.__print(msg)
                raise Exception(msg)

    # apiからの返却データからimage_urlとidデータだけを取得してリストにして返す。image_urlデータがないものは含めない
    def __create_urls_data_from_api_result_content(self, content):
        ret_data_list = []
        status = json.loads(content)
        for status in status['statuses']:
            data = self.__create_urls_data_from_status(status)
            if len(data['image_urls']) > 0:
                ret_data_list.append(data)
        return ret_data_list

    # apiからの返却データからimage_urlとidデータだけを取得して返す
    def __create_urls_data_from_status(self, status):
        ret_data = {
            'id': status['id'],
            'image_urls': []
        }
        if 'extended_entities' in status:
            for image in status['extended_entities']['media']:
                ret_data['image_urls'].append(image['media_url_https'])
        return ret_data

    def __print(self, message):
        if self.out_detail_message:
            print(message, flush=True)


if __name__ == "__main__":
    from . import config
    args = sys.argv

    if len(args) < 2:
        print("python -m image_getter [query]")
        exit(1)

    query = str(args[1])
    api = twitter_api.TwitterApi(config.CONSUMER_KEY, config.CONSUMER_SECRET, config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)
    image_getter = ImageGetter(api)
    image_getter.set_query(query)
    image_getter.out_detail_message = True
    for images_list in image_getter.get_urls_iterator():
        for images_data in images_list:
            for url in images_data['image_urls']:
                print('{0} {1}'.format(images_data['id'], url), flush=True)
    exit(0)
