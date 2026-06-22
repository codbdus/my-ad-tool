import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import openai  # AI 코멘트 자동화를 위한 라이브러리 (선택)

# 1. 페이지 기본 설정
st.set_page_config(page_title="통합 매체 자동화 보고서 리포터", layout="wide")
st.title("📊 통합 매체 광고 성과 자동화 보고서 시스템")
st.caption("바이브코딩(Vibe Coding)으로 구축하는 대행사 멀티매체 리포팅 툴")
st.markdown("---")

# 구글 시트 연결 함수 (Secret 설정 필수)
def connect_google_sheet():
    try:
        # Streamlit의 Secrets 기능을 이용해 구글 크레덴셜 안전하게 로드
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gapi"], scopes=scope)
        client = gspread.authorize(creds)
        # 본인의 구글 시트 URL 입력 또는 비밀키 설정
        sheet_url = "https://docs.google.com/spreadsheets/d/1CMNsIc2giLwUikzhYub5MRVOJFl_n9je-EOuu_gV63g/edit#gid=0"
        doc = client.open_by_url(sheet_url)
        return doc
    except Exception as e:
        st.error(f"구글 시트 연결에 실패했습니다. Secrets 설정을 확인하세요. 에러: {e}")
        return None

# AI 코멘트 생성 함수 (OpenAI API 활용 예시)
def generate_ai_comment(media_name, budget, spend, balance):
    # API 키가 세팅되어 있다면 LLM 작동, 없으면 규칙 기반 템플릿 반환
    if "OPENAI_API_KEY" in st.secrets:
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        prompt = f"""
        당신은 뷰티 전문 퍼포먼스 마케터입니다. 오늘 {media_name} 매체의 광고 운영 결과는 다음과 같습니다.
        - 매체 예산: {budget}원
        - 당일 소진 광고비: {spend}원
        - 남은 예산 잔액: {balance}원
        
        이 데이터를 기반으로 광고주 보고서용 '운영 코멘트 및 대응 내용'을 문장 부호(-) 형태의 한 줄 요약으로 전문성 있게 1~2개 작성해 주세요.
        예시: - 일자별 목표예산 맞춰 소진 확인 완료 및 효율 방어 진행
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message['content'].strip()
        except:
            return f"- {media_name} 예산 소진 확인 및 잔액 {balance:,}원 기준 효율 방어 진행 완료."
    else:
        # Fallback 템플릿
        return f"- 하루 예산 조정으로 효율 방어 진행후 예산 소진 확인 완료\n- {media_name} 당일 모니터링 및 소재 이상 무"

# 2. 사이드바 컨트롤러 (매체 및 파일 선택)
st.sidebar.header("📁 RAW 데이터 업로드")
selected_media = st.sidebar.selectbox(
    "업로드할 광고 매체를 선택하세요", 
    ["네이버 SA", "네이버 GFA", "구글 SA", "구글 Demand Gen", "메타(Meta)"]
)
uploaded_file = st.sidebar.file_uploader(f"[{selected_media}] 광고시스템에서 추출한 RAW 파일", type=["csv", "xlsx"])

# 구글 시트 미리 연결
doc = connect_google_sheet()

col1, col2 = st.columns([3, 2])

# 3. 메인 화면 로직
if uploaded_file is not None:
    # 3-1. 파일 읽기 및 매체별 통일화(Mapping)
    if uploaded_file.name.endswith('.csv'):
        df_raw = pd.read_csv(uploaded_file)
    else:
        df_raw = pd.read_excel(uploaded_file)
        
    with col1:
        st.subheader(f"📋 {selected_media} RAW 데이터 원본 (상위 5개 행)")
        st.dataframe(df_raw.head(5), use_container_width=True)
        
        # 💡 매체별 컬럼 매핑 표준화 파트
        # 각 매체마다 '광고비', '비용', 'Spend' 등으로 이름이 다른 것을 하나로 통일합니다.
        spend_val = 0
        if "광고비" in df_raw.columns:
            spend_val = df_raw["광고비"].sum()
        elif "비용" in df_raw.columns:
            spend_val = df_raw["비용"].sum()
        elif "Spend" in df_raw.columns:
            spend_val = df_raw["Spend"].sum()
        else:
            # 적절한 컬럼을 찾지 못했을 때 수동 입력 유도
            spend_val = st.number_input("데이터에서 광고비를 인식하지 못했습니다. 직접 입력해주세요:", min_value=0, value=0)
            
        st.metric(label=f"📊 분석된 {selected_media} 총 소진 금액", value=f"{int(spend_val):,} 원")

    # 3-2. 구글 시트 라이팅 및 AI 코멘트 생성
    with col2:
        st.subheader("🤖 자동 생성된 AI 리포트 코멘트")
        
        # 임의의 예산 세팅 (실제 구글 시트의 기존 예산 데이터를 가져오거나 입력받을 수 있음)
        default_budget = 3140000 
        calculated_balance = default_budget - int(spend_val)
        
        # AI 코멘트 미리보기 생성
        ai_comment = generate_ai_comment(selected_media, default_budget, int(spend_val), calculated_balance)
        edited_comment = st.text_area("매체에 기입될 코멘트 내용 수정:", value=ai_comment, height=150)
        
        # 구글 시트로 업데이트 실행 버튼
        if st.button(f"🚀 {selected_media} 데이터를 구글 시트에 업데이트"):
            if doc is not None:
                with st.spinner("구글 시트에 수식 입력 및 데이터 전송 중..."):
                    summary_sheet = doc.worksheet("Summary")
                    
                    # 🔍 기존 시트의 구조에 맞춰 '운영 매체' 열에서 매체 위치 탐색
                    # 대략 E열에 매체명이 있다고 가정한 로직 예시 (실제 구조에 따라 행 번호 매칭 조정 가능)
                    media_cells = summary_sheet.findall(selected_media)
                    
                    if media_cells:
                        target_row = media_cells[0].row
                        
                        # 값 직접 대입 (소진 광고비 - K열 가정)
                        summary_sheet.update_cell(target_row, 11, int(spend_val)) # K열에 소진광고비 입력
                        
                        # 수식 대입 (잔액 - L열 가정 / 예산[F열] - 소진광고비[K열])
                        summary_sheet.update_cell(target_row, 12, f"=F{target_row}-K{target_row}") 
                        
                        # 일자별 목표 예산 수식 대입 (J열 가정 / 예산[F열] / 운영기간[D12])
                        summary_sheet.update_cell(target_row, 10, f"=F{target_row}/$D$12")
                        
                        # 우측 코멘트 열에 AI가 만든 인사이트 기입 (O열 가정)
                        summary_sheet.update_cell(target_row, 15, edited_comment)
                        
                        st.success(f"🎉 구글 시트 [{target_row}번째 행]에 데이터와 자동 수식, 코멘트 기입이 완료되었습니다!")
                    else:
                        st.error(f"구글 시트에서 '{selected_media}' 항목을 찾지 못했습니다. 매체 명칭이 일치하는지 확인하세요.")
            else:
                st.error("구글 시트 연결이 설정되지 않아 업로드가 불가능합니다.")
else:
    with col1:
        st.info("💡 사이드바에서 분석할 매체를 선택하고 RAW 데이터 파일을 업로드해 주세요.")
    with col2:
        st.write("파일이 업로드되면 이 자리에 AI가 제안하는 일일 리포트용 코멘트가 나타납니다.")
