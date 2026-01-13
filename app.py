import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import os
import warnings

# ===============================
# (선택) 경고 숨기기
# ===============================
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
# 3. 이미지 업로드 (학생 입력은 이것만)
# ===============================
uploaded_file = st.file_uploader(
    "📷 오늘 먹은 급식 사진 업로드 (JPG, PNG)",
    type=["jpg", "jpeg", "png"]
)

# ===============================
# 4. 이미지 표시
# ===============================
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="업로드된 식단 사진", width=400)

    # 이미지 크기 제한 (발표 안정성)
    if len(uploaded_file.getvalue()) > 5_000_000:
        st.error("이미지 파일이 너무 큽니다. (5MB 이하 권장)")
        st.stop()

    # ===============================
    # 5. 분석 버튼
    # ===============================
    if st.button("🚀 영양 분석 리포트 생성"):
        with st.spinner("AI 영양 튜터가 식단을 분석 중입니다..."):
            try:
                # ✅ base64 안전 인코딩 (핵심 수정)
                base64_image = base64.b64encode(
                    uploaded_file.getvalue()
                ).decode("utf-8")

                prompt = """
너는 대한민국 중·고등학생을 위한 식생활 교육 전문가이자 영양 교사야.

📌 반드시 지켜야 할 원칙
- 이 분석은 **사진을 바탕으로 한 교육용 추정 분석**이야.
- 실제 영양소 수치와 다를 수 있음을 분명히 밝혀.
- 질병 진단, 체중 감량·증가 지시, 의료적 조언은 하지 마.

📌 분석 기준
- 「2020 한국인 영양소 섭취기준」
- 청소년 (만 12~18세) 권장량 기준

아래 형식에 맞춰 **한국어로만** 작성해줘.

---

### 📊 오늘의 식단 분석 리포트

#### 1️⃣ 인식된 메뉴
- 사진에서 보이는 음식 목록

#### 2️⃣ 주요 영양소 추정 (교육용)
| 영양소 | 추정 섭취 수준 | 권장량 대비 |
|---|---|---|
| 에너지 | | |
| 탄수화물 | | |
| 단백질 | | |
| 지방 | | |

※ 위 수치는 **학습을 위한 추정치**이며 실제 섭취량과 다를 수 있음

#### 3️⃣ 청소년 맞춤 영양 코칭
- 현재 식단의 긍정적인 점
- 다음 식사에서 보완하면 좋은 영양소

#### 4️⃣ 분석을 바탕으로 한 추천 메뉴 (교육용)
- 위 분석 결과를 근거로 다음 식사에서 선택하면 좋은 메뉴를 2가지만 제안해줘.
- 학교 급식 또는 가정에서 가능한 메뉴 위주로 제시해.

형식:
- 추천 메뉴 1:
  - 추천 이유:
- 추천 메뉴 2:
  - 추천 이유:

#### 5️⃣ 교육용 안내
- 본 결과는 참고용이며 전문적인 영양 상담을 대체하지 않음을 명확히 안내
"""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.3,
                    max_tokens=1200
                )

                st.markdown("---")
                st.markdown(response.choices[0].message.content)
                st.success("✅ 분석이 완료되었습니다!")

            except Exception as e:
                st.error("⚠️ AI 분석 중 오류가 발생했습니다.")
                st.caption("네트워크 또는 API 일시 오류일 수 있습니다.")
                st.code(str(e))

# ===============================
# 6. 푸터
# ===============================
st.markdown("---")
st.caption("© 2026 인공지능융합교육 프로젝트 | 청소년 AI 영양 튜터 (교육용)")

