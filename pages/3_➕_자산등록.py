import streamlit as st
from datetime import datetime
import utils.db as db

st.set_page_config(page_title="자산등록", page_icon="➕", layout="wide")

if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("로그인이 필요합니다. 홈으로 돌아가 로그인해주세요.")
    st.stop()

if not st.session_state.get("is_admin", False):
    st.error("보안 검토: 이 메뉴는 관리자 전용입니다.")
    st.stop()

st.title("➕ 신규 자산 등록")

st.markdown("새로운 자산을 데이터베이스에 등록합니다.")

CATEGORIES = ["건물", "구축물", "기계장치", "차량구", "공기구비품"]
DEPARTMENTS = ["개발팀", "영업팀", "인사팀", "경영지원팀"]
STATUSES = ["정상", "수리중", "대여중", "폐기"]

with st.form("asset_register_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("자산명 *", placeholder="예: 맥북 프로 16인치 M3")
        category = st.selectbox("자산종류 *", CATEGORIES)
        department = st.selectbox("담당부서 *", DEPARTMENTS)
        
        # 이름은 로그인한 사용자의 이름으로 고정
        user_name = st.session_state["user"].user_metadata.get("full_name", "알 수 없음")
        assignee = st.text_input("담당자 (자동 지정됨)", value=user_name, disabled=True)
        
        location = st.text_input("위치", placeholder="본사 3층 301호")
        
    with col2:
        purchase_date = st.date_input("구매일")
        purchase_price = st.number_input("구매가격 (원)", min_value=0, step=10000)
        status = st.selectbox("상태", STATUSES)
        warranty_expiry_date = st.date_input("보증만료일")
        next_maintenance_date = st.date_input("다음 유지보수일")
        
    notes = st.text_area("비고 (선택)")
    
    submit_button = st.form_submit_button("자산 등록하기")
    
    if submit_button:
        if not name:
            st.error("자산명을 입력해주세요.")
        else:
            # 자산번호 자동생성 로직 (AST-YYYYMMDD-랜덤4자리)
            # 여기서는 편의상 타임스탬프를 이용해 고유번호 생성
            timestamp_part = datetime.now().strftime("%Y%m%d")
            random_part = str(datetime.now().microsecond)[:4]
            auto_asset_number = f"AST-{timestamp_part}-{random_part}"
            
            data = {
                "asset_number": auto_asset_number,
                "name": name,
                "category": category,
                "department": department,
                "assignee": assignee,
                "location": location,
                "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                "purchase_price": purchase_price,
                "status": status,
                "warranty_expiry_date": warranty_expiry_date.strftime("%Y-%m-%d"),
                "next_maintenance_date": next_maintenance_date.strftime("%Y-%m-%d"),
                "notes": notes
            }
            
            result = db.create_asset(data)
            if result:
                st.success(f"자산이 성공적으로 등록되었습니다! (자산번호: {auto_asset_number})")
            else:
                st.error("자산 등록 중 오류가 발생했습니다. DB 연결을 확인하세요.")
