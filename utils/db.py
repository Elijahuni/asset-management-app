import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def init_connection() -> Client:
    """Supabase 클라이언트 초기화 및 연결"""
    # secrets.toml에서 정보를 가져옵니다.
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    
    if not url or not key or url == "https://your-project-id.supabase.co":
        st.warning("경고: Supabase URL 또는 Key가 올바르게 설정되지 않았습니다. .streamlit/secrets.toml을 확인해주세요.", icon="⚠️")
        return None
    
    return create_client(url, key)

def get_assets():
    """모든 자산 조회"""
    supabase = init_connection()
    if not supabase: return []
    
    response = supabase.table("assets").select("*").execute()
    return response.data

def get_rentals():
    """모든 대여 내역 조회"""
    supabase = init_connection()
    if not supabase: return []
    
    response = supabase.table("rentals").select("*, assets(name, asset_number)").execute()
    return response.data

def log_history(asset_id: str, change_type: str, description: str):
    """자산 변경 이력 기록"""
    supabase = init_connection()
    if not supabase: return
    
    supabase.table("asset_history").insert({
        "asset_id": asset_id,
        "change_type": change_type,
        "description": description
    }).execute()

def create_asset(data: dict):
    """신규 자산 등록"""
    supabase = init_connection()
    if not supabase: return None
    
    response = supabase.table("assets").insert(data).execute()
    if response.data:
        asset_id = response.data[0]['id']
        log_history(asset_id, "등록", f"자산 등록됨: {data.get('name')}")
        return response.data[0]
    return None

def update_asset(asset_id: str, data: dict, description: str = "자산 정보 수정"):
    """자산 정보 업데이트"""
    supabase = init_connection()
    if not supabase: return None
    
    response = supabase.table("assets").update(data).eq("id", asset_id).execute()
    if response.data:
        log_history(asset_id, "수정", description)
        return response.data[0]
    return None

def retire_asset(asset_id: str, reason: str):
    """자산 폐기 (Soft Delete) 처리"""
    supabase = init_connection()
    if not supabase: return None
    
    # 상태를 '폐기'로 업데이트
    response = supabase.table("assets").update({"status": "폐기"}).eq("id", asset_id).execute()
    if response.data:
        log_history(asset_id, "상태변경", f"자산 폐기 처리됨 (사유: {reason})")
        return response.data[0]
    return None

def create_rental(data: dict):
    """자산 대여 처리"""
    supabase = init_connection()
    if not supabase: return None
    
    response = supabase.table("rentals").insert(data).execute()
    if response.data:
        asset_id = data.get("asset_id")
        # 자산 상태 업데이트
        supabase.table("assets").update({"status": "대여중"}).eq("id", asset_id).execute()
        log_history(asset_id, "상태변경", f"대여됨 (대여자: {data.get('renter')})")
        return response.data[0]
    return None

def return_asset(rental_id: str, asset_id: str, actual_return_date: str):
    """자산 반납 처리"""
    supabase = init_connection()
    if not supabase: return None
    
    # 대여 상태 업데이트
    response = supabase.table("rentals").update({
        "status": "반납완료",
        "actual_return_date": actual_return_date
    }).eq("id", rental_id).execute()
    
    if response.data:
        # 자산 상태 정상으로 변경
        supabase.table("assets").update({"status": "정상"}).eq("id", asset_id).execute()
        log_history(asset_id, "상태변경", "반납처리됨 (상태: 정상)")
        return response.data[0]
    return None

def get_asset_history():
    """모든 이력 조회"""
    supabase = init_connection()
    if not supabase: return []
    
    response = supabase.table("asset_history").select("*, assets(name, asset_number)").order("changed_at", desc=True).execute()
    return response.data

# --- 인증(Auth) 관련 기능 추가 ---
def sign_up(email, password, name):
    supabase = init_connection()
    if not supabase: return None, "DB 연결 오류"
    try:
        res = supabase.auth.sign_up({
            "email": email, 
            "password": password,
            "options": {"data": {"full_name": name}}
        })
        return res, None
    except Exception as e:
        return None, str(e)

def sign_in(email, password):
    supabase = init_connection()
    if not supabase: return None, "DB 연결 오류"
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return res, None
    except Exception as e:
        return None, str(e)

def sign_out():
    supabase = init_connection()
    if not supabase: return
    try:
        supabase.auth.sign_out()
    except:
        pass
