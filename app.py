import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# ===============================
# 1. Streamlit 기본 설정 (최우선)
# ===============================
st.set_page_config(
    page_title="청소년 AI 영양 튜터",
    page_icon="🍱",
    layout="centered"
)

st.title("🍱 청소년 AI 영양 튜터")
st.info(
    "📌 이 서비스는 **교육 목적**의 AI 시연입니다.\n\n"
    "- 분석 결과는 **실제 영양소 측정이 아닌 추정치**입니다.\n"
    "- 의료·영양 상담을 대체하지 않습니다."
)

# ===============================
# 2. Gemini API 설정
# ===============================
API_KEY = os.getenv("GEMINI_API_KEY", "여기에_본인_API_KEY")

if not API_KEY or "여기에" in API_KEY:
    st.error("❌ Gemini API 키가 설정되지 않았습니다.")
    st.stop()

genai.configure(api_key=API_KEY)

# 🔐 발표용으로 가장 안전한 모델
model = genai.GenerativeModel("gemini-1.0-pro-vision")

# ===============================
# 3. 이미지 업로드
# ===============================
uploaded_file = st.file_uploader(
    "📷 오늘 먹은 급식 사진 업로드 (JPG, PNG)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="업로드된 식단 사진", use_column_width=True)

    # ===============================
    # 4. 분석 버튼
    # ===============================
    if st.button("🚀 영양 분석 리포트 생성"):
        with st.spinner("AI 영양사가 식단을 분석 중입니다..."):
            try:
                final_prompt = """
너는 대한민국 중·고등학생을 위한 식생활 교육 전문가이자 영양 교사야.

📌 **중요한 원칙**
- 이 분석은 사진을 기반으로 한 **교육용 추정 분석**이야.
- 실제 영양소 함량과 다를 수 있음을 명확히 밝혀.
- 학생의 건강을 위협하는 단정적 표현은 사용하지 마.

📌 **분석 기준**
- 「2020 한국인 영양소 섭취기준」
- 청소년 (만 12~18세) 권장량 기준

아래 형식으로 **한국어**로만 작성해줘.

---

### 📊 오늘의 식단 분석 리포트

#### 1️⃣ 인식된 메뉴
- 메뉴 목록을 bullet로 제시

#### 2️⃣ 주요 영양소 추정 (교육용)
| 영양소 | 추정 섭취 수준 | 권장량 대비 |
|---|---|---|
| 에너지 | | |
| 탄수화물 | | |
| 단백질 | | |
| 지방 | | |

※ 수치는 정확한 측정이 아닌 **학습을 위한 추정치**임을 명시

#### 3️⃣ 💡 청소년 맞춤 영양 코칭
- 이 식단의 긍정적인 점 1~2가지
- 다음 식사에서 보완하면 좋은 영양소와 식품 예시
- 청소년기 균형 잡힌 식사의 중요성 (3줄 이내)

#### 4️⃣ ⚠️ 교육용 안내 문구
- 이 결과는 참고용이며, 전문 상담을 대체하지 않음을 명확히 안내
"""

                response = model.generate_content(
                    [final_prompt, image],
                    generation_config={
                        "temperature": 0.3,
                        "max_output_tokens": 1200,
                    }
                )

                st.markdown("---")
                st.markdown(response.text)
                st.success("✅ 분석이 완료되었습니다!")

            except Exception as e:
                st.error("⚠️ AI 분석 중 오류가 발생했습니다.")
                st.caption("발표 시에는 네트워크 또는 API 일시 오류일 수 있습니다.")
                st.code(str(e))

# ===============================
# 5. 푸터
# ===============================
st.markdown("---")
st.caption("© 2026 인공지능융합교육 프로젝트 | 교육용 AI 시연")
