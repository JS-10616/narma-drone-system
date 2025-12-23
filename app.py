import streamlit as st
from datetime import datetime
import json

from google_sheets import GoogleSheetsDB
from drone_page import show_drone_page
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent      # .../NarmaDroneApp/app
PROJECT_ROOT = BASE_DIR.parent                  # .../NarmaDroneApp
CRED_PATH = PROJECT_ROOT / "secrets" / "credentials.json"

def init_db():
    """
    배포(Streamlit Cloud): st.secrets[gcp_service_account][json_content]
    로컬: credentials.json
    """
    print("[BOOT] init_db start")

    # Streamlit Cloud Secrets 사용
    if "gcp_service_account" in st.secrets and "json_content" in st.secrets["gcp_service_account"]:
        print("[BOOT] using secrets: gcp_service_account.json_content")
        creds_info = json.loads(st.secrets["gcp_service_account"]["json_content"])
        print("[BOOT] json.loads ok")
        db = GoogleSheetsDB(creds_info, "드론관리")
        print("[BOOT] GoogleSheetsDB init ok (secrets)")
        return db

    # 로컬 credentials.json 사용
    print("[BOOT] using local credentials.json")
    db = GoogleSheetsDB("credentials.json", "드론관리")
    print("[BOOT] GoogleSheetsDB init ok (local)")
    return db


def main():
    st.set_page_config(page_title="나르마 드론 관리 시스템", layout="wide")

    # 1) DB 연결
    try:
        print("[BOOT] main start")
        db = init_db()

        print("[BOOT] fetching worksheet: 사용자계정")
        ws_user = db.get_worksheet("사용자계정")
        print("[BOOT] worksheet ok")

    except Exception as e:
        print(f"[BOOT][ERR] {repr(e)}")
        st.error(f"❌ 연결 실패: {e}")
        return

    # 2) 로그인 상태 관리
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = ""

    # 3) 화면 분기
    if not st.session_state["logged_in"]:
        st.title("🚁 나르마 드론 통합 관리 시스템")
        tab_login, tab_register = st.tabs(["🔒 로그인", "📝 회원가입"])

        with tab_login:
            with st.form("login_form"):
                u_id = st.text_input("아이디")
                u_pw = st.text_input("비밀번호", type="password")

                if st.form_submit_button("로그인"):
                    users = ws_user.get_all_records()
                    user_match = next(
                        (
                            u
                            for u in users
                            if str(u.get("아이디")) == u_id and str(u.get("비밀번호")) == u_pw
                        ),
                        None,
                    )

                    if user_match:
                        approval_status = str(user_match.get("승인여부", "")).strip().upper()
                        if approval_status == "YES":
                            st.session_state["logged_in"] = True
                            st.session_state["user_name"] = user_match.get("이름", "관리자")
                            st.rerun()
                        else:
                            st.warning("⏳ 아직 관리자 승인 대기 중입니다. 관리자에게 문의하세요.")
                    else:
                        st.error("아이디 또는 비밀번호가 일치하지 않습니다.")

        with tab_register:
            with st.form("register_form"):
                st.write("### 신규 계정 등록 신청")
                new_id = st.text_input("아이디 설정")
                new_name = st.text_input("성함")
                new_pw = st.text_input("비밀번호 설정", type="password")
                new_pw_confirm = st.text_input("비밀번호 확인", type="password")

                if st.form_submit_button("가입 신청"):
                    existing_ids = ws_user.col_values(1)

                    if not (new_id and new_name and new_pw):
                        st.warning("모든 정보를 입력해 주세요.")
                    elif new_id in existing_ids:
                        st.error("이미 사용 중인 아이디입니다.")
                    elif new_pw != new_pw_confirm:
                        st.error("비밀번호 확인이 일치하지 않습니다.")
                    else:
                        ws_user.append_row(
                            [
                                new_id,
                                new_name,
                                new_pw,
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "WAIT",
                            ]
                        )
                        st.success("✅ 가입 신청 완료! 관리자에게 문의하여 가입 신청 허가를 받고 로그인 진행해주세요.")

    else:
        st.sidebar.title(f"👤 {st.session_state['user_name']}님")
        if st.sidebar.button("로그아웃"):
            st.session_state["logged_in"] = False
            st.rerun()

        st.sidebar.divider()
        st.sidebar.subheader("📋 메인 메뉴")

        menu = st.sidebar.radio(
            "이동할 페이지 선택",
            ["🚁 기체 관리", "🔋 배터리 관리", "📊 데이터 통계"],
            index=0,
        )

        if menu == "🚁 기체 관리":
            show_drone_page()
        elif menu == "🔋 배터리 관리":
            st.title("🔋 배터리 통합 관리")
            st.write("---")
            st.info("배터리 관리 모듈을 연결해 주세요.")
        elif menu == "📊 데이터 통계":
            st.title("📊 데이터 대시보드")
            st.info("준비 중인 기능입니다.")


if __name__ == "__main__":
    main()


