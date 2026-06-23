import streamlit as st
import pandas as pd
import time
import hmac
import hashlib
import base64
import requests
import json

# 페이지 기본 설정
st.set_page_config(page_title="네이버 키워드 도구 API", layout="wide")
st.title("🚀 네이버 검색광고 키워드 도구 API")

# 1. API 정보 입력
with st.sidebar:
    st.header("🔑 API 인증 정보")
    cust_id = st.text_input("CUSTOMER_ID (고객 ID)", type="password")
    api_key = st.text_input("API_KEY (라이선스 키)", type="password")
    secret_key = st.text_input("SECRET_KEY (비밀키)", type="password")

# 2. 서명 생성 함수 (네이버 규격 고정)
def get_signature(timestamp, method, uri, secret_key):
    message = f"{timestamp}.{method}.{uri}"
    secret_bytes = bytes(secret_key.strip(), 'utf-8')
    message_bytes = bytes(message, 'utf-8')
    hash_obj = hmac.new(secret_bytes, message_bytes, digestmod=hashlib.sha256)
    return base64.b64encode(hash_obj.digest()).decode('utf-8')

# 3. API 호출 함수 (오류 해결 버전)
def fetch_keyword_data(keywords, cust_id, api_key, secret_key):
    base_url = "https://api.searchad.naver.com"
    uri = "/keywordstool"
    method = "POST"
    timestamp = str(int(time.time() * 1000))
    
    # 서명 생성
    signature = get_signature(timestamp, method, uri, secret_key)
    
    headers = {
        "X-Timestamp": timestamp,
        "X-API-KEY": api_key.strip(),
        "X-Customer": str(cust_id).strip(),
        "X-Signature": signature,
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    # 400 에러를 방지하기 위해 필수 파라미터를 모두 명시
    # siteId, bizChannel은 null을 허용하지만 구조를 명확히 함
    payload = {
        "hintKeywords": keywords[:5],
        "siteId": None,
        "bizChannel": None
    }
    
    try:
        response = requests.post(base_url + uri, headers=headers, data=json.dumps(payload))
        
        # 상태 코드 확인
        if response.status_code == 200:
            return response.json().get("keywordList", [])
        else:
            st.error(f"❌ API 통신 실패 (상태 코드: {response.status_code})")
            st.code(response.text) # 에러의 상세 원인을 보여줍니다.
            return None
    except Exception as e:
        st.error(f"연결 오류 발생: {e}")
        return None

# 4. 실행부
input_keywords = st.text_input("분석할 키워드 (쉼표로 구분, 최대 5개)", "뷰티디바이스, 수분크림")
if st.button("데이터 조회 시작"):
    if not (cust_id and api_key and secret_key):
        st.warning("API 인증 정보 3가지를 모두 입력해 주세요.")
    else:
        kw_list = [k.strip() for k in input_keywords.split(",")]
        with st.spinner("네이버 서버와 통신 중..."):
            data = fetch_keyword_data(kw_list, cust_id, api_key, secret_key)
            
            if data:
                st.success("데이터 조회 성공!")
                df = pd.DataFrame(data)
                st.dataframe(df)
            else:
                st.error("데이터를 가져오는 데 실패했습니다. 인증 정보를 다시 확인하세요.")
