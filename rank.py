import streamlit as st
import pandas as pd
import time
import hmac
import hashlib
import base64
import requests
import json

# 웹사이트 설정
st.set_page_config(page_title="네이버 키워드 조회 도구", layout="wide")
st.title("🚀 네이버 검색광고 키워드 조회 도구")

# 사이드바
with st.sidebar:
    cust_id = st.text_input("CUSTOMER_ID", type="password")
    api_key = st.text_input("API_KEY", type="password")
    secret_key = st.text_input("SECRET_KEY", type="password")

# 서명 생성 함수 (공식 규격)
def get_signature(timestamp, method, uri, secret_key):
    message = f"{timestamp}.{method}.{uri}"
    hash = hmac.new(bytes(secret_key, "utf-8"), bytes(message, "utf-8"), hashlib.sha256)
    return base64.b64encode(hash.digest()).decode("utf-8")

# API 호출 함수
def fetch_naver_keywords(keywords, cust_id, api_key, secret_key):
    base_url = "https://api.searchad.naver.com"
    uri = "/keywordstool"
    method = "POST"
    timestamp = str(int(time.time() * 1000))
    
    signature = get_signature(timestamp, method, uri, secret_key)
    
    headers = {
        "X-Timestamp": timestamp,
        "X-API-KEY": api_key,
        "X-Customer": cust_id,
        "X-Signature": signature,
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    # 키워드 도구는 최대 5개까지 조회 가능
    payload = {
        "hintKeywords": keywords[:5], 
        "siteId": None,
        "bizChannel": None
    }
    
    response = requests.post(base_url + uri, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        return response.json().get("keywordList", [])
    else:
        st.error(f"오류 발생: {response.status_code}")
        st.write(response.text)
        return None

# 메인 실행부
input_keywords = st.text_input("분석할 키워드 (쉼표로 구분, 최대 5개)", "뷰티디바이스, 수분크림")
if st.button("조회 시작"):
    if not all([cust_id, api_key, secret_key]):
        st.error("API 정보를 입력해주세요.")
    else:
        kw_list = [k.strip() for k in input_keywords.split(",")]
        data = fetch_naver_keywords(kw_list, cust_id, api_key, secret_key)
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df)
