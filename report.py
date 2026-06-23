import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    st.header("📁 RAW 데이터 업로드")
    media = st.selectbox("광고 매체 선택", ["네이버 SA", "네이버 GFA", "구글", "메타(페이스북)", "카카오"])
    uploaded_file = st.file_uploader(f"[{media}] RAW 파일", type=["csv", "xlsx"])

if uploaded_file is None:
    st.info("👈 왼쪽에서 매체를 선택하고 파일을 업로드해 주세요!")
    st.stop()

df = None
f_name = uploaded_file.name

# 파싱 엔진 축소 통합
if f_name.endswith('.xlsx'):
    df = pd.read_excel(uploaded_file)
else:
    for enc in ['utf-8-sig', 'cp949', 'utf-8']:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc, sep=None, engine='python')
            if not df.empty and df.shape[1] > 1: break
        except:
            continue

if df is None or df.empty:
    st.error("⚠️ 파일을 읽을 수 없습니다.")
    st.stop()

df.columns = [str(c).strip() for c in df.columns]
st.subheader(f"📝 {media} RAW 데이터 확인")

# 핵심 컬럼 매핑 사전을 극단적으로 압축
maps = {
    "네이버 SA": (['노출수', '노출 수'], ['클릭수', '클릭 수'], ['총비용', '광고비', '비용']),
    "네이버 GFA": (['노출수'], ['클릭수'], ['소진액', '소진 금액']),
    "구글": (['노출수', 'Impressions'], ['클릭수', 'Clicks'], ['비용', 'Cost']),
    "메타(페이스북)": (['노출'], ['링크 클릭', 'Clicks'], ['지출 금액']),
    "카카오": (['노출수'], ['클릭수'], ['소진금액'])
}

imp_k, clk_k, cost_k = maps[media]
f_imp = next((c for c in df.columns if c in imp_k), None)
f_clk = next((c for c in df.columns if c in clk_k), None)
f_cost = next((c for c in df.columns if c in cost_k), None)
f_camp = next((c for c in df.columns if any(k in c for k in ['캠페인', 'Campaign', '광고그룹'])), df.columns[0])

def clean_num(series):
    if series is None: return pd.Series(0, index=df.index)
    v = series.astype(str).str.replace(r'[^\d]', '', regex=True)
    return pd.to_numeric(v, errors='coerce').fillna(0)

calc_df = df.copy()
if f_imp: calc_df[f_imp] = clean_num(df[f_imp])
if f_clk: calc_df[f_clk] = clean_num(df[f_clk])
if f_cost: calc_df[f_cost] = clean_num(df[f_cost])

cols = [c for c in [f_camp, f_imp, f_clk, f_cost] if c and c in df.columns]
st.dataframe(df[cols], use_container_width=True)

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
c3.metric("클릭률 CTR", f"{ctr:.2f} %")
c4.metric("총 소진 금액", f"{t_cost:,} 원")

st.markdown("---")
st.subheader("🤖 AI 자동화 성과 분석 코멘트")

if t_imp > 0:
    msg = f"**[{media} 광고 성과 요약]**\n\n"
    msg += f"- 노출수 **{t_imp:,}회**, 클릭수 **{t_clk:,}회**를 기록했습니다.\n"
    msg += f"- 종합 CTR은 **{ctr:.2f}%**이며, 평균 CPC는 **{round(cpc):,}원**입니다.\n"
    msg += f"- 총 예산 소진 금액은 **{t_cost:,}원**으로 최종 집계되었습니다."
