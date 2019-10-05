# ローカルでのpythonの環境構築
## pyenv と pipenvのインストール
    - `apt install pyenv` で `pyenv install 3.7`をして、3.7 の環境を取得
    - `apt install pipenv`した後、`pipenv shell --python=3.7` で現在のフォルダにpython3.7の環境を構築
    - `pipenv shell`でpython環境をactivate(terminalの先頭に現在activateされるようにすると便利)
    - https://dev.classmethod.jp/etc/environment_to_pipenv-pyenv/
## pipenv shellでactivateして必要なファイルをインストール
    - `pip install -r requirements.txt`で必要なものを取得できる

# GCPの設定方法
## ローカル環境設定手順
### gcloud SDKをインストールしてコマンドラインでの操作を可能にする
    - https://cloud.google.com/sdk/downloads?hl=ja

### gcloud init で使用する環境を設定する
    - どのスペース、アカウント、プロジェクトを使用するかを入力
    - https://cloud.google.com/sdk/docs/quickstart-debian-ubuntu?hl=ja

## GAEを使用する設定
    - GAEでスタンダード環境を選択
        - 3.7なのでスタンダードで対応可能
        - https://cloud.google.com/appengine/docs/the-appengine-environments?hl=ja

    - GAE用のコンポーネントとエクステンションを取得
        - https://cloud.google.com/appengine/docs/standard/python/download?hl=ja

## Djangoを使用する設定
    - Python3.7を使うためのGAEの環境設定を追加(DockerFileのようなもの)
        - 今のところ、DBは使用していないのでCloudSQLの設定は不要
        - app.yamlの設定だけ行う
        - https://cloud.google.com/python/django/appengine
    - Django等を使用できるように`requirements.txt`を作成
        - pipenvをactivateにして`requirements.txt`を吐き出し

## Djangoの開始
