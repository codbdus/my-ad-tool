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

if f_name.endswith('.xlsx'):
    df = pd.read_excel(uploaded_file)
else:
    for enc in ['utf-8-sig', 'cp949', 'utf-8', 'euc-kr']:
        try:
            uploaded_file.seek(0)
            # 1차로 그냥 읽어옴
            df = pd.read_csv(uploaded_file, encoding=enc)
            
            # [핵심] 하나의 열에 쉼표(,)로 뭉쳐진 네이버 SA 특유의 현상 강제 분리 개조
            if df.shape[1] == 1 or 'Unnamed' in str(df.columns[0]):
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=enc, sep=',', engine='python')
            
            # 만약 탭 분리 파일일 경우 처리
            if df.shape[1] <= 1:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=enc, sep='\t', engine='python')
                
            if not df.empty and df.shape[1] > 1: break
        except:
            continue

if df is None or df.empty:
    st.error("⚠️ 파일 데이터를 분리할 수 없습니다.")
    st.stop()

# 컬럼명 공백 제거
df.columns = [str(c).strip() for c in df.columns]

st.subheader(f"📝 {media} RAW 데이터 확인")

maps = {
    "네이버 SA": (['노출수', '노출 수', '노출'], ['클릭수', '클릭 수', '클릭'], ['총비용', '광고비', '비용']),
    "네이버 GFA": (['노출수'], ['클릭수'], ['소진액', '소진 금액']),
    "구글": (['노출수', 'Impressions'], ['클릭수', 'Clicks'], ['비용', 'Cost']),
    "메타(페이스북)": (['노출'], ['링크 클릭', 'Clicks'], ['지출 금액']),
    "카카오": (['노출수'], ['클릭수'], ['소진금액'])
}

imp_k, clk_k, cost_k = maps[media]
f_imp = next((c for c in df.columns if c in imp_k), None)
f_clk = next((c for c in df.columns if c in clk_k), None)
f_cost = next((c for c in df.columns if c in cost_k), None)
f_camp = next((c for c in df.columns if any(k in c for k in ['캠페인', 'Campaign', '광고상품', '광고그룹', 'Unnamed'])), df.columns[0])

def clean_num(series):
    if series is None: return pd.Series(0, index=df.index)
    v = series.astype(str).str.replace(r'[^\d]', '', regex=True)
    return pd.to_numeric(v, errors='coerce').fillna(0)

calc_df = df.copy()
if f_imp: calc_df[f_imp] = clean_num(df[f_imp])
if f_clk: calc_df[f_clk] = clean_num(df[f_clk])
if f_cost: calc_df[f_cost] = clean_num(df[f_cost])

# 정상 분리된 깔끔한 데이터프레임 노출
cols = [c for c in [f_camp, f_imp, f_clk, f_cost] if c and c in df.columns]
st.dataframe(df[cols], use_container_width=True)

t_imp = int(calc_df[f_imp].sum()) if f_imp else 0
t_clk = int(
