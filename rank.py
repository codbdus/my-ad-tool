import streamlit as st
import pandas as pd
import time
import hmac
import hashlib
import base64
import requests
import json

# 페이지 기본 설정
st.set_page_config(page_title="네이버 키워드 조회 도구", layout="wide")
st.title("🚀 네이버 검색광고 키워드 조회 도구")

# 1. API 정보 입력창
with st.sidebar:
    st.header("🔑 API 인증 정보")
    cust_id = st.text_input("CUSTOMER_ID (숫자)", type="password")
    api_key = st.text_input("API_KEY (라이선스 키)", type="password")
    secret_key = st.text_input("SECRET_KEY (비밀키)", type="password")

# 2. 서명 생성 함수 (네이버 규격 준수)
def get_signature(timestamp, method, uri, secret_key):
    message = f"{timestamp}.{method}.{uri}"
    secret_bytes = bytes(secret_key.strip(), 'utf-8')
    message_bytes = bytes(message, 'utf-8')
    hash_obj = hmac.new(secret_bytes, message_bytes, digestmod=hashlib.sha256)
    return base64.b64encode(hash_obj.digest()).decode('utf-8')

# 3. 데이터 조회 함수
def fetch_keyword_data(keywords, cust_id, api_key, secret_key):
    base_url = "https://api.searchad.naver.com"
    uri = "/keywordstool"
    method = "POST"
    timestamp = str(int(time.time() * 1000))
    
    headers = {
        "X-Timestamp": timestamp,
        "X-API-KEY": api_key.strip(),
        "X-Customer": str(cust_id).strip(),
        "X-Signature": get_signature(timestamp, method, uri, secret_key),
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    # 네이버 키워드 도구는 최대 5개 키워드만 지원
    payload = {
        "hintKeywords": keywords[:5],
        "siteId": None,
        "bizChannel": None
    }
    
    response = requests.post(base_url + uri, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json().get("keywordList", [])
    else:
        st.error(f"오류 발생! 코드: {response.status_code}")
        st.json(response.json())
        return None

# 4. 실행부
input_keywords = st.text_input("분석할 키워드 (쉼표로 구분, 최대 5개)", "뷰티디바이스, 수분크림")
if st.button("데이터 조회 시작"):
    if not (cust_id and api_key and secret_key):
        st.warning("API 정보를 모두 입력해주세요.")
    else:
        kw_list = [k.strip() for k in input_keywords.split(",")]
        data = fetch_keyword_data(kw_list, cust_id, api_key, secret_key)
        
        if data:
            st.success("데이터를 성공적으로 가져왔습니다!")
            st.dataframe(pd.DataFrame(data))
