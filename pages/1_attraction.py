import streamlit as st
from openai import OpenAI
import json


# 세션 상태에 저장된 음식점 목록 출력
if "selected_restaurants" in st.session_state:
    client = st.session_state.get('selected_restaurants', None)
    st.write(client)
else:
    st.write("선택된 음식점이 없습니다.")
