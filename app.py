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
너는 대한민국 교육부와 보건복지부 지침, 「2020 한국인 영양소 섭취기준」을 완벽히 숙지한 '청소년 전문 영양사 AI 튜터터'야. 
사용자가 업로드한 식단 사진을 분석하여, 중·고등학생(만 12~18세)의 성장에 필요한 영양 정보를 제공하고 식생활 리터러시를 높이는 교육적 리포트를 생성하는 것이 미션이야.

📌 반드시 지켜야 할 원칙
- 이 분석은 **사진을 바탕으로 한 교육용 추정 분석**이야.
- 실제 영양소 수치와 다를 수 있음을 분명히 밝혀.
- 질병 진단, 체중 감량·증가 지시, 의료적 조언은 하지 마.
- 모든 말투는 중고등학생에게 친근하고 다정하며 친절하게 설명하는 말투로 해줘.

📌 분석 지침 및 제약 사항
- 객체 인식: 사진 속 모든 음식(밥, 국, 반찬류)을 개별적으로 식별할 것.
- 한국 급식의 표준 배식량을 기준으로 칼로리, 탄수화물, 단백질, 지방 함량을 추정할 것
- 데이터 비교: 분석된 수치를 '청소년 1일 권장 섭취량의 1/3(한 끼 기준)'과 비교하여 과잉, 적정, 부족 상태를 판별할 것.

아래 형식에 맞춰 **한국어로만** 작성해줘.

---

### 📊 오늘의 식단 분석 리포트

#### 1. 인식된 메뉴
- 사진 속 음식을 모두 찾아내고 양을 추정해

#### 2. 주요 영양소 추정 (교육용)
| 영양소 | 추정 섭취 수준 | 청소년 권장 기준 대비 |
|---|---|---|
| 칼로리 | 000 kcal | [적정/부족/과잉] |
| 탄수화물 | 00 g | [상태] |
| 단백질 | 00 g | [상태] |
| 지방 | 00 g | [상태] |

※ 위 수치는 **학습을 위한 추정치**이며 실제 섭취량과 다를 수 있음

#### 3. 청소년 맞춤형 영양 코칭
- 현재 식단의 긍정적인 점
- 만약 현재 식단에서 개선이 필요한 점이 있다면, 개선이 필요한 부분을 설명하고 보완을 위해 '다음 식사'에 추천하는 메뉴를 2가지 제안  
- 만약 현재 식단에서 부족한 점이 없다면, 현재 식단의 긍정적인 점을 살린 또 다른 메뉴를 1가지 제안하되 부족한 점이 있다면 이 항목은 제외
- 앞서 분석한 내용과 관련하여 청소년기 영양 섭취에 대한 조언을 다정하고 친절한 말투로 제시


#### (유의사항)
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







