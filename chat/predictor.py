import MeCab
import pandas as pd
from joblib import load
from sklearn.feature_extraction.text import TfidfVectorizer

# ラベルや学習モデルはずっとかわらないので、staticで持っておくのがいいかもしれない
# 一回一回読み込んでたら死ぬのでは？
static_sentence_csv = pd.read_csv('chat/static/chat/file/data.csv')
static_reply_csv = pd.read_csv('chat/static/chat/file/reply.csv')


class Predictor():
    tagger = MeCab.Tagger("-Ochasen")
    INDEX_CATEGORY = 0
    INDEX_ROOT_FORM = 6
    TARGET_CATEGORIES = ["名詞", "動詞", "形容詞", "連体詞", "副詞"]
    text = []
    words = []

    def __init__(self, *args, **kwargs):
        self.text = []
        self.words = []

    def extract_words(self, text):

        if not text:
            return []

        node = self.tagger.parseToNode(text)
        while node:
            features = node.feature.split(',')
            if features[self.INDEX_CATEGORY] in self.TARGET_CATEGORIES:
                if features[self.INDEX_ROOT_FORM] == "*":
                    self.words.append(node.surface)
                else:
                    self.words.append(features[self.INDEX_ROOT_FORM])

            node = node.next

        return self.words

    def execute(self, sentence):
        # データ読み込み
        m = load("chat/static/chat/pkl/model.pkl")
        le = load("chat/static/chat/pkl/le.pkl")
        v = load("chat/static/chat/pkl/vocabulary.pkl")

        try:
            # 予測
            self.text.append(sentence)
            tv = TfidfVectorizer(analyzer=self.extract_words, vocabulary=v)
            new_data = tv.fit_transform(self.text)
            classify = m.predict(X=new_data)
            print(text)
            print(new_data.shape)
            # 戻り値呼び出し
            compatible_class = le.inverse_transform(classify)
            print(compatible_class)
            result = static_reply_csv.query('Label == ' + str(compatible_class))
            print(result["Words"])
            return result
        except Exception as e:
            print(f"error: {e}")
            return "ごめんね。何を言っているのかわからなかった..."