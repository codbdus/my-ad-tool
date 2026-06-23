import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    st.header("📁 RAW 데이터 업로드")
    list_m = ["네이버 SA", "네이버 GFA", "구글", "메타(페이스북)", "카카오"]
    media = st.selectbox("광고 매체 선택", list_m)
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
    for enc in ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc)
            break
        except:
            continue

if df is None:
    st.error("⚠️ 파일 형식을 확인할 수 없습니다.")
    st.stop()

st.subheader(f"📝 {media} RAW 데이터 확인")

# [핵심 수정] 모든 형태의 네이버 광고비 컬럼명 종류를 전부 등록했습니다.
maps = {
    "네이버 SA": (
        ['노출수', '노출 수'], 
        ['클릭수', '클릭 수'], 
        ['총비용', '광고비', '비용', '총비용(VAT포함)', '광고비(VAT포함)', '총비용(VAT 포함)', '광고비(VAT 포함)']
    ),
    "네이버 GFA": (['노출수', '노출 수'], ['클릭수', '클릭 수'], ['소진액', '소진 금액', '광고비']),
    "구글": (['노출수', 'Impressions'], ['클릭수', 'Clicks'], ['비용', 'Cost']),
    "메타(페이스북)": (['노출', 'Impressions'], ['링크 클릭', 'Clicks'], ['지출 금액', 'Amount Spent']),
    "카카오": (['노출수', 'Impressions'], ['클릭수', 'Clicks'], ['소진금액', '캐시소진액'])
}

imp_keys, clk_keys, cost_keys = maps[media]
f_imp, f_clk, f_cost, f_camp = None, None, None, df.columns[0]

for c in df.columns:
    c_str = str(c).strip()
    if not f_imp and c_str in imp_keys: f_imp = c
    if not f_clk and c_str in clk_keys: f_clk = c
    if not f_cost and c_str in cost_keys: f_cost = c
    if '캠페인' in c_str or 'Campaign' in c_str: f_camp = c

# 문자열을 숫자로 완벽하게 강제 변환하는 함수
def clean(s):
    if s is None:
        return pd.Series(0, index=df.index)
    s_clean = s.astype(str).str.replace(r'[^\d\-]', '', regex=True).str.strip()
    s_clean = s_clean.replace('', '0')
    return pd.to_numeric(s_clean, errors='coerce').fillna(0)

if f_imp: df[f_imp] = clean(df[f_imp]).astype(int)
if f_clk: df[f_clk] = clean(df[f_clk]).astype(int)
if f_cost: df[f_cost] = clean(df[f_cost]).astype(int)

cols = [f_camp]
for f in [f_imp, f_clk, f_cost]:
    if f: cols.append(f)

st.dataframe(df[cols], use_container_width=True)

# 지표 계산
t_imp = int(df[f_imp].sum()) if f_imp else 0
t_clk = int(df[f_clk].sum()) if f_clk else 0
t_cost = int(df[f_cost].sum()) if f_cost else 0
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

# 광고비나 노출수가 집계되면 코멘트가 바로 나오도록 조건을 유연하게 변경
if t_imp > 0 or t_cost > 0:
    ai_comment = f"**[{media} 성과 요약 보고]**\n\n"
    ai_comment += f"- 이번 기간 동안 총 **{t_imp:,}회**의 광고 노출과 **{t_clk:,}회**의 클릭이 일어났습니다.\n"
    ai_comment += f"- 평균 클릭률(CTR)은 **{ctr:.2f}%**이며, 총 소진 금액은 **{t_cost:,}원**입니다.\n"
    if t_clk > 0:
        ai_comment += f"- 클릭당 비용(CPC)은 평균 **{round(cpc):,}원**으로 집계됩니다.\n\n"
    
    if ctr >= 1.5:
        ai_comment += "📢 **종합 의견**: 타겟 고객에게 광고 소재가 매력적으로 소구되고 있습니다. 현재 세팅을 유지하되 확장 키워드를 고려해 보세요! 👍"
    else:
        ai_comment += "📢 **종합 의견**: 클릭률이 다소 낮은 편입니다. 고객의 이목을 끌 수 있는 광고 카피나 확장 소재의 개선을 검토해 보세요. 💡"
    st.info(ai_comment)
else:
    st.warning("⚠️ 파일에서 데이터를 합산하지 못했습니다. 매체 선택과 업로드한 파일이 일치하는지 확인해 주세요.")

st.markdown("---")
st.subheader("📥 정제된 분석 보고서 다운로드")

out_df = pd.DataFrame([{
    "매체명": media, "총 노출수": t_imp, "총 클릭수": t_clk, 
    "클릭률": f"{ctr:.2f}%", "CPC": round(cpc), "총 소진금액": t_cost
}])

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine='openpyxl') as w:
    df[cols].to_excel(w, sheet_name='상세', index=False)
    out_df.to_excel(w, sheet_name='요약', index=False)

st.download_button(
    label="🟢 정제된 엑셀 보고서 (.xlsx) 다운로드", 
    data=buf.getvalue(), 
    file_name=f"{media}_광고보고서.xlsx", 
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
