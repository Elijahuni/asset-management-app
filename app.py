import streamlit as st
import utils.db as db

st.set_page_config(
    page_title="회사 자산관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 세션 상태 초기화
if "user" not in st.session_state:
    st.session_state["user"] = None

# 로그인 화면
if not st.session_state["user"]:
    # 비로그인 상태일 때는 사이드바를 숨깁니다 (선택사항이나 깔끔함을 위해)
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .stDeployButton {display:none;}
        #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🏢 회사 자산관리 시스템")
    st.markdown("자산 관리 시스템에 접속하려면 로그인이 필요합니다.")
    
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        with st.form("login_form"):
            email_in = st.text_input("이메일")
            pw_in = st.text_input("비밀번호", type="password")
            submit_in = st.form_submit_button("로그인")
            
            if submit_in:
                if not email_in or not pw_in:
                    st.error("이메일과 비밀번호를 모두 입력해주세요.")
                else:
                    res, err = db.sign_in(email_in, pw_in)
                    if err:
                        st.error(f"로그인 실패: {err}")
                    elif res and res.user:
                        st.session_state["user"] = res.user
                        st.session_state["is_admin"] = res.user.email in st.secrets.get("ADMIN_EMAILS", [])
                        st.success("로그인 성공!")
                        st.rerun()

    with tab2:
        with st.form("signup_form"):
            email_up = st.text_input("이메일 (Gmail 전용)")
            name_up = st.text_input("이름 (실명 입력 필수) *")
            pw_up = st.text_input("비밀번호", type="password")
            pw_confirm = st.text_input("비밀번호 확인", type="password")
            submit_up = st.form_submit_button("회원가입")
            
            if submit_up:
                if not email_up or not pw_up or not name_up:
                    st.error("이메일, 이름, 비밀번호를 모두 입력해주세요.")
                elif not email_up.endswith("@gmail.com"):
                    st.error("보안 검토: Gmail(@gmail.com) 계정으로만 가입하실 수 있습니다.")
                elif pw_up != pw_confirm:
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    res, err = db.sign_up(email_up, pw_up, name_up)
                    if err:
                        st.error(f"회원가입 실패: {err}")
                    else:
                        st.success("가입이 성공했습니다! (단, Supabase 설정에 따라 '이메일 인증' 메일 확인이 필요할 수 있습니다. 이미 이메일 인증을 껐다면 로그인을 진행해주세요.)")

else:
    # 로그인 상태일 때 메인 대시보드 진입점
    st.markdown("""
    <style>
        .reportview-container { margin-top: -2em; }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    st.title("🏢 회사 자산관리 시스템")

    admin_status = "👑 관리자 모드" if st.session_state.get("is_admin") else "🧑‍💻 임직원 모드"
    st.markdown(f"### 환영합니다, {st.session_state['user'].user_metadata.get('full_name', st.session_state['user'].email)} 님! ({admin_status})")
    st.markdown("""
    이 어플리케이션은 회사 내 모든 IT 및 사무 자산을 효율적으로 관리하기 위해 만들어졌습니다.

    👈 **왼쪽 사이드바 메뉴**를 통해 각 기능에 접근하세요.

    - **📊 대시보드**: 전체 자산 요약 및 도래하는 알림 확인
    - **📋 자산목록**: 등록된 모든 자산을 확인, 필터링, 그리고 엑셀 추출
    - **➕ 자산등록**: 새로운 자산을 등록하거나 기존 관리 정보 수정
    - **🤝 대여관리**: 자산 대여 현황 및 모니터링, 반납 처리
    - **🕒 이력조회**: 누가, 언제 자산 정보를 변경 및 등록했는지 추적
    
    ---
    """)
    if st.button("로그아웃"):
        db.sign_out()
        st.session_state["user"] = None
        st.rerun()
