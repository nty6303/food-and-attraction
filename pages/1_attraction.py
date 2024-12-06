# 터미널에서 실행: streamlit run app.py
import streamlit as st
from openai import OpenAI
import json

# OpenAI API 클라이언트 초기화
api_key = "sk-"
client = OpenAI(api_key=api_key)

# Attraction 클래스 정의
class Attraction:
    def __init__(self, name, category, address, phone, hours, description):
        self.name = name
        self.category = category
        self.address = address
        self.phone = phone
        self.hours = hours
        self.description = description

    def __repr__(self):
        return (f"Attraction(name='{self.name}', "
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

# 명소 추천 함수
def get_related_Attractions(query, Attractions, client, model="gpt-4o-mini"):
    Attraction_data = [a.to_dict() for a in Attractions]

    messages = [
        {"role": "system", "content": "You are a helpful assistant for recommending attractions."},
        {"role": "user", "content": f"""
        아래는 명소 데이터입니다. 사용자가 '{query}'에 관련된 명소를 3개 추천해주세요.
        추천 결과는 JSON 형식으로 반환하며, 각 명소에는 다음 필드가 있어야 합니다:
        - name (명소 이름)
        - category (명소 종류)
        - address (주소)
        - phone (전화번호)
        - hours (운영 시간)
        - description (설명)

        JSON 형식으로만 답변해주세요. 예:
        [
            {{
                "name": "명1",
                "category": "역사",
                "address": "주소1",
                "phone": "전화번호1",
                "hours": "운영 시간1",
                "description": "설명1"
            }},
            ...
        ]

        명소 데이터:
        {Attraction_data}
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
        Attraction(
            name=item["name"],
            category=item["category"],
            address=item["address"],
            phone=item["phone"],
            hours=item["hours"],
            description=item["description"]
        )
        for item in recommendations
    ]

if 'selected_Attractions' not in st.session_state:
    st.session_state['selected_Attractions'] = []

# Streamlit UI 구성
st.title("부산 명소 추천 시스템")

# 테스트용 명소 데이터
Attractions = [
    Attraction("겨울 철새의 아름다움을 만나는 ‘명지철새탐조대’", "자연", "부산 강서구 명지오션시티1로 284", "051-970-4000", "없음", "명지철새탐조대는 매년 150여 종의 겨울 철새가 찾는 도래지로, 갯벌에서 철새들의 생동감 넘치는 모습을 관찰할 수 있는 생태학습 명소입니다. 망원경과 안내 표지판이 마련되어 있어 탐조의 즐거움을 더하며, 일몰과 함께 황금빛 자연 풍경을 감상할 수 있는 힐링 장소로도 유명합니다.")
]

# 카테고리 선택 옵션
categories = ["전체", "자연", "역사", "문화", "공원"]
selected_category = st.radio("카테고리를 선택하세요:", categories)

# 선택된 카테고리에 따라 명소 필터링
if selected_category and selected_category != "전체":
    filtered_Attractions = [r for r in Attractions if r.category == selected_category]
else:
    filtered_Attractions = Attractions

# 사용자 입력
query = st.text_input("원하는 명소를 알려주세요")

# 추천받기 버튼 클릭 시 로직
if st.button("추천받기"):
    if query.strip():
        with st.spinner("추천을 가져오는 중..."):
            related_Attractions = get_related_Attractions(query, filtered_Attractions, client)

        if related_Attractions:
            st.success(f"'{selected_category}' 카테고리에서 추천 명소를 찾았습니다!")

            for r in related_Attractions:
                st.markdown(f"### {r.name}")
                st.write(f"**주소:** {r.address}")
                st.write(f"**전화번호:** {r.phone}")
                st.write(f"**운영 시간:** {r.hours}")
                st.write(f"**설명:** {r.description}")
                st.write("")
                if r.name not in [res.name for res in st.session_state.selected_Attractions]:
                    st.session_state.selected_Attractions.append(r)
        else:
            st.warning("관련 명소를 찾을 수 없습니다.")
    else:
        st.error("키워드를 입력해주세요.")

if st.button("List 보기"):
        st.switch_page("pages/2_list.py")