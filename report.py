import streamlit as st
import pandas as pd

st.set_page_config(page_title="광고 보고서", layout="wide")
st.title("📊 통합 매체 광고 보고서 생성기")

with st.sidebar:
    media = st.selectbox("매체", ["네이버 SA", "네이버 GFA", "구글", "메타", "카카오"])
    f = st.file_uploader("파일 업로드", type=["csv", "xlsx"])

if not f:
    st.info("👈 왼쪽에서 파일을 업로드해 주세요!"), st.stop()

df = None
if f.name.endswith('.xlsx'):
    df = pd.read_excel(f)
else:
    for e in ['utf-8-sig', 'cp949', 'utf-8', 'euc-kr']:
        try:
            f.seek(0)
            lines = [line.decode(e).strip() for line in f.readlines() if line.strip()]
            if lines:
                parsed = [l.split(',') for l in lines]
                t_idx = 0
                for i, row in enumerate(parsed):
                    if any(k in "".join(row) for k in ['노출', '클릭', '비용', 'Impressions']):
                        t_idx = i; break
                df = pd.DataFrame(parsed[t_idx+1:], columns=[x.strip() for x in parsed[t_idx]])
                break
        except: continue

if df is None or df.empty:
    st.error("⚠️ 파일을 읽을 수 없습니다."), st.stop()

# 컬럼명 정리 및 매칭 사전 구축
df.columns = [str(c).strip() for c in df.columns]

ki = next((c for c in df.columns if any(k in c for k in ['노출수', '노출 수', '노출', 'Impressions', 'Imp'])), None)
kc = next((c for c in df.columns if any(k in c for k in ['클릭수', '클릭 수', '클릭', 'Clicks', '링크 클릭'])), None)
ks = next((c for c in df.columns if any(k in c for k in ['총비용', '광고비', '비용', '소진', '지출', 'Cost'])), None)
kg = next((c for c in df.columns if any(k in c for k in ['캠페인', 'Campaign', '광고상품', '그룹', '키워드'])), df.columns[0])

# 숫자가 아닌 값(따옴표, 콤마 등) 기호 강제 제거 연산
def to_int(col):
    if not col or col not in df.columns: return 0
    return int(pd.to_numeric(df[col].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce').fillna(0).sum())

ni = to_int(ki)
nc = to_int(kc)
ns = to_int(ks)
r = (nc / ni * 100) if ni > 0 else 0
p = (ns / nc) if nc > 0 else 0

st.subheader(f"📝 {media} RAW 데이터 확인")
st.dataframe(df[[c for c in [kg, ki, kc, ks] if c in df.columns
