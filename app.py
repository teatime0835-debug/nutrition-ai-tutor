import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import os
import json
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# ===============================
# 1. Streamlit 기본 설정
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
# 2. OpenAI API 설정
# ===============================
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    st.error("⚠️ OpenAI API 키가 설정되지 않았습니다.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ===============================
# 3. 이미지 업로드
# ===============================
uploaded_file = st.file_uploader(
    "📷 오늘 먹은 급식 사진 업로드 (JPG, PNG)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    if len(uploaded_file.getvalue()) > 5_000_000:
        st.error("이미지 파일이 너무 큽니다. (5MB 이하 권장)")
        st.stop()

    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="업로드된 식단 사진", width=400)

    base64_image = base64.b64encode(
        uploaded_file.getvalue()
    ).decode("utf-8")

    # ===============================
    # 4. 1단계: 음식 인식
    # ===============================
    if st.button("🍽️ 음식 인식 시작"):
        with st.spinner("AI가 식단을 인식하고 있습니다..."):
            try:
                detect_prompt = """
너는 대한민국 중·고등학생 급식 사진을 분석하는 AI야.

⚠️ 지금 단계에서는 영양 분석을 절대 하지 마.
오직 사진 속 음식과 섭취량만 추정해.

출력 형식은 반드시 JSON 배열로 작성해.

예시:
[
  {"food": "쌀밥", "amount": "보통"},
  {"food": "된장국", "amount": "절반"},
  {"food": "닭강정", "amount": "소량"}
]

섭취량은 다음 중 하나만 사용:
보통 / 절반 / 소량 / 거의 먹지 않음

한국어 음식명만 사용해.
"""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": detect_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.2,
                    max_tokens=600
                )

                detected_foods = json.loads(
                    response.choices[0].message.content
                )

                st.session_state["foods"] = detected_foods
                st.success("✅ 음식 인식 완료! 아래에서 수정해 주세요.")

            except Exception as e:
                st.error("음식 인식 중 오류가 발생했습니다.")
                st.code(str(e))

# ===============================
# 5. 2단계: 사용자 수정
# ===============================
if "foods" in st.session_state:
    st.subheader("📝 AI 인식 결과 확인 및 수정")

    edited_foods = []

    for i, item in enumerate(st.session_state["foods"]):
        col1, col2 = st.columns([2, 1])
