import json
import time
import unittest

import config
from image_getter import ImageGetter
from twitter_api.twitter_api import TwitterApi
from twitter_api.mock_twitter_api import MockTwitterApi


class TestMain(unittest.TestCase):
    def test_execute_real_twitter_api(self):
        twitter_api = TwitterApi(config.CONSUMER_KEY, config.CONSUMER_SECRET, config.ACCESS_TOKEN,
                                 config.ACCESS_TOKEN_SECRET)
        res = twitter_api.exec_search('#虹')
        self.assertTrue(res.status_code == 200)

    def test_execute_mock_twitter_api(self):
        twitter_api = MockTwitterApi()
        twitter_api.set_once_getting_num = 10
        twitter_api.set_maximum_id = 100
        res = twitter_api.exec_search('#虹')

        expect_content = json.dumps(self.__create_expect_content(max_id=100, since_id=91)).encode()
        self.assertTrue(res.status_code == 200)
        self.assertEqual(expect_content, res.content)

        # もう一回実行
        res = twitter_api.exec_search('#虹')
        expect_content = json.dumps(self.__create_expect_content(max_id=100, since_id=91)).encode()
        self.assertTrue(res.status_code == 200)
        self.assertEqual(expect_content, res.content)

        # max_idを指定して実行
        res = twitter_api.exec_search('#虹', max_id=5)
        expect_content = json.dumps(self.__create_expect_content(max_id=5, since_id=0)).encode()
        self.assertTrue(res.status_code == 200)
        self.assertEqual(expect_content, res.content)

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

        image_getter.set_query('#雨')
        image_urls = image_getter.get_urls()
        self.assertListEqual(expect_urls, image_urls)

    def test_image_getter_iterate(self):
        twitter_api = MockTwitterApi()
        twitter_api.set_once_getting_num(20)
        twitter_api.set_maximum_id(200)
        twitter_api.set_minimum_id(101)
        image_getter = ImageGetter(twitter_api)
        image_getter.set_sleep(0)
        image_getter.set_query('#虹')
        got_urls = []
        for images_list in image_getter.get_urls_list_maximum_iterate():
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

    @staticmethod
    def __make_test_file(file_name):
        f = open(file_name, "w", encoding="utf-8")
        f.write("初期入力データ\n")
        f.close()

    def __get_image_urls_maximum(self, content):
        ret_list = []
        for i in range(2):
            ret_list.extend(self.__get_image_urls_once(content))
        return ret_list

    @staticmethod
    def __get_image_urls_once(content):
        ret_list = []
        content = json.loads(content)
        for tweet in content['statuses']:
            if 'extended_entities' in tweet:
                for image in tweet['extended_entities']['media']:
                    ret_list.append(image['media_url_https'])
        return ret_list


if __name__ == "__main__":
    unittest.main()
