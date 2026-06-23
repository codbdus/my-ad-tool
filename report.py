import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    st.header("📁 RAW 데이터 업로드")
    media = st.selectbox("광고 매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    uploaded_file = st.file_uploader("RAW 파일 업로드", type=["csv", "xlsx"])

if not uploaded_file:
    st.info("👈 왼쪽에서 파일을 업로드해 주세요!")
    st.stop()

df_raw = None
if uploaded_file.name.endswith('.xlsx'):
    df_raw = pd.read_excel(uploaded_file)
else:
    for enc in ['utf-8-sig', 'cp949', 'utf-8', 'euc-kr']:
        try:
            uploaded_file.seek(0)
            df_raw = pd.read_csv(uploaded_file, encoding=enc, sep=None, engine='python')
            if not df_raw.empty: break
        except: continue

if df_raw is None or df_raw.empty:
    st.error("⚠️ 파일을 읽을 수 없습니다.")
    st.stop()

# 🎯 [핵심 패치] 상단에 쓸데없는 설명 줄이 끼어있을 경우, 진짜 데이터 시작점 자동 탐색
target_row_idx = 0
found = False

# 첫 10줄을 검사하며 진짜 컬럼명이 들어있는 행 탐색
for idx in range(min(10, len(df_raw))):
    row_str = "".join(df_raw.iloc[idx].astype(str))
    if any(k in row_str for k in ['노출', '클릭', '비용', '금액', 'Impressions', 'Clicks']):
        target_row_idx = idx
        found = True
        break

if found:
    # 찾은 행을 컬럼명으로 지정하고 데이터 재구성
    new_cols = [str(x).strip() for x in df_raw.iloc[target_row_idx]]
    df = df_raw.iloc
