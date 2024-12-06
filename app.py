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

if 'selected_restaurants' not in st.session_state:
    st.session_state['selected_restaurants'] = []

# Streamlit UI 구성
st.title("부산 음식점 추천 시스템")

# 테스트용 음식점 데이터
restaurants = [
    Restaurant("60년 전통 할매국밥", "따로 국밥, 수육백반", "한식", "동구 중앙대로533번길 4", "051-646-6295", "일요일", "10:00-19:00", "60년 전통의 돼지국밥 전문점으로 식사 시간에는 30분 이상을 기다려야 하는 유명한 식당이다. 대부분의 돼지국밥들과는 다른 맑은 국물이 특징이며, 대충 썬 것 같은 돼지 수육은 예상외로 부드러운 맛이다. 돼지국물과 고기가 따로 나오는 수육백반이 특히 인기 있다."),
    Restaurant("예이제", "런치, 예이제 코스", "한식", "부산 해운대구 해운대해변로298번길 29 해운대푸르지오시티 2층", "051-731-1100", "명절", "12:00-15:00 / 17:30-21:20", "해운대 해변인근에 위치한 한정식전문점으로, 가족모임이나 손님 대접 등으로 많이 찾는 곳이다. 주인이 직접 고른 제철 식재료와 지인이 운영하는 농장에서 키운 채소를 사용하는이 곳은 먹는 것이 고민스러울 정도로 예쁜 음식이 특징이다."),
    Restaurant("국제밀면본점", "물밀면, 비빔밀면", "한식", "연제구 중앙대로1235번길 23-6", "051-501-5507", "명절", "10:00-20:00 / 4~9월 10:00-21:00", "밀면전문점 중에서도 특히 맛으로 소문난 이곳은 소 사골만을 사용한 육수 등 독창적인 방식의 밀면을 만들고 있다. 보통 기계로 잘려진 편육이 고명으로 올려지는데, 이곳은 손으로 일일이 얇게 찢은 양지머리 고기가 올려지는 것이 특징이다."),
    Restaurant("석화정", "굴국밥, 생굴", "한식", "영도구 동삼로 42번길 16-11", "070-8913-9989", "명절", "09:00-21:00", "20여 년을 운영해 온 굴요리 전문점으로, 제철 생굴, 굴구이, 굴튀김, 굴파전, 굴김치 등 굴을 이용한 다양한 음식들을 즐길 수 있다. 특히 대표메뉴인 굴국밥은 신선한 자연산 굴을 사용하여, 깔끔하고 풍부한 맛으로 인기 있다"),
    Restaurant("식당 3선 덕천점", "양념돼지갈비(330g), 고추장돼지갈비(330g)", "한식", "부산 북구 금곡대로 112", "051-333-0050", "없음", "11:00-22:00", "숯불구이, 파삼겹구이, 밀면 등을 맛볼 수 있는 식당인 이곳은 나이와 취향에 관계없이 즐길 수있는 대중적인 맛이 특징으로, 넓은 공간을 가지고 있어 가족외식장소로 인기 있다. 메인요리인 숯불구이는 조리되어 제공되어서 먹기 편하다."),
    Restaurant("금수복국 해운대본점", "은복국 (지리 / 탕), 밀복국 (지리 / 탕)", "한식", "해운대구 중동1로 43번길23", "0507-1334-3600", "없음", "금수복국 00:00-24:00 / 복요리 전문점 11:00-22:00", "복국의 원조라 할 수 있는 50년 전통의 복요리집으로, 신선한 원재료와 정확한 물류 시스템, 모든 장류는 직접 담아 사용하는 것이 맛의 비결이라고 한다. 24시간 영업하는 곳."),
    Restaurant("해남식당 부산용호동W스퀘어점", "묵은지수육한판, 옛날김치찌개", "한식", "부산광역시 남구 분포로 145 1072,1073호(용호동, 더블유) 용호동 더블유스퀘어", "051-628-2015", "명절", "11:30-21:00", "김치요리전문식당인 이 곳은 배추산지로 유명한 해남의 배추를 사용 하여, 오랜 시간 숙성시킨 묵은지를 사용하는 것이 특징이며, 다양한 김치요리를 먹을 수 있다. 해남묵은지에 대한 높은 자부심을 가지고 있다."),
    Restaurant("얼크니손칼국수", "얼크니손칼국수, 만두", "한식", "부산 기장군 기장읍 차성로 417번길 22", "051-721-3487", "없음", "11:20-21:30", "간단히 준비된 샤브샤브를 먹은 후 직접 면을 넣고 조리해 먹는 칼국수 가격에 비해 푸짐한 재료들이 특징이다. 먼저 샤브샤브를 먹고 그 국물에 칼국수를 만들어 먹고 나면, 점원이 볶음밥을 만들어 준다."),
    Restaurant("한우숯불양곱창", "특양(200g), 전골", "한식", "부산 해운대구 해운대해변로 385", "051-741-8969", "없음", "16:00-22:00", "해운대 중동역 인근의 양곱창 전문점인 이 곳은 특히 소의 첫 번째 위인 특양 양념구이가 유명하다. 주문과 동시에 특제양념을 발라, 점원이 구워주는 이 곳의 특양 구이는 무척 부드 러우면서도 살짝 탄력 있는 식감이 특징이다."),
    Restaurant("편의방", "삼선만두, 군만두", "중식", "서구 대신공원로 13-5", "051-256-2121", "월요일", "11:00-21:00", "빨간 간판이 눈에 띄는 이곳은 3대째 이어오는 중국만두전문점으로, 하루에 40인분 한정에, 30분 전에 미리 전화로 주문해야 한다는 삼선만두가 유명한 곳이다. 주문과 동시에 만드는 삼선만두는 각종야채와 새우가 가득 차 육즙이 흘러넘친다."),
    Restaurant("북경의 자전거", "짜장면, 탕수육", "중식", "부산광역시 북구 용당로5번길 14", "051-902-8282", "없음", "11:30-22:30", "본격적인 중국풍의 인테리어가 특색있는 이 중식당은 중국인 쉐프들이 요리하고 있는 것으로 유명하다. 사용되는 면은 전통방식인 수타로 만들고, 다양하고 많은 종류의 요리들을 만드는 단골 손님이 많은 가게이다."),
    Restaurant("신흥반점", "짬뽕, 자장면, 깐풍기, 삼선볶음밥", "중식", "서구 충무대로 284-1", "051-242-6164", "일요일", "11:00-20:00", "2대째 운영 중인 신흥반점은 서구에서 55년 동안 화교 가족들이 운영해오고 있는 곳으로, 중국 현지의 식당 같은 분위기의 가게에서 다양한 중국요리를 맛 볼 수 있다. 짬뽕국물과 깐풍기가 이 곳에서 추천하는 인기 메뉴이다."),
    Restaurant("반핀 서면전포점", "차슈덮밥, 마파두부", "중식", "부산진구 동천로 108번길 9", "0507-1498-6223", "없음", "11:30-16:00 / 17:00-21:00", "대만음식을 베이스로한 캐주얼한 메뉴로 젊은 층에 인기 높은 이 곳은 비장탄 숯불을 사용한 덮밥이 인기메뉴이다. 간단한 요리메뉴도 있어 식사나 맥주와도 잘 어울린다."),
    Restaurant("삼형제오리 부산1호점", "양꼬치 2인, 오리바베큐", "중식", "영도구 태종로 73번길 23", "051-417-7043", "없음", "17:00-23:00", "중국 현지 북경오리 프랜차이즈의 국내 유일 지점으로 숯불에 구운 오리바베큐가 대표메뉴지만, 양갈비살로 만든 양꼬치도 인기 있다. 오리바베큐를 먹기 위해선 예약이 필수다."),
    Restaurant("문스시", "오마카세 문 스시, 오마카세 스 스시", "일식", "부산 해운대구 좌동순환로 43", "051-744-3316", "없음", "11:30-15:00 / 17:30-22:00", "TV프로그램을 통해 소개된 유명 쉐프가 운영하는 일식전문점으로, 기대를 충족하는 수준 있는 요리들과 깔끔하고 세련된 인테리어가 특징이다. 쉐프가 추천하는 음식으로 구성되는 오마카세 스시 코스가 특히 유명하다."),
    Restaurant("영변횟집", "세꼬시(넙치), 모듬회", "일식", "부산 해운대구 송정강변로 15", "051-703-7590", "없음", "11:00 ~ 21:00", "뼈와 함께 먹는 잘게 썬 세꼬시가 특히 유명한 생선회전문점으로, 도다리, 광어, 우럭, 돌돔, 농어 등 다양한 활어를 철에 따라 즐길 수 있다. 특히 가자미나 광어를 이용한 세꼬시가 인기 메뉴로 회를 주문하면 상을 꽉 채우는 반찬과 해산물 등이 함께 제공된다."),
    Restaurant("젠스시", "디너 1인, 콜 키지 병당", "일식", "해운대구 대천로42번길28-5", "051-746-7456", "월, 화요일", "18:00-22:00", "해운대의 유명 일식전문점으로, 명인 인증서를 받은 오너 쉐프가 운영하며, 주방 분위기가 엄격하고, 위생에 무척 신경을 쓰는 것으로도 유명하다. 열 가지의 초밥과 함께 미소시루, 달걀 찜, 튀김 등으로 구성 된 코스요리가 대표메뉴"),
    Restaurant("식당 토성동", "한입 스테이크 덮밥, 돈카츠정식", "일식", "부산 서구 구덕로 124번길 27", "0507-1353-1425", "토요일, 일요일", "10:00-20:30", "의외의 장소에 자리하고 있는 아담하고 예쁜 인테리어의 덮밥전문점으로, 간단한 음식, 깔끔한 맛, 친절한 서비스로 유명한 곳이다. 모든 음식이 인기메뉴이긴 하지만, 손질과 숙성을 거쳐 부드러운 맛의 한입 스테이크 덮밥이 대표메뉴라고 한다."),
    Restaurant("원조18번완당", "발국수, 완당", "일식", "서구 구덕로 238번길 6", "0507-1348-3391", "월요일", "10:30-19:30", "1947년부터 3대를 이어 운영 중인 유명한 식당으로 1대 창업주가 일본에서 배워온 완당을 한국인의 입맛에 맞게 발전시켰다. 부산 음식문화의 한 부분을 장식한 유서 깊은 식당이다."),
    Restaurant("어밤부", "팟타이, 푸팟퐁커리", "아세안요리", "해운대구 송정광어골로 87 1층", "0507-1366-8183", "없음", "11:00-15:00 / 17:00-20:55", "태국풍의 라탄 조명과 송정 해수욕장의 멋진 풍경이 어우러진 태국음식전문점으로, 다양한 태국 음식들과 함께 와인 등의 주류와 다양한 음료도 준비되어 있다."),
    Restaurant("오공떵번", "후띠우, 분짜, 넴", "아세안요리", "승학로 50, 1층", "051-292-4441", "일요일", "11:00-20:00", "한국에서 흔하게 맛볼 수 있는 쌀국수는 ‘포’라는 하노이식 쌀국수라면, 이곳은 ‘후띠우’라는 호치민식 쌀국수를 만들고 있다. ‘포’와는 달리 향이 강하지 않아 누구나 쉽게 즐길 수 있는 맛이다."),
    Restaurant("타이빈", "크랩 팟 퐁 커리, 뿌님 팟 퐁 커리", "아세안요리", "동래구 금강로73번길 12", "051-558-8885", "없음", "11:00-21:50", "태국 정부로부터 Thai select 최고등급인 signature 인증을 받았다는 태국음식전문점으로, 태국인요리사가 준비하는 정통태국음식이 준비되어 있다. 태국으로 여행 온 기분을 느끼게 해주는 인테리어가 무척 인상적인 곳이다."),
    Restaurant("이재모피자 본점", "치즈크러스트피자, 오븐스파게티", "양식", "중구 광복중앙로 31", "051-255-9494", "일요일", "10:00-21:10", "30여년을 운영 중인 피자전문점으로 부산에서 피자가 대중화된 시기를 생각하면 상당한 전통을 자랑하는 유명한 곳이다. 국내산 임실치즈를 사용한 푸짐한 토핑의 피자가 특징이며, 변함없는 맛을 지키고 있다."),
    Restaurant("다이닝센 부산본점", "쇠고기 찹스테이크 샐러드, 목살필라프", "양식", "부산 남구 용호로 88 3층,4층", "0507-1319-8833", "없음", "11:00-22:00", "패밀리레스토랑 다이닝센은 직접 만드는 소스들을 사용하고, 비교적 저렴한 가격에 비해 높은 수준의 음식들이 제공된다. 행사를 위한 시설과 공간도 잘 준비되어 있다."),
    Restaurant("버거샵 서면", "클래식버거, 베이컨치즈", "양식", "부산진구 동천로 108번길 11", "부산진구 동천로 108번길 11", "없음", "11:00-20:30", "직접 손질하는 1등급 한우 패티와 매일 아침 구운 브리오슈 번으로 만드는 수제버거전문점으로, 외국인 손님들도 많이 찾는 곳이다. 독특한 인테리어를 즐기며 다양한 소품들도 구입하고 볼 수 있는 가게이다."),
    Restaurant("초량 1941", "바닐라우유, 생강우유", "카페&베이커리", "동구 망양로 533-5", "051-462-7774", "없음", "10:30-18:00", "동구의 관광명소인 ‘이바구길’에 위치한 이 카페는 1941년 당시 부산에 살던 일본인에 의해 지어진 집을 개조한 곳으로, 주변 환경을 포함해 외관도 실내도 모두 1941년을 연상시 키는 레트로한 감성을 가지고 있다. 메인메뉴는 자체개발한 예쁜 병에 담겨있는 다양한 ‘우유’이다."),
    Restaurant("홍옥당", "단팥빵, 단팥죽", "카페&베이커리", "부산 수영구 남천동로 108번길 49", "051-627-1026", "없음", "10:00-21:00", "광안리해수욕장 앞 골목길에 위치한 아담한 이 가게는 국산 팥만을 사용하여 음식들을 만드는 팥전문점이다. 팥빙수와 단팥죽, 단팥빵이 유명한데, 특히 단팥빵의 인기가 높아 빵을 사가려는 사람들의 줄이 길게 늘어서곤 한다."),
    Restaurant("파니니브런치본점", "아메리칸브런치, 아메리카노", "카페&베이커리", "사상구 엄궁남로 15", "0507-1332-2292", "월요일", "10:00-18:00", "주택을 개조하여 만든 예쁜 외관의 브런치카페로, 휴일과 잘 어울릴 것 같은 화사한 실내와창 너머에 보이는 화단이 인상적이다. 아메리칸 브런치, 불고기파니니, 맥앤치즈파니니, 부리또 브런치, 리코타샐러드 등이 인기 있는 메뉴이다."),
    Restaurant("만호갈미샤브샤브", "갈미샤브샤브, 갈미조개삼겹살", "해산물", "강서구 르노삼성대로 602", "051-271-4389", "2, 4주 월요일", "11:00-21:00", "샤브샤브, 수육, 구이 등 다양한 방식으로 갈미조개를 요리하는 갈미조개 전문 식당. 국물이 맛있기로 유명한 이곳은 갈미샤브샤브와 갈미수육이 대표메뉴이다."),
    Restaurant("국이네낙지볶음", "낙곱새(낙지/곱창/새우볶음), 각종 사리", "해산물", "수영구 연수로 410", "051-754-7776", "없음", "10:30-22:00", "푸짐한 재료와 자극적이지 않은 맛으로 인기 있는 낙지볶음전문점으로 부산의 쟁쟁한 낙지볶음전문점들 사이에서 신흥강자로 떠오른 곳이다. 반찬들은 모두 셀프리필이 가능하고, 직원들이 항상 친절한 것으로도 유명하다"),
    Restaurant("무궁화", "전골요리", "해산물", "황령산로8번길 5", "051-623-5700", "월요일", "11:30-21:00", "할머니집에 놀러온 것 같은 느낌을 주는 이곳은 전골요리로 무척 유명한 식당으로, 직접 만든 커다란 만두를 사용한 만두전골이 특히 인기 있다. 신선한 야채를 사용하는 이곳은 항상 변함없는 맛으로 기억되는 곳이기도 하다."),
    Restaurant("거대갈비", "등심(100g), 생갈비(100g)", "그릴", "해운대구 달맞이길 22", "051-746-0037", "없음", "11:30-15:00 / 17:00-22:00", "최상등급의 고기와 최고의 원재료만을 사용한다는 한우숯불구이전문점으로, 깔끔한 실내와 친절한 점원들이 인상적이다. 최상등급의 한우인만큼 가격도 높은 편이지만, 직원이 고기를 구워주는 등 만족도가 높은 식당이다"),
    Restaurant("오륙도 가원", "특수부위, 한우모음", "그릴", "남구 백운포로 14", "051-635-0707", "명절", "11:30-21:30", "건축상을 받은 아름다운 외관과 잘 가꾸어진 넓은 잔디정원이 인상적이다. 이곳은 유명한 한우숯불구이 전문식당으로, 제공되는 음식과 서비스 등 모든 것이 무척 고급스럽다"),
    Restaurant("남촌", "흑돼지", "그릴", "북구 금곡대로8번길 14", "051-335-9294", "명절", "10:00-22:00", "청정지역인 지리산 아래 산청의 흑돼지만 사용하고 있는 믿을 수 있는 돼지구이전문점이다. 사용되는 흑돼지 자체가 일반적인 돼지고기와 식감과 맛의 차이가 많이 나며, 껍데기가 붙어 있는 오겹살 흑돼지 고기를 쓰는 것이 특징이다.")
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
                st.write(f"**대표 메뉴:** {r.menu}")
                st.write(f"**주소:** {r.address}")
                st.write(f"**전화번호:** {r.phone}")
                st.write(f"**휴무일:** {r.holiday}")
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