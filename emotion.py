from flask import Flask, request, jsonify
from tensorflow import keras
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
import json

app = Flask(__name__)

# 훈련된 모델을 로드합니다.
model5 = keras.models.load_model('lstm5.h5')

# 토크나이저를 로드합니다.
tokenizer = Tokenizer(10807)
tokenizer.fit_on_texts([])  # 토크나이저를 로드하기 위해 빈 데이터로 fit합니다.

# 감정 변환 함수를 정의합니다.
def emotion(x):
    if x == '기쁨':
        return 0
    elif x == '당황':
        return 1
    elif x == '분노':
        return 2
    elif x == '불안':
        return 3
    elif x == '상처':
        return 4
    elif x == '슬픔':
        return 5

# 문장을 전처리하고 감정을 예측하는 함수를 정의합니다.
def predict_emotions(sentence):
    okt = Okt()
    data_test = []
    data_test_preprocessing = okt.morphs(sentence, stem=True)
    data_test.append(data_test_preprocessing)

    tokenizer.fit_on_texts(data_test)
    data_test_input = tokenizer.texts_to_sequences(data_test)

    test_data_seq = pad_sequences(data_test_input, maxlen=152)

    predictions = model5.predict(test_data_seq)
    return predictions[0]

# 감정 백분율을 계산하는 함수를 정의합니다.
def calculate_emotion_percentages(sentence):
    emotions = predict_emotions(sentence)
    percentages = {
        '기쁨': int(emotions[0] * 100),
        '당황': int(emotions[1] * 100),
        '분노': int(emotions[2] * 100),
        '불안': int(emotions[3] * 100),
        '상처': int(emotions[4] * 100),
        '슬픔': int(emotions[5] * 100)
    }
    return percentages


@app.route('/predict_emotions', methods=['GET', 'POST'])
def predict_emotions_api():
    if request.method == 'GET':
        try:
            sentence = request.args.get('sentence', '')
            percentages = calculate_emotion_percentages(sentence)

            # 가장 높은 퍼센트의 감정을 찾습니다.
            max_emotion = max(percentages, key=percentages.get)

            response_data = {
                'emotion_percentages': percentages,
                'max_emotion': max_emotion
            }

            # 감정 백분율과 가장 높은 감정을 JSON 형식으로 반환하고 한글 인코딩을 지정합니다.
            response = app.response_class(
                response=json.dumps(response_data, ensure_ascii=False, default=str),
                status=200,
                mimetype='application/json; charset=utf-8'
            )
            return response
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif request.method == 'POST':
        try:
            data = request.get_json()
            sentence = data.get('sentence', '')
            percentages = calculate_emotion_percentages(sentence)

            # 가장 높은 퍼센트의 감정을 찾습니다.
            max_emotion = max(percentages, key=percentages.get)

            response_data = {
                'emotion_percentages': percentages,
                'max_emotion': max_emotion
            }

            # 감정 백분율과 가장 높은 감정을 JSON 형식으로 반환하고 한글 인코딩을 지정합니다.
            response = app.response_class(
                response=json.dumps(response_data, ensure_ascii=False, default=str),
                status=200,
                mimetype='application/json; charset=utf-8'
            )
            return response
        except Exception as e:
            return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
