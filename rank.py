import streamlit as st
import pandas as pd
import time
import hmac
import hashlib
import base64
import urllib.request
import urllib.parse
import json
from io import BytesIO

# 웹사이트 기본 설정
st.set_page_config(page_title="네이버 검색광고 대시보드 최종형", layout="wide")
st.title("🚀 네이버 검색광고 공식 API 연동 모니터링 도구")
st.markdown("네이버 공식 API를 연결하여 차단 없이 **실시간 키워드 데이터 및 대시보드**를 조회합니다.")

# 사이드바 설정창
with st.sidebar:
    st.header("🔐 네이버 API 인증 정보")
    st.caption("네이버 검색광고 시스템 [도구 > SA API 사용 관리]에서 확인 가능합니다.")
    
    cust_id = st.text_input("1. CUSTOMER_ID (고객 ID)", type="password")
    api_key = st.text_input("2. API_KEY (라이선스 키)", type="password")
    secret_key = st.text_input("3. SECRET_KEY (비밀키)", type="password")
    
    st.divider()
    st.header("⚙️ 조회 설정")
    input_keywords = st.text_input("분석할 키워드 (쉼표로 구분)", "뷰티디바이스, 수분크림")
    run_button = st.button("📊 실시간 API 데이터 가져오기")

# [네이버 공식 가이드라인 표준 Signature 로직]
def make_signature(timestamp, method, uri, secret_key):
    message = f"{timestamp}\n{method}\n{uri}"
    secret_bytes = bytes(secret_key.strip(), 'utf-8')
    message_bytes = bytes(message, 'utf-8')
    
    signing_mac = hmac.new(secret_bytes, message_bytes, digestmod=hashlib.sha256)
    return base64.b64encode(signing_mac.digest()).decode('utf-8')

# 네이버 키워드 데이터 조회 함수 (urllib 표준 방식 전환)
def get_keyword_stats(keywords_list, cust_id, api_key, secret_key):
    pure_uri = "/ncc/keywordstats"
    method = "GET"
    
    clean_cust_id = str(cust_id).strip()
    clean_api_key = str(api_key).strip()
    clean_secret_key = str(secret_key).strip()
    
    current_timestamp = str(int(time.time() * 1000))
    signature = make_signature(current_timestamp, method, pure_uri, clean_secret_key)
    
    # URL 파라미터 조립
    kw_query = ",".join([k.strip() for k in keywords_list])
    params = {"keywords": kw_query}
    url_params = urllib.parse.urlencode(params)
    request_url = f"https://api.naver.com{pure_uri}?{url_params}"
    
    req = urllib.request.Request(request_url, method=method)
    req.add_header("X-Timestamp", current_timestamp)
    req.add_header("X-API-KEY", clean_api_key)
    req.add_header("X-Customer", clean_cust_id)
    req.add_header("X-Signature", signature)
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_code = response.getcode()
            if res_code == 200:
                res_data = response.read().decode('utf-8')
                data = json.loads(res_data)
                return pd.DataFrame(data.get("keywordList", []))
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8') if e.read() else ""
        st.error(f"❌ 네이버 API 통신 실패 (에러코드: {e.code})")
        st.warning("⚠️ 인증 키 값 점검 요망:")
        st.info("네이버는 API Key, Secret Key, 고객 ID 중 하나만 틀려도 보안상 404 에러를 던집니다. 광고주센터 [SA API 사용 관리] 화면에서 복사할 때 앞뒤로 빈 공백이 들어가지 않았는지 반드시 메모장에 붙여넣어 확인해 주세요!")
        return None
    except Exception as e:
        st.error(f"⚠️ 연결 중 오류 발생: {e}")
        return None

# 실행 버튼 클릭 시
if run_button:
    if not (cust_id and api_key and secret_key):
        st.error("⚠️ 네이버 API 인증 정보 3가지를 모두 입력해 주세요!")
    else:
        kw_list = [k.strip() for k in input_keywords.split(",")]
        
        with st.spinner("🔄 네이버 공식 광고 서버에서 데이터를 안전하게 가져오는 중..."):
            df_result = get_keyword_stats(kw_list, cust_id, api_key, secret_key)
            
        if df_result is not None and not df_result.empty:
            df_result = df_result.rename(columns={
                'relKeyword': '키워드',
                'monthlyPcQcCnt': '월간 PC 검색수',
                'monthlyMobileQcCnt': '월간 모바일 검색수',
                'monthlyAvePcClkCnt': '월간 PC 평균 클릭수',
                'monthlyAveMobileClkCnt': '월간 모바일 평균 클릭수',
                'monthlyAvePcCtr': 'PC 평균 CTR (%)',
                'monthlyAveMobileCtr': '모바일 평균 CTR (%)'
            })
            
            st.subheader("📊 실시간 매체 데이터 대시보드")
            st.dataframe(df_result, use_container_width=True)
            
            # 마케팅 인사이트
            st.subheader("💡 채널별 타겟팅 가이드")
            for index, row in df_result.iterrows():
                kw = row["키워드"]
                try:
                    pc_search = int(str(row['월간 PC 검색수']).replace('<', '').replace(',', '').strip())
                except:
                    pc_search = 0
                try:
                    mo_search = int(str(row['월간 모바일 검색수']).replace('<', '').replace(',', '').strip())
                except:
                    mo_search = 0
                
                st.markdown(f"**📍 [{kw}] 매체 가치 분석**")
                if mo_search > pc_search * 3:
                    st.info(f"📱 모바일 검색 비중이 PC보다 **압도적으로 높습니다** (모바일 {mo_search:,}건 / PC {pc_search:,}건). 광고 예산 배정을 모바일에 80% 이상 집중하세요.")
                else:
                    st.success(f"🖥️ PC와 모바일 밸런스가 좋습니다 (모바일 {mo_search:,}건 / PC {pc_search:,}건). 두 매체 모두 모니터링이 필요합니다.")
                st.write("---")
                
            # 엑셀 다운로드
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_result.to_excel(writer, sheet_name='네이버_API_리포트', index=False)
                
            st.download_button(
                label="📄 API 원본 리포트 다운로드",
                data=output.getvalue(),
                file_name=f"naver_api_report_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.ms-excel"
            )
