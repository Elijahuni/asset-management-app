# 자산관리 웹 앱 배포 및 설정 가이드 (초보자용)

이 문서는 코딩 및 서버 배포에 익숙하지 않은 초보자 분들을 위해 단계별로 작성되었습니다.

---

## 1. Supabase 접속 및 데이터베이스 셋업

Supabase는 무료로 사용할 수 있는 클라우드 데이터베이스입니다.

1. [Supabase 홈페이지](https://supabase.com/)에 접속하여 GitHub 계정이나 이메일로 **Sign Up / Sign In** 하세요.
2. 대시보드에서 **[New Project]** 버튼을 클릭합니다.
   - Project Name: `asset-management` (자유롭게 지정)
   - Database Password: 강력한 비밀번호 생성 후 **반드시 따로 저장**해두세요.
   - Region: `Seoul (ap-northeast-2)` 선택
   - **[Create new project]** 클릭 (생성까지 약 2~3분 소요)
3. 생성이 완료되면, 왼쪽 메뉴 아이콘 중 **[SQL Editor]** (</> 모양)를 클릭합니다.
4. **[New Query]**를 누른 후, 프로젝트 폴더에 있는 `schema.sql` 파일의 내용을 전부 복사해서 붙여넣습니다.
5. 우측 하단의 **[Run]** 버튼을 눌러 테이블들을 생성합니다. "Success" 메시지가 뜨면 완료된 것입니다.
6. 이제 앱과 연결할 키를 찾습니다. 왼쪽 톱니바퀴 모양 **[Project Settings]** -> **[API]** 메뉴를 클릭하세요.
   - **Project URL**: 이 주소를 복사합니다.
   - **Project API Keys (anon, public)**: 이 키를 복사합니다.
7. 로컬 컴퓨터의 `/Users/riyu/asset/.streamlit/secrets.toml` 파일에 복사한 주소와 키를 각각 붙여넣어 줍니다.

---

## [추가] 1.5. 로그인 편의를 위한 이메일 인증(Confirm email) 해제하기

현재 코드에는 회원가입 및 로그인 기능이 탑재되어 있습니다. 
기본적으로 Supabase는 회원가입 시 이메일 인증 확인을 거쳐야만 로그인이 되도록 설정되어 있는데, 실제 메일 서버 연동 등의 번거로움을 피하기 위해 이 설정을 해제하시면 좋습니다.

1. Supabase 대시보드의 왼쪽 메뉴 중 자물쇠 모양의 **[Authentication]** 을 클릭합니다.
2. 하단의 **[Providers]** 항목을 클릭하고, **Email** 항목을 눌러 봅니다.
3. 거기서 **Confirm email** 이라는 토글 스위치를 찾아 회색(Off)상태로 끕니다.
4. 아래쪽의 초록색 **[Save]**를 누릅니다.
이제 앱에서 회원가입을 하면 즉시 로그인을 할 수 있습니다!

---

## 2. GitHub에 코드 업로드하기

Streamlit Cloud는 GitHub에 올라간 코드를 바탕으로 무료 배포를 진행합니다.

1. [GitHub 홈페이지](https://github.com/)에 로그인하고 우측 상단의 **[+]** -> **[New repository]**를 클릭합니다.
2. Repository Name에 `asset-management-app` 등 적당한 이름을 적습니다.
3. Private 또는 Public 여부 선택 후 **[Create repository]**를 클릭합니다.
4. Mac의 '터미널(Terminal)'을 열고 다음 명령어를 한 줄씩 차례대로 입력하세요.
   ```bash
   cd /Users/riyu/asset
   git init
   git add .
   git commit -m "첫 자산관리 앱 업로드"
   git branch -M main
   git remote add origin [방금 생성한 깃허브 Repository의 URL (.git 으로 끝남)]
   git push -u origin main
   ```
5. GitHub 홈페이지를 새로고침 해보면 내 코드가 올라간 것을 볼 수 있습니다.

---

## 3. Streamlit Cloud를 통해 링크 앱으로 만들기

1. [Streamlit 커뮤니티 클라우드](https://share.streamlit.io/)에 접속하여 GitHub 계정으로 로그인합니다.
2. 우측 상단 **[New app]** 버튼을 클릭합니다.
3. "Deploy an app" 화면에서 설정합니다.
   - **Repository**: 방금 만든 `asset-management-app`을 선택
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. **[중요 - Advanced settings 클릭]**
   - 팝업창에서 `Secrets` 영역이 보일 것입니다.
   - 여기에 로컬에서 작성했던 `.streamlit/secrets.toml`의 내용을 똑같이 복사해서 붙여넣습니다:
     ```toml
     SUPABASE_URL = "https://..."
     SUPABASE_KEY = "ey..."
     ```
   - Save를 누릅니다.
5. 우측 하단의 **[Deploy]** 버튼을 클릭합니다!
6. 풍선이 날아가며 배포가 시작되고, 수 분 내로 앱이 완성됩니다.
7. 완성된 앱의 브라우저 주소(URL)를 복사하여 팀원들에게 공유하면 누구나 접속해서 사용할 수 있습니다!
