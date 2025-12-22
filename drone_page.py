import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_qrcode_scanner import qrcode_scanner
from google_sheets import GoogleSheetsDB
import qr_logic

# 상세 관리 모듈 임포트
from drone_modules.flight_log import show_flight_log
from drone_modules.repair_log import show_repair_log
from drone_modules.accident_log import show_accident_log

def show_drone_page():
    st.title("🚁 기체 통합 관리 시스템")
    db = GoogleSheetsDB('credentials.json', '드론관리')
    ws_main = db.get_worksheet("기체데이터")

    # ---------------------------------------------------------
    # 1. [신규 기체 등록 섹션] - QR코드 및 수동 등록
    # ---------------------------------------------------------
    with st.expander("🆕 새 기체 등록 및 QR 스캔", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("📷 **QR 코드 인식**")
            # QR 스캐너 실행
            qr_val = qrcode_scanner(key="drone_reg_scanner")
            if qr_val:
                st.success(f"인식된 ID: {qr_val}")
        
        with col2:
            st.write("⌨️ **수동 정보 입력**")
            # QR로 인식된 값이 있으면 자동으로 입력창에 채워줌
            reg_id = st.text_input("기체 ID (Narma_AF_xxxx)", value=qr_val if qr_val else "")
            reg_model = st.text_input("모델명")
            reg_owner = st.text_input("담당자 성함")
            
            if st.button("🚀 기체 신규 등록"):
                if reg_id and qr_logic.verify_qr(reg_id, "기체"):
                    # 시트 저장 (기본 상태값은 FALSE로 초기화)
                    # 순서: ID, 모델명, 담당자, 등록일, 제작완료, 지상테스트완료, 초도비행완료
                    ws_main.append_row([reg_id, reg_model, reg_owner, datetime.now().strftime("%Y-%m-%d"), "FALSE", "FALSE", "FALSE"])
                    st.success(f"기체 {reg_id} 등록 성공!")
                    st.rerun()
                else:
                    st.error("올바른 기체 ID를 입력해 주세요.")

    st.divider()

    # ---------------------------------------------------------
    # 2. [기체 상세 관리 섹션] - 상태 불러오기 및 이력 관리
    # ---------------------------------------------------------
    all_values = ws_main.get_all_values()
    
    if len(all_values) > 1:
        df = pd.DataFrame(all_values[1:], columns=all_values[0])
        
        st.subheader("🔍 기체 상세 이력 관리")
        selected_id = st.selectbox("관리할 기체를 선택하세요", df['ID'].tolist())

        if selected_id:
            # 선택된 기체 데이터 추출
            drone_info = df[df['ID'] == selected_id].iloc[0]
            row_idx = df.index[df['ID'] == selected_id][0] + 2

            # 데이터 정규화 함수 (불러오기 에러 방지)
            def get_bool_state(val):
                return str(val).strip().upper() == "TRUE"

            # 기존 저장된 정보 불러오기
            p_saved = get_bool_state(drone_info.get('제작완료'))
            g_saved = get_bool_state(drone_info.get('지상테스트완료'))
            f_saved = get_bool_state(drone_info.get('초도비행완료'))

            st.markdown(f"**📍 현재 기체:** {selected_id} ({drone_info.get('모델명')})")
            
            # [준비 상태 확인 체크박스]
            c1, c2, c3 = st.columns(3)
            p_ready = c1.checkbox("제작 완료", value=p_saved, key=f"p_{selected_id}")
            g_ready = c2.checkbox("지상 테스트 완료", value=g_saved, key=f"g_{selected_id}")
            f_ready = c3.checkbox("초도 비행 완료", value=f_saved, key=f"f_{selected_id}")

            if st.button("💾 준비 상태 저장"):
                update_vals = [[str(p_ready).upper(), str(g_ready).upper(), str(f_ready).upper()]]
                # E, F, G 열이 상태 열인지 확인 후 업데이트
                ws_main.update(f"E{row_idx}:G{row_idx}", update_vals)
                st.success("정보가 업데이트되었습니다.")
                st.rerun()

            st.divider()

            # [이력 등록 탭] - 3가지 모두 완료 시 노출
            if p_ready and g_ready and f_ready:
                tab1, tab2, tab3 = st.tabs(["📅 비행 정보", "🛠️ 수리/교체", "⚠️ 사고 이력"])
                with tab1: show_flight_log(db, selected_id)
                with tab2: show_repair_log(db, selected_id)
                with tab3: show_accident_log(db, selected_id)
            else:
                st.warning("⚠️ 필수 준비 절차(제작, 지상테스트, 초도비행)를 모두 완료해야 이력을 등록할 수 있습니다.")
    else:
        st.info("등록된 기체가 없습니다. 상단의 '새 기체 등록' 메뉴를 이용해 주세요.")