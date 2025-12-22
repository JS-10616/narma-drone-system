import streamlit as st
import pandas as pd
from datetime import datetime

def show_flight_log(db, drone_id):
    st.write(f"### 📅 {drone_id} 비행 정보")
    ws = db.get_worksheet("비행정보")
    
    # 입력 폼
    with st.form("flight_form"):
        col1, col2 = st.columns(2)
        f_date = col1.date_input("비행 날짜")
        f_location = col2.text_input("비행 장소")
        f_time = col1.number_input("비행 시간(분)", min_value=1)
        f_purpose = col2.selectbox("비행 목적", ["테스트", "점검", "방제", "촬영"])
        f_worker = st.text_input("비행 담당자 성함") # 기존 유지 (수동 입력)
        f_note = st.text_area("비행 내용")
        
        if st.form_submit_button("비행 기록 저장"):
            # 1. [추가] 세션에서 로그인한 사용자의 이름을 가져옴 (app.py에서 로그인 시 저장된 값)
            current_user = st.session_state.get('user_name', 'Unknown')
            
            # 2. [수정] append_row 리스트의 맨 끝에 current_user를 추가
            ws.append_row([
                drone_id, 
                str(f_date), 
                f_location, 
                f_time, 
                f_purpose, 
                f_worker, # 사용자가 직접 쓴 담당자
                f_note, 
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # 저장 시간(초까지)
                current_user # ⭐ 자동으로 찍히는 시스템 등록자
            ])
            st.success(f"저장되었습니다. (등록자: {current_user})")
            st.rerun()

    # 이력 조회 (기존 로직 유지)
    st.write("#### 🔍 과거 비행 이력")
    all_values = ws.get_all_values()

    if len(all_values) > 1:
        # 데이터프레임 생성을 위한 헤더 처리 (중복/빈 열 방지 로직 권장)
        raw_headers = all_values[0]
        valid_indices = [i for i, h in enumerate(raw_headers) if h.strip() != ""]
        clean_headers = [raw_headers[i] for i in valid_indices]
        clean_rows = [[row[i] if i < len(row) else "" for i in valid_indices] for row in all_values[1:]]
        
        df = pd.DataFrame(clean_rows, columns=clean_headers)
        
        if '기체ID' in df.columns:
            filtered_df = df[df['기체ID'] == drone_id]
            if not filtered_df.empty:
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.info("해당 기체의 비행 이력이 없습니다.")
    else:
        st.info("등록된 비행 정보가 없습니다.")
