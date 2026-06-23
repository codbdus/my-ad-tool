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
    if '캠페인' in c_str or 'Campaign' in c_str or '광고상품' in c_str: f_camp = c

# [해결 1] 0원/0회 에러를 잡기 위해 문자와 공백을 완벽하게 제거하고 숫자로 바꾸는 안심 로직
def clean_to_numeric(series):
    if series is None:
        return pd.Series(0, index=df.index)
    # 기호, 쉼표, 공백, 한글 단위를 모두 지우고 숫자만 남김
    cleaned = series.astype(str).str.replace(r'[^\d\-.]', '', regex=True).str.strip()
    cleaned = cleaned.replace(['', 'nan', '.', '-'], '0')
    return pd.to_numeric(cleaned, errors='coerce').fillna(0)

# 원본 데이터 가독성을 위해 계산용 복사본 데이터프레임(calc_df) 생성
calc_df = df.copy()

if f_imp: calc_df[f_imp] = clean_to_numeric(df[f_imp])
if f_clk: calc_df[f_clk] = clean_to_numeric(df[f_clk])
if f_cost: calc_df[f_cost] = clean_to_numeric(df[f_cost])

cols = [f_camp]
for f in [f_imp, f_clk, f_cost]:
    if f: cols.append(f)

# 사용자가 업로드한 원본 표 형태 그대로 깔끔하게 노출
st.dataframe(df[cols], use_container_width=True)

# 지표 계산 (정제 완료된 calc_df 기준으로 합산 진행)
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

# [해결 2] 수치 정제가 완료되었으므로 AI 자동화 성과 분석 코멘트 상시 노출 가능
st.markdown("---")
st.subheader("🤖 AI 자동화 성과 분석 코멘트")

ai_comment = f"**[{media} 광고 성과 분석 요약 보고]**\n\n"
ai_comment += f"- 분석 기간 동안 총 **{t_imp:,}회** 노출되었으며, 광고를 통해 유입된 총 클릭수는 **{t_clk:,}회**입니다.\n"
ai_comment += f"- 전체 종합 클릭률(CTR)은 **{ctr:.2f}%**를 기록하고 있습니다. "

if ctr >= 1.2:
    ai_comment += "업종 평균 대비 양호한 유입률을 보이고 있으므로 현재의 타겟팅과 소재 방향성을 유지하는 것을 권장합니다. 👍\n"
else:
    ai_comment += "유입 효율이 다소 정체되어 있으므로 잠재 고객의 클릭을 유도할 수 있는 확장 소재 추가나 메인 카피 변경을 고려해 보세요. 💡\n"

ai_comment += f"- 마케팅 예산은 총 **{t_cost:,}원**이 집행되었으며, 1회 클릭당 비용(CPC)은 평균 **{round(cpc):,}원** 수준으로 파악됩니다."
st.info(ai_comment)

# [해결 3] 다운로드 시 ROAS만 나오던 버그 해결 및 원본 상세 내역 + 요약 시트 동시 기입
st.markdown("---")
st.subheader("📥 정제된 분석 보고서 다운로드")

out_df = pd.DataFrame([{
    "매체명": media, 
    "총 노출수": t_imp, 
    "총 클릭수": t_clk, 
    "클릭률(CTR)": f"{ctr:.2f}%", 
    "평균 CPC": round(cpc), 
    "총 소진금액": t_cost
}])

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine='openpyxl') as w:
    # '상세' 시트에는 원본에서 선택된 주요 열(캠페인명, 노출, 클릭, 비용)을 그대로 저장합니다.
    df[cols].to_excel(w, sheet_name='상세_캠페인별', index=False)
    # '요약' 시트에는 전체 합산 성과 지표를 깔끔하게 저장합니다.
    out_df.to_excel(w, sheet_name='종합_요약', index=False)

st.download_button(
    label="🟢 정제된 엑셀 보고서 (.xlsx) 다운로드", 
    data=buf.getvalue(), 
    file_name=f"{media}_광고보고서.xlsx", 
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
