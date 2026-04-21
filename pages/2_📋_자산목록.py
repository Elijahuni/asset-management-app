import streamlit as st
import pandas as pd
import utils.db as db
import utils.depreciation as dep
from io import BytesIO

st.set_page_config(page_title="자산목록", page_icon="📋", layout="wide")

if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("로그인이 필요합니다. 홈으로 돌아가 로그인해주세요.")
    st.stop()

st.title("📋 전체 자산 목록")

assets = db.get_assets()

if not assets:
    st.info("등록된 자산이 없습니다.")
else:
    df = pd.DataFrame(assets)
    # 컬럼 순서 및 한글명 핑
    display_cols = {
        'asset_number': '자산번호',
        'name': '자산명',
        'category': '자산종류',
        'department': '담당부서',
        'assignee': '담당자',
        'status': '상태',
        'purchase_date': '구매일'
    }
    
    # 관리자만 구매가격(원가)과 위치 정보를 볼 수 있음
    if st.session_state.get("is_admin", False):
        display_cols['purchase_price'] = '구매가격'
        display_cols['residual_value'] = '현재가치(추정)'
        display_cols['location'] = '위치'
        
        # 감가상각 현재 가치 계산 (오직 관리자 뷰일 때만)
        df['residual_value'] = df.apply(lambda row: dep.calculate_residual_value(row.get('purchase_date'), row.get('purchase_price')), axis=1)
        
    # 필터 옵션
    st.markdown("### 필터")
    
    include_retired = st.checkbox("폐기 자산 포함보기", value=False)
    if not include_retired:
        df = df[df['status'] != '폐기']
        
    col1, col2, col3 = st.columns(3)
    
    departments = ["전체"] + list(df['department'].dropna().unique())
    statuses = ["전체"] + list(df['status'].dropna().unique())
    assignees = ["전체"] + list(df['assignee'].dropna().unique())
    
    with col1:
        dept_filter = st.selectbox("부서별", departments)
    with col2:
        status_filter = st.selectbox("상태별", statuses)
    with col3:
        assignee_filter = st.selectbox("담당자별", assignees)
        
    filtered_df = df.copy()
    if dept_filter != "전체":
        filtered_df = filtered_df[filtered_df['department'] == dept_filter]
    if status_filter != "전체":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if assignee_filter != "전체":
        filtered_df = filtered_df[filtered_df['assignee'] == assignee_filter]
        
    st.markdown(f"총 **{len(filtered_df)}** 건")
    
    # 테이블 표시
    display_df = filtered_df[[col for col in display_cols.keys() if col in filtered_df.columns]].rename(columns=display_cols)
    st.dataframe(display_df, use_container_width=True)
    
    # 엑셀 내보내기 기능
    def to_excel(df_to_export):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_to_export.to_excel(writer, index=False, sheet_name='Sheet1')
        processed_data = output.getvalue()
        return processed_data

    excel_data = to_excel(display_df)
    
    st.download_button(
        label="📥 엑셀(.xlsx) 내보내기",
        data=excel_data,
        file_name='asset_list.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # 자산 폐기 관리 UI (관리자 전용)
    if st.session_state.get("is_admin", False):
        st.markdown("---")
        st.subheader("⚠️ 자산 상태 관리 (폐기 처리)")
        st.markdown("더 이상 사용하지 않거나 폐기/매각된 자산을 상태 변경합니다.")
        
        # 폐기 가능한 자산 목록 (정상 또는 대여중, 이미 폐기된 것은 제외)
        retirable_assets = df[df['status'] != '폐기']
        
        if len(retirable_assets) > 0:
            with st.form("retire_asset_form"):
                # 선택지 포맷팅: [자산번호] 자산명
                asset_options = retirable_assets.apply(lambda x: f"[{x['asset_number']}] {x['name']}", axis=1).tolist()
                asset_ids = retirable_assets['id'].tolist()
                
                selected_option = st.selectbox("폐기할 자산 선택", asset_options)
                retire_reason = st.text_input("폐기 사유 (예: 노후화로 인한 매각, 고장 폐기 등)", max_chars=100)
                
                submitted = st.form_submit_button("폐기 처리")
                
                if submitted:
                    if not retire_reason:
                        st.error("폐기 사유를 입력해주세요.")
                    else:
                        selected_index = asset_options.index(selected_option)
                        selected_id = asset_ids[selected_index]
                        
                        db.retire_asset(selected_id, retire_reason)
                        st.success("자산이 성공적으로 폐기 처리되었습니다.")
                        st.rerun()
        else:
            st.info("현재 폐기 처리할 수 있는 자산이 없습니다.")
