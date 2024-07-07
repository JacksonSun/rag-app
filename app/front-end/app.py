import chardet
import pandas as pd
import requests
import streamlit as st

# タイトルの設定
st.title("ツイート感情分析アプリ")
st.write("")
st.write(
    """
    このアプリはTwitterから検索ワードに関するツイートを取得してその内容を感情分析し、
    ポジティブまたはネガティブなツイートのみを表示させるアプリです。
    """
)
st.write("")

url = "http://127.0.0.1:8000/"
response = requests.get(url)

if response.status_code == 200:
    result = response.json()
    st.write(result)
else:
    st.error(f"感情分析エラー:{response.text}")  # APIエラーの表示
