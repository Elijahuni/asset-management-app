import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import utils.db as db
import utils.depreciation as dep

st.set_page_config(page_title="대시보드", page_icon="📊", layout="wide")

if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("로그인이 필요합니다. 홈으로 돌아가 로그인해주세요.")
    st.stop()

st.title("📊 메인 대시보드")

# 데이터 로드
assets = db.get_assets()

if not assets:
    st.info("현재 등록된 자산이 없거나 데이터베이스에 연결되지 않았습니다.")
else:
    df = pd.DataFrame(assets)
    
    # 1. 요약 카드
    st.subheader("자산 현황 요약")
    col1, col2, col3, col4 = st.columns(4)
    
    total_assets = len(df)
    rented_assets = len(df[df['status'] == '대여중'])
    repair_assets = len(df[df['status'] == '수리중'])
    disposed_assets = len(df[df['status'] == '폐기'])
    
    with col1:
        st.metric("총 자산", f"{total_assets} 개")
    with col2:
        st.metric("대여 중", f"{rented_assets} 개")
    with col3:
        st.metric("수리 중", f"{repair_assets} 개")
    with col4:
        st.metric("폐기", f"{disposed_assets} 개")

    if st.session_state.get("is_admin", False):
        st.markdown("---")
        st.subheader("💰 회사 회계 자산 요약 (현재 가치, 5년 정액법 기준)")
        
        # 폐기 안된 자산 대상
        active_assets = df[df['status'] != '폐기'].copy()
        
        active_assets['purchase_price'] = pd.to_numeric(active_assets['purchase_price'], errors='coerce').fillna(0)
        total_original_price = active_assets['purchase_price'].sum()
        
        active_assets['residual_value'] = active_assets.apply(lambda row: dep.calculate_residual_value(row.get('purchase_date'), row.get('purchase_price')), axis=1)
        total_residual_value = active_assets['residual_value'].sum()
        
        depreciation_loss = total_original_price - total_residual_value
        residual_percent = (total_residual_value / total_original_price * 100) if total_original_price > 0 else 0
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("총 구매 원가 합계", f"₩ {total_original_price:,.0f}")
        with col_m2:
            st.metric("총 추정 잔존 가치", f"₩ {total_residual_value:,.0f}", delta=f"-₩ {depreciation_loss:,.0f} (감가상각 에상액)", delta_color="inverse")
        with col_m3:
            st.metric("자산 가치 보존율", f"{residual_percent:.1f}%")

        st.markdown("---")
        st.subheader("🔔 알림 (30일 이내 도래)")
        
        col_a, col_b = st.columns(2)
    
        today = datetime.now().date()
        thirty_days_later = today + timedelta(days=30)
        
        # 날짜 필드 형변환 안전하게 처리
        df['warranty_expiry_date'] = pd.to_datetime(df['warranty_expiry_date']).dt.date
        df['next_maintenance_date'] = pd.to_datetime(df['next_maintenance_date']).dt.date
    
        with col_a:
            st.markdown("#### 🛡️ 보증기간 만료 임박")
            warranty_warning = df[
                (df['warranty_expiry_date'] >= today) & 
                (df['warranty_expiry_date'] <= thirty_days_later)
            ]
            if not warranty_warning.empty:
                for _, row in warranty_warning.iterrows():
                    days_left = (row['warranty_expiry_date'] - today).days
                    st.warning(f"**{row['name']}** ({row['asset_number']}) - 만료일: {row['warranty_expiry_date']} (D-{days_left})")
            else:
                st.success("30일 이내 보증기간 만료 자산이 없습니다.")

        with col_b:
            st.markdown("#### 🔧 유지보수 도래 임박")
            maint_warning = df[
                (df['next_maintenance_date'] >= today) & 
                (df['next_maintenance_date'] <= thirty_days_later)
            ]
            if not maint_warning.empty:
                for _, row in maint_warning.iterrows():
                    days_left = (row['next_maintenance_date'] - today).days
                    st.error(f"**{row['name']}** ({row['asset_number']}) - 점검일: {row['next_maintenance_date']} (D-{days_left})")
            else:
                st.success("30일 이내 유지보수 도래 자산이 없습니다.")
