import streamlit as st
from datetime import datetime
import pandas as pd
from streamlit_qrcode_scanner import qrcode_scanner
from google_sheets import GoogleSheetsDB
import qr_logic

def show_battery_page():
    st.title("🔋 배터리 상태 관리")
    db = GoogleSheetsDB('credentials.json', '드론관리')
    ws = db.get_worksheet("배터리데이터")
    
    # --- [섹션 1: 등록된 배터리 목록] ---
    st.subheader("📋 배터리 재고 현황")
    data = ws.get_all_records()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("등록된 배터리가 없습니다.")

    # --- [섹션 2: 입력 방식 선택] ---
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📷 QR 스캔")
        with st.expander("카메라 열기"):
            qr_val = qrcode_scanner(key="bat_scan")
    with c2:
        st.subheader("⌨️ 수동 입력")
        manual_id = st.text_input("배터리 S/N 입력 (예: NARMA_BT_0001)")

    target_id = qr_val if qr_val else manual_id

    if target_id:
        if qr_logic.verify_qr(target_id, "배터리"):
            existing = db.fetch_data(ws, target_id)
            
            with st.form("bat_form"):
                st.write(f"📍 대상 S/N: **{target_id}**")
                cycle = st.number_input("충전 횟수", min_value=0, value=int(existing['충전횟수']) if existing is not None else 0)
                status = st.selectbox("상태", ["정상", "점검필요", "폐기"], 
                                     index=["정상", "점검필요", "폐기"].index(existing['상태']) if existing is not None else 0)
                
                if st.form_submit_button("배터리 데이터 저장"):
                    if existing is not None:
                        row = ws.find(target_id).row
                        ws.update(range_name=f"B{row}:C{row}", values=[[cycle, status]])
                        st.success("배터리 상태가 업데이트되었습니다.")
                    else:
                        ws.append_row([target_id, cycle, status, datetime.now().strftime("%Y-%m-%d")])
                        st.success("신규 배터리가 등록되었습니다.")
                    st.rerun()
        else:
            st.error("배터리 QR/ID 형식이 올바르지 않습니다 (NARMA_BT_ 시작 필요)")