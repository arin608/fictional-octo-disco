from flask import Flask, request, jsonify
import requests
import random
import googleapiclient.discovery

app = Flask(__name__)

# Google 개발자 콘솔에서 생성한 YouTube API 키 입력
API_KEY = 'AIzaSyAxWQAhD-N6TEGvcIfLYECB3Smq7p8f3u0'

# YouTube API 클라이언트 생성
youtube = googleapiclient.discovery.build('youtube', 'v3', developerKey=API_KEY)

# 감정별로 음악 데이터를 저장할 딕셔너리
emotion_music_data = {
    '기쁨': [],
    '슬픔': [],
    '분노': [],
    '불안': [],
    '상처': [],
    '당황': []
}

# 음악 데이터를 가져와서 딕셔너리에 저장하는 함수
def fetch_music_data():
    api_urls = {
        '기쁨': ['https://www.music-flo.com/api/meta/v1/channel/52765', 'https://www.music-flo.com/api/meta/v1/channel/29869'],
        '슬픔': ['https://www.music-flo.com/api/meta/v1/channel/25378', 'https://www.music-flo.com/api/meta/v1/channel/30100'],
        '분노': ['https://www.music-flo.com/api/meta/v1/channel/29093', 'https://www.music-flo.com/api/meta/v1/channel/42487'],
        '불안': ['https://www.music-flo.com/api/meta/v1/channel/48387', 'https://www.music-flo.com/api/meta/v1/channel/26139'],
        '상처': ['https://www.music-flo.com/api/meta/v1/channel/47090', 'https://www.music-flo.com/api/meta/v1/channel/22546'],
        '당황': ['https://www.music-flo.com/api/meta/v1/channel/52466', 'https://www.music-flo.com/api/meta/v1/channel/26126']
    }

    for emotion, api_url_list in api_urls.items():
        music_list = []

        for api_url in api_url_list:
            req = requests.get(api_url)
            data = req.json()
            new_musics = data['data']['trackList']

            for new_music in new_musics:
                music_list.append({
                    'title': new_music['name'],
                    'artist': new_music['artistList'][0]['name']
                })

        emotion_music_data[emotion] = music_list

# 각각의 감정에 따른 음악을 랜덤하게 선택하는 함수
def get_random_music(emotion):
    music_list = emotion_music_data.get(emotion)
    if music_list:
        random_music = random.choice(music_list)
        return random_music
    else:
        return None

@app.route('/get_music', methods=['GET'])
def get_music():
    emotion = request.args.get('emotion')

    if emotion:
        # 각각의 감정에 따른 음악 추천
        recommended_music = get_random_music(emotion)

        if recommended_music:
            title = recommended_music['title']
            artist = recommended_music['artist']

            # YouTube에서 해당 노래 검색
            search_query = f"{title} {artist} 뮤직 비디오"
            search_response = youtube.search().list(
                q=search_query,
                type='video',
                part='id',
                maxResults=1
            ).execute()

            videos = search_response.get('items', [])
            if videos:
                video_id = videos[0]['id']['videoId']
                play_url = f'https://www.youtube.com/watch?v={video_id}'

                response_data = {
                    'title': title,
                    'artist': artist,
                    'play_url': play_url
                }

                # Content-Type 헤더 설정
                return jsonify(response_data), 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return jsonify({"message": "YouTube에서 노래를 찾을 수 없습니다."}), 404
        else:
            return jsonify({"message": "해당 감정에 대한 음악을 찾을 수 없습니다."}), 404
    else:
        return jsonify({"message": "감정을 지정해주세요."}), 400

@app.route('/post_music', methods=['POST'])
def post_music():
    # POST로 음악 정보를 받아옴
    music_data = request.get_json()

    if music_data:
        # 받아온 음악 정보를 처리 (예: 저장하거나 다른 동작을 수행)
        # ...

        return jsonify({"message": "음악 정보를 성공적으로 처리했습니다."})
    else:
        return jsonify({"message": "음악 정보를 받을 수 없습니다."}), 400

if __name__ == '__main__':
    fetch_music_data()  # 음악 데이터를 초기화
    app.run(debug=True)
