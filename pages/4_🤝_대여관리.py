import streamlit as st
import pandas as pd
from datetime import datetime
import utils.db as db

st.set_page_config(page_title="대여관리", page_icon="🤝", layout="wide")

if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("로그인이 필요합니다. 홈으로 돌아가 로그인해주세요.")
    st.stop()

st.title("🤝 대여 관리")

tab1, tab2 = st.tabs(["대여 등록", "현재 대여/반납 관리"])

assets = db.get_assets()

with tab1:
    st.subheader("신규 대여 등록")
    if not assets:
        st.warning("등록된 자산이 없습니다.")
    else:
        df_assets = pd.DataFrame(assets)
        # 대여 가능한 정상 자산만 필터링
        available_assets = df_assets[df_assets['status'] == '정상']
        
        if available_assets.empty:
            st.info("현재 대여 가능한 '정상' 상태의 자산이 없습니다.")
        else:
            asset_options = {row['id']: f"{row['name']} ({row['asset_number']})" for _, row in available_assets.iterrows()}
            
            with st.form("rental_form"):
                selected_asset_id = st.selectbox("대여할 자산 선택", list(asset_options.keys()), format_func=lambda x: asset_options[x])
                
                # 대여자는 로그인한 사용자의 이름으로 자동 고정
                user_name = st.session_state["user"].user_metadata.get("full_name", "알 수 없음")
                renter = st.text_input("대여자 이름 (자동 지정됨) *", value=user_name, disabled=True)
                
                rental_date = st.date_input("대여일", datetime.today())
                expected_return_date = st.date_input("반납예정일")
                
                submit = st.form_submit_button("대여 처리")
                if submit:
                    if not renter:
                        st.error("대여자를 입력해주세요.")
                    elif expected_return_date < rental_date:
                        st.error("반납예정일은 대여일보다 같거나 늦어야 합니다.")
                    else:
                        data = {
                            "asset_id": selected_asset_id,
                            "renter": renter,
                            "rental_date": rental_date.strftime("%Y-%m-%d"),
                            "expected_return_date": expected_return_date.strftime("%Y-%m-%d")
                        }
                        result = db.create_rental(data)
                        if result:
                            st.success(f"{asset_options[selected_asset_id]} 자산이 대여 처리되었습니다.")
                        else:
                            st.error("대여 처리 중 오류가 발생했습니다.")

with tab2:
    st.subheader("대여 내역 및 반납")
    rentals = db.get_rentals()
    
    if not rentals:
        st.info("대여 이력이 없습니다.")
    else:
        df_rentals = pd.DataFrame(rentals)
        # 테이블 파싱
        df_rentals['asset_name'] = df_rentals['assets'].apply(lambda x: x['name'] if x else '알수없음')
        df_rentals['asset_number'] = df_rentals['assets'].apply(lambda x: x['asset_number'] if x else '알수없음')
        
        # 권한 기반 필터링: 관리자가 아니면 로그인한 유저의 대여내역만 필터링
        user_name = st.session_state["user"].user_metadata.get("full_name", "알 수 없음")
        if not st.session_state.get("is_admin", False):
            df_rentals = df_rentals[df_rentals['renter'] == user_name]
            
        if df_rentals.empty:
            st.info("열람 가능한 대여 내역이 없습니다.")
        else:
            # 현재 대여중인 항목들
            current_rentals = df_rentals[df_rentals['status'] == '대여중']
            
            if current_rentals.empty:
                st.success("현재 대여 중인 자산이 없습니다.")
            else:
                for _, row in current_rentals.iterrows():
                    with st.expander(f"{row['asset_name']} ({row['asset_number']}) - 대여자: {row['renter']}"):
                        st.write(f"**대여일:** {row['rental_date']}")
                        st.write(f"**반납 예정일:** {row['expected_return_date']}")
                        
                        if st.button("반납 완료 처리", key=f"return_{row['id']}"):
                            actual_return_date = datetime.now().strftime("%Y-%m-%d")
                            res = db.return_asset(row['id'], row['asset_id'], actual_return_date)
                            if res:
                                st.success("반납 처리가 완료되었습니다. 새로고침을 해주세요.")
                                st.rerun()
                            else:
                                st.error("반납 처리에 실패했습니다.")
                                
            # 일반 임직원용: 과거 반납 완료 내역
            if not st.session_state.get("is_admin", False):
                st.markdown("---")
                st.markdown("#### 나의 과거 반납 이력")
                past_rentals = df_rentals[df_rentals['status'] == '반납완료']
                
                if past_rentals.empty:
                    st.write("과거에 완료된 대여 이력이 없습니다.")
                else:
                    display_past = past_rentals[['asset_name', 'asset_number', 'rental_date', 'actual_return_date']].rename(columns={
                        'asset_name': '자산명', 'asset_number': '자산번호', 'rental_date': '대여일', 'actual_return_date': '실제 반납일'
                    })
                    st.dataframe(display_past, use_container_width=True, hide_index=True)
