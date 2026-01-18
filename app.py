import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import os
import json
import re
import warnings

# ===============================
# 경고 숨기기
# ===============================
warnings.filterwarnings("ignore", category=FutureWarning)

# ===============================
# Streamlit 기본 설정
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
# OpenAI API 설정
# ===============================
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    st.error("⚠️ OpenAI API 키가 설정되지 않았습니다.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# ===============================
# 세션 상태 초기화
# ===============================
if "foods" not in st.session_state:
    st.session_state.foods = None

# ===============================
# 이미지 업로드
# ===============================
uploaded_file = st.file_uploader(
    "📷 오늘 먹은 급식 사진 업로드 (JPG, PNG)",
    type=["jpg", "jpeg", "png"]
)

# ===============================
# 이미지 표시 및 1단계: 음식 인식
# ===============================
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="업로드된 식단 사진", width=400)

    if len(uploaded_file.getvalue()) > 5_000_000:
        st.error("이미지 파일이 너무 큽니다. (5MB 이하 권장)")
        st.stop()

    if st.button("① 음식 인식하기"):
        with st.spinner("AI가 식단을 인식 중입니다..."):
            try:
                base64_image = base64.b64encode(
                    uploaded_file.getvalue()
                ).decode("utf-8")

                detect_prompt = """
너는 청소년 급식 사진을 분석하는 AI야.

⚠️ 지금 단계에서는 영양 분석을 하지 마.
오직 음식 이름과 섭취량만 추정해.

출력 형식은 반드시 JSON 배열만 사용해.
설명 문장, 인사말, Markdown, ```json``` 사용 금지.

형식 예시:
[
  {"food": "쌀밥", "amount": "대체로"},
  {"food": "된장국", "amount": "절반"},
  {"food": "제육볶음", "amount": "모두"}
]

섭취량은 반드시 다음 중 하나:
모두 / 대체로 / 절반 / 소량 / 거의 먹지 않음
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

                raw_output = response.choices[0].message.content.strip()

                # JSON 안전 추출
                match = re.search(r"\[.*\]", raw_output, re.DOTALL)
                if not match:
                    st.error("⚠️ 음식 인식 결과를 구조화하지 못했습니다.")
                    st.code(raw_output)
                    st.stop()

                st.session_state.foods = json.loads(match.group())
                st.success("✅ 음식 인식 완료! 아래에서 확인·수정하세요.")

            except Exception as e:
                st.error("⚠️ 음식 인식 중 오류 발생")
                st.code(str(e))
                st.stop()

# ===============================
# 2단계: 사용자 수정
# ===============================
if st.session_state.foods:
    st.subheader("📝 AI 인식 결과 확인 및 수정")

    edited_foods = []

    intake_options = ["모두", "대체로", "절반", "소량", "거의 먹지 않음"]

    for i, item in enumerate(st.session_state.foods):
        col1, col2 = st.columns([2, 1])

        with col1:
            food = st.text_input(
                "음식명",
                value=item["food"],
                key=f"food_{i}"
            )

        with col2:
            amount = st.selectbox(
                "섭취량",
                intake_options,
                index=intake_options.index(item["amount"])
                if item["amount"] in intake_options else 1,
                key=f"amount_{i}"
            )

        edited_foods.append({"food": food, "amount": amount})

    # ===============================
    # 3단계: 최종 영양 분석
    # ===============================
    if st.button("② 최종 영양 분석 리포트 생성"):
        with st.spinner("AI 영양 튜터가 분석 중입니다..."):
            try:
                final_prompt = f"""
다음은 학생이 직접 확인·수정한 실제 섭취 식단 정보야.

{edited_foods}

너는 「2020 한국인 영양소 섭취기준」을 기반으로
청소년(만 12~18세) 한 끼 기준의
**교육용 영양 분석 리포트**를 작성해.

⚠️ 반드시 지켜:
- 추정 분석임을 명확히 밝힐 것
- 질병 진단, 체중 조절 지시 금지
- 친절하고 다정한 말투 사용

아래 형식으로 한국어로 작성해.

---

### 📊 최종 영양 분석 리포트

#### 1️⃣ 섭취한 메뉴 정리
- 수정된 음식 목록과 섭취량 정리

#### 2️⃣ 주요 영양소 추정 (교육용)
| 영양소 | 추정 섭취 수준 | 청소년 기준 대비 | 하루 총 섭취량 대비(%) ]
|---|---|---|---|
| 칼로리 | | | |
| 탄수화물 | | | |
| 단백질 | | | |
| 지방 | | | |


※ 실제 섭취량과 다를 수 있음

#### 3️⃣ 💡 맞춤형 영양 코칭
- 현재 식단의 긍정적인 점
- 부족하거나 보완하면 좋은 점
- 다음 식사 추천 메뉴 제안
- 청소년기 식사의 중요성 설명

#### ⚠️ 유의사항
- 본 결과는 교육용 참고 자료임
"""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": final_prompt}],
                    temperature=0.3,
                    max_tokens=1200
                )

                st.markdown("---")
                st.markdown(response.choices[0].message.content)
                st.success("✅ 분석 완료!")

            except Exception as e:
                st.error("⚠️ 분석 중 오류 발생")
                st.code(str(e))

# ===============================
# 푸터
# ===============================
st.markdown("---")
st.caption("© 2026 인공지능융합교육 프로젝트 | 청소년 AI 영양 튜터 (교육용)")
