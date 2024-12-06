# 터미널에서 실행: streamlit run app.py
import streamlit as st
from openai import OpenAI
import json

# OpenAI API 클라이언트 초기화
api_key = "sk-"
client = OpenAI(api_key=api_key)

# Restaurant 클래스 정의
class Restaurant:
    def __init__(self, name, menu, category, address, phone, holiday, hours, description):
        self.name = name
        self.menu = menu
        self.category = category
        self.address = address
        self.phone = phone
        self.holiday = holiday
        self.hours = hours
        self.description = description

    def __repr__(self):
        return (f"Restaurant(name='{self.name}', menu='{self.menu}', "
                f"category='{self.category}', address='{self.address}', "
                f"phone='{self.phone}', holiday='{self.holiday}', "
                f"hours='{self.hours}', description='{self.description}')")

    def to_dict(self):
        return {
            "name": self.name,
            "menu": self.menu,
            "category": self.category,
            "address": self.address,
            "phone": self.phone,
            "holiday": self.holiday,
            "hours": self.hours,
            "description": self.description,
        }

# 음식점 추천 함수
def get_related_restaurants(query, restaurants, client, model="gpt-4o-mini"):
    restaurant_data = [r.to_dict() for r in restaurants]

    messages = [
        {"role": "system", "content": "You are a helpful assistant for recommending restaurants."},
        {"role": "user", "content": f"""
        아래는 음식점 데이터입니다. 사용자가 '{query}'에 관련된 음식점을 3개 추천해주세요.
        추천 결과는 JSON 형식으로 반환하며, 각 음식점에는 다음 필드가 있어야 합니다:
        - name (음식점 이름)
        - menu (대표 메뉴)
        - category (음식 종류)
        - address (주소)
        - phone (전화번호)
        - holiday (휴무일)
        - hours (운영 시간)
        - description (설명)

        JSON 형식으로만 답변해주세요. 예:
        [
            {{
                "name": "음식점1",
                "menu": "메뉴1",
                "category": "한식",
                "address": "주소1",
                "phone": "전화번호1",
                "holiday": "휴일1",
                "hours": "운영 시간1",
                "description": "설명1"
            }},
            ...
        ]

        음식점 데이터:
        {restaurant_data}
        """}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    # 응답 내용 가져오기
    answer = response.choices[0].message.content

    # 불필요한 코드 블록 제거
    cleaned_answer = answer.strip("```").strip("json").strip()

    try:
        recommendations = json.loads(cleaned_answer)
    except json.JSONDecodeError as e:
        st.error(f"JSON 파싱 오류: {e}")
        st.write(f"원본 응답: {answer}")  # 디버깅용 출력
        st.write(f"클린된 응답: {cleaned_answer}")  # 클린한 응답 확인
        return []

    return [
        Restaurant(
            name=item["name"],
            menu=item["menu"],
            category=item["category"],
            address=item["address"],
            phone=item["phone"],
            holiday=item["holiday"],
            hours=item["hours"],
            description=item["description"]
        )
        for item in recommendations
    ]



# 세션 상태 초기화
if "selected_restaurants" not in st.session_state:
    st.session_state.selected_restaurants = []

# Streamlit UI 구성
st.title("음식점 추천 시스템")

# 테스트용 음식점 데이터
restaurants = [
    Restaurant("맛있는 김밥", "김밥, 떡볶이", "한식", "서울 강남구", "010-1234-5678", "일요일", "10:00-20:00", "정성껏 만든 김밥과 떡볶이"),
    Restaurant("이탈리아노", "파스타, 피자", "양식", "서울 종로구", "010-8765-4321", "월요일", "11:00-22:00", "정통 이탈리안 요리를 제공합니다"),
    Restaurant("스시야", "스시, 사시미", "일식", "서울 마포구", "010-5555-6666", "화요일", "12:00-23:00", "신선한 재료로 만든 스시와 사시미"),
    Restaurant("중화반점", "짜장면, 짬뽕", "중식", "서울 송파구", "010-3333-4444", "없음", "11:00-21:00", "오랜 전통의 중화 요리"),
    Restaurant("베트남 쌀국수", "쌀국수, 반미", "베트남 요리", "서울 강동구", "010-2222-1111", "수요일", "09:00-18:00", "현지의 맛을 살린 베트남 요리"),
]

# 카테고리 선택 옵션
categories = ["모든 음식점", "한식", "양식", "일식", "중식", "베트남 요리"]
selected_category = st.radio("카테고리를 선택하세요:", categories)

# 선택된 카테고리에 따라 음식점 필터링
if selected_category and selected_category != "모든 음식점":
    filtered_restaurants = [r for r in restaurants if r.category == selected_category]
else:
    filtered_restaurants = restaurants

# 사용자 입력
query = st.text_input("원하는 음식 키워드를 입력하세요 (예: 떡볶이, 파스타):")

# 버튼 클릭 시 추천 실행
if st.button("추천받기"):
    if query.strip():
        with st.spinner("추천을 가져오는 중..."):
            related_restaurants = get_related_restaurants(query, filtered_restaurants, client)
        
        if related_restaurants:
            st.success(f"'{selected_category}' 카테고리에서 추천 음식점을 찾았습니다!")
            for r in related_restaurants:
                col1, col2 = st.columns([4, 1])  # 카드와 체크박스 배치
                with col1:
                    st.markdown(f"### {r.name}")  # 음식점 이름
                    st.write(f"**대표 메뉴:** {r.menu}")
                    st.write(f"**주소:** {r.address}")
                    st.write(f"**전화번호:** {r.phone}")
                    st.write(f"**휴무일:** {r.holiday}")
                    st.write(f"**운영 시간:** {r.hours}")
                    st.write(f"**설명:** {r.description}")
                with col2:
                    # 체크박스 상태 관리
                    checked = st.checkbox("선택", key=f"checkbox_{r.name}")

                    if checked and r.name not in [res.name for res in st.session_state.selected_restaurants]:
                        st.session_state.selected_restaurants.append(r)
                    elif not checked and r.name in [res.name for res in st.session_state.selected_restaurants]:
                        st.session_state.selected_restaurants = [
                            res for res in st.session_state.selected_restaurants if res.name != r.name
                        ]
        else:
            st.warning("관련 음식점을 찾을 수 없습니다.")
    else:
        st.error("키워드를 입력해주세요.")
