import streamlit as st
from openai import OpenAI
 
# OpenAI API 키 설정
api_key = "sk-"
client = OpenAI(api_key=api_key)

# Streamlit 앱 제목
st.title("부산 관광 동선 추천")

# 사용자로부터 관광지 입력받기
st.subheader("부산에서 방문하고 싶은 관광지를 입력하세요.")
tourist_spots = st.text_area(
    "관광지를 2개 이상 입력하세요 (예: 해운대, 감천문화마을, 광안리)",
    placeholder="여기에 입력하세요.",
)

# 버튼 클릭 시 실행
if st.button("동선 추천받기"):
    if len(tourist_spots.split(',')) < 2:
        st.error("관광지를 2개 이상 입력해주세요!")
    else:
        with st.spinner("동선을 생성 중입니다..."):
            try:
                # OpenAI API 호출
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "너는 여행 플래너야. 주어진 관광지를 기반으로 최적의 여행 동선을 제안해줘."
                        },
                        {
                            "role": "user",
                            "content": f"다음 관광지를 방문할 계획이야: {tourist_spots}. 최적의 동선을 짜줘."
                        }
                    ]
                )
                # 응답 처리
                answer = response.choices[0].message.content
                st.success("동선 추천 결과:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")