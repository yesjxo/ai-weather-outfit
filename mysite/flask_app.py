# ----------------------------------------------------
# AI 옷차림 & 날씨 추천
# ----------------------------------------------------
from flask import Flask, request, render_template_string
import requests
import google.generativeai as genai
from datetime import datetime
import pytz

# ----------------------------------------------------
# API Key 설정
# ----------------------------------------------------
OPENWEATHER_KEY = "ad1f9fce7496227b3c8e76412206ec4b"
GEMINI_KEY = "AIzaSyAy8rb9uJ6QAwugYKIsjUV59arHgJL5udc"
genai.configure(api_key=GEMINI_KEY)

app = Flask(__name__)

# ----------------------------------------------------
# 날씨 데이터 가져오기
# ----------------------------------------------------
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric&lang=kr"
    res = requests.get(url)
    return res.json()

# ----------------------------------------------------
# Gemini AI 프롬프트 분리 (옷차림 / 우산)
# ----------------------------------------------------
def generate_outfit_recommendation(temp, desc, city):
    outfit_prompt = f"""
    현재 {city}의 기온은 {temp}도이며, 날씨는 {desc}입니다.
    사용자가 외출을 준비하는 상황을 가정하고,
    기온대에 따라 적절한 옷차림을 제안해주세요.

    - 색상이나 디자인은 언급하지 말고, 옷의 종류와 두께 중심으로 추천하세요.
    - 예: 28도 이상 → 반팔, 민소매 / 23~27도 → 얇은 셔츠, 면바지 / 20~22도 → 긴팔티, 가디건 / 17~19도 → 얇은 니트, 청바지 / 12~16도 → 자켓, 야상, 니트 / 5~11도 → 코트, 목도리 / 0도 이하 → 패딩, 장갑
    - 문체는 따뜻하고 다정한 문어체로 3줄 이내로 작성하세요.
    - 불필요한 감탄사나 인사말은 쓰지 마세요.
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(outfit_prompt)
    return response.text.strip()

def generate_umbrella_recommendation(desc, city):
    umbrella_prompt = f"""
    현재 {city}의 날씨는 '{desc}'입니다.
    오늘 비예보를 고려하여 우산을 챙길 필요가 있는지를 한 줄로만 알려주세요.
    문체는 따뜻하지만 단정하고 간결하게, 예를 들어
    '오늘은 비가 예상되니 작은 우산을 챙기세요.' 또는
    '맑은 날씨라 우산은 필요하지 않습니다.' 와 같은 형식으로 답변하세요.
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(umbrella_prompt)
    return response.text.strip()

# ----------------------------------------------------
# Flask 웹페이지
# ----------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>🌤 AI 옷차림 & 날씨 추천</title>
        <style>
            body {
                background: linear-gradient(to bottom, #a1c4fd, #c2e9fb);
                font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
                text-align: center;
                color: #333;
                margin: 0;
                padding: 0;
            }
            .container {
                background: white;
                border-radius: 24px;
                padding: 45px;
                max-width: 450px;
                margin: 70px auto;
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            }
            h1 {
                font-size: 2em;
                color: #0077b6;
                margin-bottom: 25px;
            }
            select, button {
                font-size: 1em;
                padding: 10px 15px;
                margin-top: 15px;
                border-radius: 10px;
                border: 1px solid #ccc;
            }
            button {
                background-color: #48cae4;
                color: white;
                border: none;
                cursor: pointer;
                transition: 0.3s;
                font-weight: 600;
            }
            button:hover {
                background-color: #0096c7;
            }
            .result-box {
                margin-top: 30px;
                text-align: left;
                background: #f9fbff;
                border-radius: 16px;
                padding: 25px;
                font-size: 0.96em;
                line-height: 1.7em;
                border: 1px solid #d7e3fc;
            }
            hr {
                border: none;
                height: 1px;
                background-color: #eee;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div style="font-size:3em;">🌤️</div>
            <h1>AI 옷차림 & 날씨 추천</h1>
            <form method="POST">
                <label>📍 도시 선택:</label><br>
                <select name="city" required>
                    <option value="Seoul">서울</option>
                    <option value="Busan">부산</option>
                    <option value="Incheon">인천</option>
                    <option value="Daegu">대구</option>
                    <option value="Daejeon">대전</option>
                    <option value="Gwangju">광주</option>
                    <option value="Jeju">제주</option>
                </select><br><br>
                <button type="submit">오늘의 추천 보기 ❤️</button>
            </form>

            {% if result %}
            <div class="result-box">
                <h3>🕒 현재 한국 시각: {{ now }}</h3>
                <p><b>도시:</b> {{ city }}</p>
                <p><b>온도:</b> 🌡️ {{ temp }}°C</p>
                <p><b>날씨:</b> ☁️ {{ desc }}</p>
                <hr>
                <h4>👕 오늘의 AI 옷차림 추천</h4>
                <p>{{ outfit }}</p>
                <h4>🌂 우산 챙김 여부</h4>
                <p>{{ umbrella }}</p>
            </div>
            {% endif %}
        </div>
    </body>
    </html>
    """

    if request.method == "POST":
        city = request.form["city"]
        weather = get_weather(city)
        temp = weather["main"]["temp"]
        desc = weather["weather"][0]["description"]
        outfit = generate_outfit_recommendation(temp, desc, city)
        umbrella = generate_umbrella_recommendation(desc, city)
        now = datetime.now(pytz.timezone("Asia/Seoul")).strftime("%Y-%m-%d %H:%M")

        return render_template_string(
            html, city=city, temp=temp, desc=desc,
            outfit=outfit, umbrella=umbrella, now=now, result=True
        )

    return render_template_string(html, result=False)

if __name__ == "__main__":
    app.run(debug=True)
