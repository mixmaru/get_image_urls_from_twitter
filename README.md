# get_image_urls_from_twitter

検索ワードでヒットするtweetの画像urlの一覧をできるだけ取得する。  
どれくらい取得できるかは、twitter search apiの仕様による。  
https://developer.twitter.com/en/docs/tweets/search/overview  
※Standard Search APIであれば過去7日分まで。

# 動作検証

python 3.6.6での実行確認済

# 準備
## ダウンロード
```
$ git clone https://github.com/mixmaru/get_image_urls_from_twitter.git
$ cd get_image_urls_from_twitter
```

## twitter api トークンの設定

config.py.orgをコピー、または名称変更して、apiのトークンなどをここに記述する
```
cp config.py.org config.py
```

```
# 「***」の部分をそれぞれ置き換える
CONSUMER_KEY = "***"
CONSUMER_SECRET = "***"
ACCESS_TOKEN = "***"
ACCESS_TOKEN_SECRET = "***"
```

トークンの取得方法などはこことかを参考に
https://qiita.com/bakira/items/00743d10ec42993f85eb

## 必要ライブラリのインポート

pipenvを使っているのでpipenvをインストールする。
```
$ pip install pipenv
```

ライブラリのインポートをする
```
$ pipenv sync
```

# 使い方

pipenvで仮想環境に入る
```
$ pipenv shell
```

画像url取得実行
```
$ python -m image_getter "#雲"
```

標準出力にurlのリストが出力される
```
(tweet id)          (画像url)
1041553909938974722 https://pbs.twimg.com/media/DnRUxRoUcAEtG_H.jpg
1041553382329204736 https://pbs.twimg.com/media/DnRUxRpVAAEi-EN.jpg
1041553382329204736 https://pbs.twimg.com/media/DnRUxRqU4AUzAm3.jpg
1041553382329204736 https://pbs.twimg.com/media/DnRUxRpVsAAf4n3.jpg
1041553382329204736 https://pbs.twimg.com/media/DnRUxRoUcAEtG_H.jpg
...
```


