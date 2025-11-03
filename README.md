# AI 옷차림 & 날씨 추천 웹서비스

**실시간 날씨 데이터를 기반으로 인공지능이 옷차림과 우산 챙김 여부를 추천하는 Flask 웹서비스**  
OpenWeather API와 Google Gemini 모델을 활용하여 사용자에게 맞춤형 생활 정보를 제공합니다.

---

## 1. 프로젝트 개요

최근 일교차가 커지고 갑작스러운 비나 추위로 옷차림을 고민하는 일이 많아졌습니다.  
이를 해결하기 위해, 사용자가 도시를 선택하면 해당 지역의 실시간 날씨 데이터를 바탕으로  
AI가 적절한 옷차림과 우산 필요 여부를 안내하는 서비스를 개발했습니다.

---

## 2. 주요 기능

- **실시간 날씨 조회**: OpenWeather API를 이용해 도시별 현재 기온과 날씨 정보를 가져옵니다.  
- **AI 텍스트 생성**: Google Gemini 모델이 날씨 조건에 맞는 문장형 옷차림/우산 추천을 생성합니다.  
- **Flask 웹 인터페이스**: 간결한 웹 UI로 사용자가 도시를 선택하고 결과를 즉시 확인할 수 있습니다.   

---

## 3. 기술 스택

| 구분 | 사용 기술 |
|------|------------|
| Backend | Python 3.10, Flask |
| AI Model | Google Gemini API |
| Data Source | OpenWeather API |
| Frontend | HTML, CSS (Jinja2 Template) |
| Hosting | PythonAnywhere |
| Version Control | Git, GitHub |

---

## 4. 시스템 구조

사용자 입력 (도시 선택)
↓
OpenWeather API 호출 → 실시간 기온 / 날씨 데이터 수집
↓
Gemini 모델 프롬프트 생성
↓
AI 추천 문장 생성 (옷차림 / 우산 여부)
↓
Flask 웹페이지에 결과 출력

---

## 5. 구현 과정 요약

1. Flask 서버 구축 및 OpenWeather API 연동  
2. Gemini API를 활용한 자연어 프롬프트 설계  
3. 옷차림 추천과 우산 추천을 분리된 프롬프트로 구성  
4. HTML 템플릿으로 결과 표시 및 감성형 디자인 적용  
5. PythonAnywhere를 이용한 웹 배포 및 외부 접근 가능 상태 구현  

---

## 6. 주요 코드 예시

```python
def generate_outfit_recommendation(temp, desc, city):
    outfit_prompt = f"""
    현재 {city}의 기온은 {temp}도이며, 날씨는 {desc}입니다.
    기온대에 맞는 옷차림을 문어체로 3줄 이내로 제안해주세요.
    예: 28도 이상 → 반팔, 민소매 / 23~27도 → 얇은 셔츠, 면바지 / ...
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(outfit_prompt)
    return response.text.strip()
