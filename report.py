import streamlit as st
import pandas as pd
import io
import csv

st.set_page_config(
    page_title="광고 보고서",
    layout="wide"
)
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    st.header("📁 RAW 데이터 업로드")
    list_m = [
        "네이버 SA", 
        "네이버 GFA", 
        "구글", 
        "메타(페이스북)", 
        "카카오"
    ]
    media = st.selectbox(
        "광고 매체 선택", 
        list_m
    )
    uploaded_file = st.file_uploader(
        f"[{media}] RAW 파일", 
        type=["csv", "xlsx"]
    )

if uploaded_file is None:
    st.info("👈 왼쪽에서 매체를 선택하고 파일을 업로드해 주세요!")
    st.stop()

df = None
f_name = uploaded_file.name

# [대폭 수정] 파일 파싱의 모든 예외를 방어하는 마스터 리더 엔진
if f_name.endswith('.xlsx'):
    df = pd.read_excel(uploaded_file)
else:
    for enc in ['utf-8-sig', 'cp949', 'utf-8', 'euc-kr']:
        try:
            uploaded_file.seek(0)
            text_bytes = uploaded_file.read()
            text_str = text_bytes.decode(enc)
            
            # csv sniffer를 사용해 공백/탭/쉼표를 자동으로 완전히 분석
            dialect = csv.Sniffer().sniff(text_str[:4000])
            df = pd.read_csv(
                io.StringIO(text_str),
                sep=dialect.delimiter,
                engine='python'
            )
            if not df.empty and df.shape[1] > 1:
                break
        except:
            try:
                # 스니퍼 실패 시 기본 콤마(,) 및 탭(\t) 강제 분리 2차 방어선
                uploaded_file.seek(0)
                df = pd.read_csv(
                    uploaded_file, 
                    encoding=enc, 
                    sep=None, 
                    engine='python'
                )
                if not df.empty and df.shape[1] > 1:
                    break
            except:
                continue

if df is None or df.empty:
    st.error("⚠️ 파일 데이터를 읽을 수 없습니다.")
    st.stop()

# 모든 컬럼명 정제
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

camp_keywords = ['캠페인', 'Campaign', '광고상품', '광고그룹']

for c in df.columns:
    if not f_imp and c in imp_keys: f_imp = c
    if not f_clk and c in clk_keys: f_clk = c
    if not f_cost and c in cost_keys: f_cost = c
    for key in camp_keywords:
        if key in c: f_camp = c

def strict_clean(series):
    if series is None:
        return pd.Series(0, index=df.index)
    s_txt = series.astype(str)
    v = s_txt.str.replace(r'[^\d]', '', regex=True)
    return pd.to_numeric(v, errors='coerce').fillna(0)

calc_df = df.copy()
if f_imp: calc_df[f_imp] = strict_clean(df[f_imp])
if f_clk: calc_df[f_clk] = strict_clean(df[f_clk])
if f_cost: calc_df[f_cost] = strict_clean(df[f_cost])

cols = [f_camp]
for f in [f_imp, f_clk, f_cost]:
    if
