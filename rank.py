import streamlit as st
import pandas as pd
import time
import hmac
import hashlib
import base64
import requests
import json

# 페이지 설정
st.set_page_config(page_title="네이버 키워드 조회 도구", layout="wide")
st.title("🚀 네이버 검색광고 키워드 조회 API")

# 사이드바 설정
with st.sidebar:
    st.header("🔑 API 인증 정보")
    cust_id = st.text_input("CUSTOMER_ID (고객 ID)", type="password")
    api_key = st.text_input("API_KEY (라이선스 키)", type="password")
    secret_key = st.text_input("SECRET_KEY (비밀키)", type="password")

# [핵심] 서명 생성 로직 (네이버 공식 규격)
def get_signature(timestamp, method, uri, secret_key):
    # 공식 규격: timestamp + "." + method + "." + uri
    message = f"{timestamp}.{method}.{uri}"
    secret_bytes = bytes(secret_key.strip(), 'utf-8')
    message_bytes = bytes(message, 'utf-8')
    
    hash_obj = hmac.new(secret_bytes, message_bytes, digestmod=hashlib.sha256)
    return base64.b64encode(hash_obj.digest()).decode('utf-8')

# API 호출 함수
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
    
    # 네이버 키워드 도구는 최대 5개 키워드만 지원
    payload = {
        "hintKeywords": keywords[:5],
        "siteId": None,
        "bizChannel": None
    }
    
    try:
        response = requests.post(base_url + uri, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json().get("keywordList", [])
        else:
            st.error(f"❌ API 통신 실패 (상태 코드: {response.status_code})")
            st.json(response.json()) # 에러 상세 확인
            return None
    except Exception as e:
        st.error(f"오류 발생: {e}")
        return None

# 메인 실행부
input_text = st.text_input("분석할 키워드 입력 (콤마로 구분, 최대 5개)", "뷰티디바이스, 수분크림")
if st.button("데이터 조회"):
    if not (cust_id and api_key and secret_key):
        st.warning("API 인증 정보를 모두 입력해주세요.")
    else:
        keywords = [k.strip() for k in input_text.split(",")]
        with st.spinner("데이터 조회 중..."):
            result = fetch_keyword_data(keywords, cust_id, api_key, secret_key)
            if result:
                df = pd.DataFrame(result)
                st.success("조회 완료!")
                st.dataframe(df)
