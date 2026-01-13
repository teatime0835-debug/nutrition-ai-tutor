# ===============================
# Streamlit 기본 설정 (반드시 최상단)
# ===============================
import streamlit as st

st.set_page_config(
    page_title="청소년 AI 영양 튜터",
    page_icon="🍱",
    layout="centered"
)

st.title("🍱 청소년 AI 영양 튜터")
st.info("오늘 먹은 급식 사진을 올리면 2020 한국인 영양소 섭취기준에 맞춰 분석해 드립니다.")

# ===============================
# 라이브러리
# ===============================
from PIL import Image
import os

# Gemini는 try-except로 보호
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

# ===============================
# Gemini 설정 (API 키는 환경변수)
# ===============================
MODEL_READY = False

if GEMINI_AVAILABLE:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        MODEL_READY = True
    else:
        st.warning("⚠️ Gemini API 키가 설정되지 않았습니다.")

# ===============================
# 파일 업로드
# ===============================
uploaded_file = st.file_uploader(
    "📷 음식 사진 업로드 (JPG, PNG)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="업로드된 식단 사진", use_container_width=True)

    if MODEL_READY and st.button("🚀 영양 분석 리포트 생성"):
        with st.spinner("AI 영양사가 데이터를 분석 중입니다..."):
            try:
                final_prompt = """
너는 대한민국 청소년 식생활 교육 전문가이자 영양사야.
제시된 사진 속 음식을 분석해서 다음 양식에 맞춰 한국어로 출력해줘.
반드시 '2020 한국인 영양소 섭취기준' 중 청소년(만 12~18세) 권장량을 기준으로 해줘.

### 📊 오늘의 식단 분석 리포트

1. 인식된 메뉴: [메뉴명1, 메뉴명2...]

2. 영양 성분 데이터:
| 영양소 | 추정량 | 권장량 대비 상태 |
| :--- | :--- | :--- |
| 칼로리 | 000 kcal | 적정/부족/과잉 |
| 탄수화물 | 00 g | 상태 |
| 단백질 | 00 g | 상태 |
| 지방 | 00 g | 상태 |

3. 💡 맞춤형 영양 튜터링
- 현재 식단의 교육적 장점 기술
- 다음 식사에서 보완하면 좋은 식품 제안
- 청소년기 영양 섭취의 중요성에 대한 짧은 조언
"""

                response = model.generate_content([final_prompt, image])
                st.markdown("---")
                st.markdown(response.text)
                st.success("분석이 완료되었습니다!")

            except Exception as e:
                st.error("분석 중 오류가 발생했습니다.")
                st.code(e)

st.markdown("---")
st.caption("© 2026 인공지능융합교육 프로젝트 - 청소년 자기주도적 식단 관리 시스템")
