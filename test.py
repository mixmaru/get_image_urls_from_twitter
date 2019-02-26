import json
import time
import unittest

from image_getter.config import *
from image_getter.image_getter import ImageGetter
from image_getter.twitter_api.twitter_api import TwitterApi
from image_getter.twitter_api.mock_twitter_api import MockTwitterApi


class TestMain(unittest.TestCase):
    # 実際のtwitter apiに接続してsearch apiが実行できているかをテスト
    def test_execute_real_twitter_api(self):
        twitter_api = TwitterApi(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN,
                                 ACCESS_TOKEN_SECRET)
        res = twitter_api.exec_search('#虹')
        self.assertTrue(res.status_code == 200)

    # MockTwitterApi.exec_searchの実行テスト：デフォルト実行
    def test_execute_mock_twitter_api(self):
        twitter_api = MockTwitterApi()
        res = twitter_api.exec_search('#虹')

        self.assertTrue(res.status_code == 200)
        expect_content = json.dumps(self.__create_expect_content(max_id=100, since_id=91)).encode()
        self.assertEqual(expect_content, res.content)

    # MockTwitterApi.exec_searchの実行テスト：一回実行で取得される数を指定
    def test_execute_mock_twitter_api_01(self):
        twitter_api = MockTwitterApi()
        twitter_api.set_once_getting_num(20)
        res = twitter_api.exec_search('#虹')

        self.assertTrue(res.status_code == 200)
        expect_content = json.dumps(self.__create_expect_content(max_id=100, since_id=81)).encode()
        self.assertEqual(expect_content, res.content)

    # MockTwitterApi.exec_searchの実行テスト：一回に取得する数が取得されるtweet_idが最大値と最小値内に収まる場合
    def test_execute_mock_twitter_api_02(self):
        twitter_api = MockTwitterApi()
        twitter_api.set_minimum_id(300)
        twitter_api.set_maximum_id(400)
        twitter_api.set_once_getting_num(100)
        res = twitter_api.exec_search('#虹')

        self.assertTrue(res.status_code == 200)
        expect_content = json.dumps(self.__create_expect_content(max_id=400, since_id=301)).encode()
        self.assertEqual(expect_content, res.content)

    # MockTwitterApi.exec_searchの実行テスト：一回に取得する数が取得されるtweet_idが最大値と最小値内に収まらない場合
    def test_execute_mock_twitter_api_03(self):
        twitter_api = MockTwitterApi()
        twitter_api.set_minimum_id(300)
        twitter_api.set_maximum_id(400)
        twitter_api.set_once_getting_num(1000)
        res = twitter_api.exec_search('#虹')

        self.assertTrue(res.status_code == 200)
        expect_content = json.dumps(self.__create_expect_content(max_id=400, since_id=300)).encode()
        self.assertEqual(expect_content, res.content)

    # MockTwitterApi.exec_searchの実行テスト：取得できるtweet_idの最大値が最小値よりも小さかった場合
    def test_execute_mock_twitter_api_04(self):
        twitter_api = MockTwitterApi()
        twitter_api.set_minimum_id(300)
        twitter_api.set_maximum_id(200)
        with self.assertRaises(Exception):
            res = twitter_api.exec_search('#虹')

    # tweet_idがmax_idのものから、since_idのものまでのデータを作成。
    # 3で割り切れるtweet_idのデータには画像urlが2つ({tweet_id}_1.jpg,{tweet_id}_2.jpg)存在する
    def __create_expect_content(self, max_id: int, since_id: int):
        ret_data = {'statuses': []}
        for id in reversed(range(since_id, max_id + 1)):
            make_image = True if (id % 3 == 0) else False
            ret_data['statuses'].append(self.__create_expect_status(id, make_image))
        return ret_data

    def __create_expect_status(self, id: int, image: bool):
        ret_status = {
            'id': id,
        }
        if image:
            ret_status['extended_entities'] = {'media': []}
            ret_status['extended_entities']['media'].append({'media_url_https': self.__create_expect_image_url(id, 1)})
            ret_status['extended_entities']['media'].append({'media_url_https': self.__create_expect_image_url(id, 2)})
        return ret_status

    @staticmethod
    def __create_expect_image_url(i1: int, i2: int):
        return 'https://{0}_{1}.jpg'.format(i1, i2)

    # ImageGetter.get_urlsのテスト：max_idからminimum_idまでのデータを一括取得できているか？
    def test_image_getter(self):
        twitter_api = MockTwitterApi()
        twitter_api.set_once_getting_num(10)
        twitter_api.set_maximum_id(100)
        twitter_api.set_minimum_id(0)
        image_getter = ImageGetter(twitter_api)
        image_getter.set_sleep(0)
        image_getter.set_query('#虹')
        image_urls = image_getter.get_urls()

        expect_urls = self.__create_image_getter_expect_urls(max_id=100, since_id=0)
        self.assertListEqual(expect_urls, image_urls)

    # ImageGetter.get_urls_iteratorのテスト：max_idからminimum_idまでのデータを一括取得できているか？
    def test_image_getter_iterate(self):
        twitter_api = MockTwitterApi()
        twitter_api.set_once_getting_num(20)
        twitter_api.set_maximum_id(200)
        twitter_api.set_minimum_id(101)
        image_getter = ImageGetter(twitter_api)
        image_getter.set_sleep(0)
        image_getter.set_query('#虹')
        got_urls = []
        for images_list in image_getter.get_urls_iterator():
            got_urls.extend(images_list)

        expect_urls = self.__create_image_getter_expect_urls(max_id=200, since_id=101)
        self.assertListEqual(expect_urls, got_urls)

    def __create_image_getter_expect_urls(self, max_id: int, since_id: int):
        ret_list = []
        for id in reversed(range(since_id, max_id+1)):
            if id % 3 == 0:
                ret_list.extend(self.__create_url_list(id))
        return ret_list

    def __create_url_list(self, id: int):
        return [
            {
                'id': id,
                'image_urls': [
                    'https://{0}_1.jpg'.format(id),
                    'https://{0}_2.jpg'.format(id),
                ]
            }
        ]

    # image_getterがapiを実行する際に1秒以上sleepしているか確認
    def test_image_getter_sleep(self):
        twitter_api = MockTwitterApi()
        twitter_api.set_maximum_id(20)
        twitter_api.set_once_getting_num(10)
        image_getter = ImageGetter(twitter_api)
        image_getter.set_query('#虹')

        start = time.time()
        image_getter.get_urls()
        exec_time = time.time() - start
        self.assertTrue(exec_time >= 1)


if __name__ == "__main__":
    unittest.main()
