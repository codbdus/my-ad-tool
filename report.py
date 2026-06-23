import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    st.header("📁 RAW 데이터 업로드")
    list_m = ["네이버 SA", "네이버 GFA", "구글", "메타(페이스북)", "카카오"]
    media = st.selectbox("광고 매체 선택", list_m)
    uploaded_file = st.file_uploader(f"[{media}] RAW 파일", type=["csv", "xlsx"])

if uploaded_file is None:
    st.info("👈 왼쪽에서 매체를 선택하고 파일을 업로드해 주세요!")
    st.stop()

df = None
f_name = uploaded_file.name

# [엔진 보강] 네이버 SA 특유의 상단 빈 줄 및 탭 분리 현상 방어선 구축
if f_name.endswith('.xlsx'):
    df = pd.read_excel(uploaded_file)
else:
    for enc in ['utf-8-sig', 'cp949', 'utf-8', 'euc-kr']:
        try:
            uploaded_file.seek(0)
            # csv 파일의 구분자가 콤마(,)가 아닌 탭(\t)일 경우까지 통합 파싱
            df = pd.read_csv(uploaded_file, encoding=enc, sep=None, engine='python')
            if df.shape[1] <= 1: 
                continue
            break
        except:
            continue

if df is None or df.empty:
    st.error("⚠️ 파일 데이터를 읽을 수 없습니다. 올바른 포맷인지 확인해주세요.")
    st.stop()

# 모든 컬럼명의 앞뒤 공백 제거 및 정리
df.columns = [str(c).strip() for c in df.columns]

st.subheader(f"📝 {media} RAW 데이터 확인")

maps = {
    "네이버 SA": (
        ['노출수', '노출 수', '노출'], 
        ['클릭수', '클릭 수', '클릭'], 
        ['총비용', '광고비', '비용', '총비용(VAT포함)', '광고비(VAT포함)']
    ),
    "네이버 GFA": (['노출수', '노출 수'], ['클릭수', '클릭 수'], ['소진액', '소진 금액', '광고비']),
    "구글": (['노출수', 'Impressions'], ['클릭수', 'Clicks'], ['비용', 'Cost']),
    "메타(페이스북)": (['노출', 'Impressions'], ['링크 클릭', 'Clicks'], ['지출 금액', 'Amount Spent']),
    "카카오": (['노출수', 'Impressions'], ['클릭수', 'Clicks'], ['소진금액', '캐시소진액'])
}

imp_keys, clk_keys, cost_keys = maps[media]
f_imp, f_clk, f_cost, f_camp = None, None, None, df.columns[0]

for c in df.columns:
    if not f_imp and c in imp_keys: f_imp = c
    if not f_clk and c in clk_keys: f_clk = c
    if not f_cost and c in cost_keys: f_cost = c
    if '캠페인' in c or 'Campaign' in c or '광고상품' in c: f_camp = c

# [해결 1] 어떠한 문자열 형태도 무조건 순수한 숫자로만 강제 필터링하는 전처리
def strict_clean(series):
    if series is None:
        return pd.Series(0, index=df.index)
    # 문자가 섞인 셀에서 오직 숫자만 정규식으로 안전하게 추출
    v = series.astype(str).
