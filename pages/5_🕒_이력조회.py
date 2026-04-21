import streamlit as st
import pandas as pd
import utils.db as db

st.set_page_config(page_title="이력조회", page_icon="🕒", layout="wide")

if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("로그인이 필요합니다. 홈으로 돌아가 로그인해주세요.")
    st.stop()

if not st.session_state.get("is_admin", False):
    st.error("보안 검토: 이 메뉴는 관리자 전용입니다.")
    st.stop()

st.title("🕒 자산 변경 이력 조회")

history = db.get_asset_history()

if not history:
    st.info("아직 기록된 변경 이력이 없습니다.")
else:
    df_history = pd.DataFrame(history)
    
    # 조인된 데이터 파싱
    df_history['asset_name'] = df_history['assets'].apply(lambda x: x['name'] if pd.notnull(x) else '삭제된 자산')
    df_history['asset_number'] = df_history['assets'].apply(lambda x: x['asset_number'] if pd.notnull(x) else '-')
    
    df_history['changed_at'] = pd.to_datetime(df_history['changed_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    display_df = df_history[['changed_at', 'asset_number', 'asset_name', 'change_type', 'description']]
    display_df.columns = ['변경 일시', '자산번호', '자산명', '변경 유형', '상세 내용']
    
    # 필터 기능
    st.markdown("### 이력 검색 필터")
    col1, col2 = st.columns(2)
    with col1:
        type_filter = st.selectbox("변경 유형별", ["전체"] + list(df_history['change_type'].unique()))
    with col2:
        search_kw = st.text_input("자산명 또는 자산번호 검색")
        
    if type_filter != "전체":
        display_df = display_df[display_df['변경 유형'] == type_filter]
        
    if search_kw:
        display_df = display_df[display_df['자산명'].str.contains(search_kw) | display_df['자산번호'].str.contains(search_kw)]
        
    st.dataframe(display_df, use_container_width=True)
