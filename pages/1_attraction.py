# 터미널에서 실행: streamlit run app.py
import streamlit as st
from openai import OpenAI
import json

# OpenAI API 클라이언트 초기화
api_key = "sk-"
client = OpenAI(api_key=api_key)

# Restaurant 클래스 정의
class Restaurant:
    def __init__(self, name, category, address, phone, hours, description):
        self.name = name
        self.category = category
        self.address = address
        self.phone = phone
        self.hours = hours
        self.description = description

    def __repr__(self):
        return (f"Restaurant(name='{self.name}', "
                f"category='{self.category}', address='{self.address}', "
                f"phone='{self.phone}', hours='{self.hours}', "
                f"description='{self.description}')")

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "address": self.address,
            "phone": self.phone,
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
        - category (음식 종류)
        - address (주소)
        - phone (전화번호)
        - hours (운영 시간)
        - description (설명)

        JSON 형식으로만 답변해주세요. 예:
        [
            {{
                "name": "음식점1",
                "category": "한식",
                "address": "주소1",
                "phone": "전화번호1",
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
            category=item["category"],
            address=item["address"],
            phone=item["phone"],
            hours=item["hours"],
            description=item["description"]
        )
        for item in recommendations
    ]

if 'selected_restaurants' not in st.session_state:
    st.session_state['selected_restaurants'] = []

# Streamlit UI 구성
st.title("음식점 추천 시스템")

# 테스트용 음식점 데이터
restaurants = [
    Restaurant("남촌", "그릴", "북구 금곡대로8번길 14", "051-335-9294", "10:00-22:00", "청정지역인 지리산 아래 산청의 흑돼지만 사용하고 있는 믿을 수 있는 돼지구이전문점이다. 사용되는 흑돼지 자체가 일반적인 돼지고기와 식감과 맛의 차이가 많이 나며, 껍데기가 붙어 있는 오겹살 흑돼지 고기를 쓰는 것이 특징이다.")
]

# 카테고리 선택 옵션
categories = ["전체", "한식", "중식", "일식", "아세안요리", "양식", "카페&베이커리", "해산물", "그릴"]
selected_category = st.radio("카테고리를 선택하세요:", categories)

# 선택된 카테고리에 따라 음식점 필터링
if selected_category and selected_category != "전체":
    filtered_restaurants = [r for r in restaurants if r.category == selected_category]
else:
    filtered_restaurants = restaurants

# 사용자 입력
query = st.text_input("원하는 음식(점)을 알려주세요")

# 추천받기 버튼 클릭 시 로직
if st.button("추천받기"):
    if query.strip():
        with st.spinner("추천을 가져오는 중..."):
            related_restaurants = get_related_restaurants(query, filtered_restaurants, client)

        if related_restaurants:
            st.success(f"'{selected_category}' 카테고리에서 추천 음식점을 찾았습니다!")

            for r in related_restaurants:
                st.markdown(f"### {r.name}")
                st.write(f"**주소:** {r.address}")
                st.write(f"**전화번호:** {r.phone}")
                st.write(f"**운영 시간:** {r.hours}")
                st.write(f"**설명:** {r.description}")
                st.write("")
                if r.name not in [res.name for res in st.session_state.selected_restaurants]:
                    st.session_state.selected_restaurants.append(r)
        else:
            st.warning("관련 음식점을 찾을 수 없습니다.")
    else:
        st.error("키워드를 입력해주세요.")

if st.button("List 보기"):
        st.switch_page("pages/2_list.py")