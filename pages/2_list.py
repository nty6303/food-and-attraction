import streamlit as st

# 세션 상태에서 저장된 음식점 목록 직접 가져오기
if "selected_restaurants" not in st.session_state or not st.session_state.selected_restaurants:
    if st.button("List 없음"):
        st.switch_page("app.py")
    st.stop()

# 세션 상태에서 바로 음식점 목록 가져오기
for r in st.session_state.selected_restaurants:
    st.markdown(f"### {r.name}")
    st.write(f"**대표 메뉴:** {r.menu}")
    st.write(f"**주소:** {r.address}")
    st.write(f"**전화번호:** {r.phone}")
    st.write(f"**휴무일:** {r.holiday}")
    st.write(f"**운영 시간:** {r.hours}")
    st.write(f"**설명:** {r.description}")
    st.write("")

    # 삭제 버튼 추가
    if st.button(f"삭제 {r.name}", key=f"delete_{r.name}"):
        # 음식점 리스트에서 해당 음식점 제거
        st.session_state.selected_restaurants = [
            res for res in st.session_state.selected_restaurants if res.name != r.name
        ]
        st.success(f"{r.name}이(가) 목록에서 삭제되었습니다.")

        # 페이지 새로 고침
        st.rerun()  # 페이지 새로 고침