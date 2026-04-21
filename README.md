# 회사 자산관리 시스템

Streamlit + Supabase 기반의 중소기업용 IT/사무기기 자산 관리 웹 애플리케이션입니다.

---

## 주요 기능

| 기능 | 설명 | 권한 |
|------|------|------|
| 대시보드 | 자산 현황 요약, 감가상각 현황, 보증/유지보수 만료 알림 | 관리자 전용 기능 포함 |
| 자산 목록 | 부서·상태·담당자별 필터링, 엑셀 다운로드 | 전체 (컬럼 일부 관리자 전용) |
| 자산 등록 | 자산번호 자동 생성, 구매정보·보증·유지보수 일정 등록 | 관리자 전용 |
| 대여 관리 | 대여 신청·반납 처리, 대여 이력 조회 | 전체 (본인 대여 내역만 조회) |
| 이력 조회 | 전체 자산 변경 이력 감사 로그 | 관리자 전용 |

---

## 기술 스택

- **Frontend / Framework**: [Streamlit](https://streamlit.io/) 1.40.1
- **Database / Auth**: [Supabase](https://supabase.com/) 2.10.0 (PostgreSQL + RLS)
- **Data 처리**: Pandas 2.2.3
- **Excel 내보내기**: OpenPyXL 3.1.5
- **환경변수 관리**: python-dotenv 1.0.1

---

## 프로젝트 구조

```
asset/
├── app.py                    # 앱 진입점 (로그인, 인증, 네비게이션)
├── requirements.txt          # 패키지 의존성
├── schema.sql                # DB 스키마 및 RLS 정책
├── .streamlit/
│   └── secrets.toml          # Supabase 인증정보 (git 제외)
├── pages/
│   ├── 1_📊_대시보드.py
│   ├── 2_📋_자산목록.py
│   ├── 3_➕_자산등록.py
│   ├── 4_🤝_대여관리.py
│   └── 5_🕒_이력조회.py
└── utils/
    ├── db.py                 # DB CRUD 및 인증
    └── depreciation.py       # 정액법 감가상각 계산
```

---

## 시작하기

### 1. 패키지 설치

```bash
git clone https://github.com/Elijahuni/asset-management-app.git
cd asset-management-app
pip install -r requirements.txt
```

### 2. Supabase 설정

1. [Supabase](https://supabase.com)에서 프로젝트 생성
2. SQL 에디터에서 `schema.sql` 전체 실행
3. Authentication → Providers → Email에서 이메일 인증 비활성화 (개발 편의)

### 3. 환경변수 설정

`.streamlit/secrets.toml` 파일 생성:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
ADMIN_EMAILS = ["admin@gmail.com"]
```

### 4. 로컬 실행

```bash
streamlit run app.py
```

브라우저에서 http://localhost:8501 접속

---

## 클라우드 배포 (Streamlit Cloud)

1. GitHub에 코드 push
2. [share.streamlit.io](https://share.streamlit.io) 접속 후 새 앱 생성
3. 다음 항목 설정:
   - Repository: `Elijahuni/asset-management-app`
   - Branch: `main`
   - Main file: `app.py`
4. Advanced settings → Secrets에 `secrets.toml` 내용 붙여넣기
5. Deploy 클릭

---

## 데이터베이스 구조

| 테이블 | 역할 |
|--------|------|
| `assets` | 자산 기본 정보 (구매정보, 보증, 유지보수 일정 등) |
| `rentals` | 대여/반납 내역 및 상태 추적 |
| `asset_history` | 자산 변경 이력 감사 로그 |

모든 테이블은 UUID PK와 Row Level Security(RLS) 정책을 적용하여 인증된 사용자만 접근 가능합니다.

---

## 권한 구분

- **관리자(Admin)**: `secrets.toml`의 `ADMIN_EMAILS`에 등록된 계정
  - 자산 등록·폐기, 감가상각 현황, 전체 대여 내역, 이력 조회 가능
- **일반 직원(Employee)**: 자산 목록 조회, 본인 대여 신청·반납 가능

---

## 스크린샷

> 추후 추가 예정

---

## 라이선스

MIT License
