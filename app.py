import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import warnings

# ===============================
# (선택) 불필요한 경고 숨기기
# ===============================
warnings.filterwarnings("ignore", category=FutureWarning)

# ===============================
# 1. Streamlit 기본 설정 (반드시 최상단)
# ===============================
st.set_page_config(
    page_title="청소년 AI 영양 튜터",
    page_icon="🍱",
    layout="centered"
)

st.title("🍱 청소년 AI 영양 튜터")

st.info(
    "📌 이 서비스는 **교육 목적의 AI 시연**입니다.\n\n"
    "- 분석 결과는 **실제 영양소 측정이 아닌 추정치**입니다.\n"
    "- 의료·영양 상담을 대체하지 않습니다."
)

# ===============================
# 2. Gemini API 설정 (Cloud / 로컬 공통)
# ===============================
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("⚠️ Gemini API 키가 설정되지 않았습니다.")
    st.stop()

genai.configure(api_key=API_KEY)

# ✅ Streamlit Cloud에서 현재 가장 안정적인 멀티모달 모델
model = genai.GenerativeModel("models/gemini-1.0-pro-vision")


# (디버그용 – 문제 생기면 확인)
# st.caption(f"🔍 사용 모델: {model.model_name}")

# ===============================
# 3. 이미지 업로드
# ===============================
uploaded_file = st.file_uploader(
    "📷 오늘 먹은 급식 사진 업로드 (JPG, PNG)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
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

📌 중요한 원칙
- 이 분석은 사진을 바탕으로 한 **교육용 추정 분석**이야.
- 실제 영양소 함량과 다를 수 있음을 분명히 밝혀.
- 학생의 건강을 위협하거나 진단하는 표현은 사용하지 마.

📌 분석 기준
- 「2020 한국인 영양소 섭취기준」
- 청소년 (만 12~18세) 권장량 기준

아래 형식에 맞춰 **한국어로만** 작성해줘.

---

### 📊 오늘의 식단 분석 리포트

#### 1️⃣ 인식된 메뉴
- 사진에서 보이는 메뉴를 목록으로 제시

#### 2️⃣ 주요 영양소 추정 (교육용)
| 영양소 | 추정 섭취 수준 | 권장량 대비 |
|---|---|---|
| 에너지 | | |
| 탄수화물 | | |
| 단백질 | | |
| 지방 | | |

※ 위 수치는 **학습을 위한 추정치**이며 실제 섭취량과 다를 수 있음

#### 3️⃣ 💡 청소년 맞춤 영양 코칭
- 현재 식단의 긍정적인 점 1~2가지
- 다음 식사에서 보완하면 좋은 영양소와 식품 예시
- 청소년기에 균형 잡힌 식사가 왜 중요한지 간단히 설명

#### 4️⃣ ⚠️ 교육용 안내
- 이 결과는 참고용이며, 전문적인 영양 상담을 대체하지 않음을 명확히 안내
"""

                response = model.generate_content(
                    [
                        {
                            "role": "user",
                            "parts": [
                                {"text": final_prompt},
                                image
                            ]
                        }
                    ],
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
                st.caption("네트워크 또는 API 일시 오류일 수 있습니다.")
                st.code(str(e))

# ===============================
# 5. 푸터
# ===============================
st.markdown("---")
st.caption("© 2026 인공지능융합교육 프로젝트 | 청소년 AI 영양 튜터 (교육용)")

