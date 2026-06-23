import streamlit as st
import pandas as pd
import io
import re

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

if f_name.endswith('.xlsx'):
    df = pd.read_excel(uploaded_file)
else:
    for enc in ['utf-8-sig', 'cp949', 'utf-8', 'euc-kr']:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(
                uploaded_file, 
                encoding=enc, 
                sep=None, 
                engine='python'
            )
            if df.shape[1] <= 1: 
                continue
            break
        except:
            continue

if df is None or df.empty:
    st.error("⚠️ 파일 데이터를 읽을 수 없습니다.")
    st.stop()

# 컬럼명 정리
df.columns = [str(c).strip() for c in df.columns]

st.subheader(f"📝 {media} RAW 데이터 확인")

# 매칭 사전
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

# [오류 해결 부분] 
# 마침표 뒤가 잘리지 않도록 줄 바꿈으로 잘게 쪼갰습니다.
def strict_clean(series):
    if series is None:
        return pd.Series(0, index=df.index)
    
    # 쪼개서 결합하는 방식으로 코드 우측 컷팅 현상 원천 차단
    s_txt = series.astype(str)
    v = s_txt.str.replace(
        r'[^\d]', 
        '', 
        regex=True
    )
    v = v.replace(['', 'nan'], '0')
    
    return pd.to_numeric(
        v, 
        errors='coerce'
    ).fillna(0)

calc_df = df.copy()
if f_imp: calc_df[f_imp] = strict_clean(df[f_imp])
if f_clk: calc_df[f_clk] = strict_clean(df[f_clk])
if f_cost: calc_df[f_cost] = strict_clean(df[f_cost])

cols = [f_camp]
for f in [f_imp, f_clk, f_cost]:
    if f and f in df.columns: cols.append(f)

st.dataframe(df[cols], use_container_width=True)

# 지표 계산
t_imp = int(calc_df[f_imp].sum()) if f_imp else 0
t_clk = int(calc_df[f_clk].sum()) if f_clk else 0
t_cost = int(calc_df[f_cost].sum()) if f_cost else 0
ctr = (t_clk / t_imp * 100) if t_imp > 0 else 0
cpc = (t_cost / t_clk) if t_clk > 0 else 0

st.markdown("---")
st.subheader(f"📈 {media} 주요 지표 요약")
c1, c2, c3, c4 = st.columns(4)
c1.metric("총 노출수", f"{t_imp:,} 회")
c2.metric("총 클릭수", f"{t_clk:,} 회")
c3.metric("클릭률 (CTR)", f"{ctr:.2f} %")
c4.metric("총 소진 금액", f"{t_cost:,} 원")

st.markdown("---")
st.subheader("🤖 AI 자동화 성과 분석 코멘트")

if t_imp > 0:
    ai_txt = f"**[{media} 광고 성과 데이터 정밀 분석 결과]**\n\n"
    ai_txt += f"-
