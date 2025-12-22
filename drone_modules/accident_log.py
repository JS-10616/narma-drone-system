import streamlit as st
import pandas as pd
from datetime import datetime

def show_accident_log(db, drone_id):
    st.write(f"### ⚠️ {drone_id} 사고 이력 관리")
    ws = db.get_worksheet("사고이력")
    
    # [1] 사고 이력 입력 폼
    with st.form("accident_form"):
        col1, col2 = st.columns(2)
        a_date = col1.date_input("사고 발생일")
        a_location = col2.text_input("사고 장소")
        a_worker = col1.text_input("보고자/담당자 성함") # 기존 유지 (수동 입력)
        a_cause = col2.selectbox("사고 원인", ["조종 미숙", "기체 결함", "통신 장애", "기상 악화", "기타"])
        a_detail = st.text_area("사고 경위 및 파손 부위 상세")
        
        if st.form_submit_button("사고 이력 등록", type="primary"):
            # 1. [추가] 세션에서 로그인한 사용자의 이름을 가져옴
            current_user = st.session_state.get('user_name', 'Unknown')
            
            # 2. [수정] 데이터 리스트 맨 끝에 current_user 추가
            # 구글 시트 구조: 기체ID, 날짜, 장소, 원인, 상세, 담당자, 등록시간, 시스템등록자
            ws.append_row([
                drone_id, 
                str(a_date), 
                a_location, 
                a_cause, 
                a_detail, 
                a_worker, # 사용자가 직접 쓴 담당자
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # 저장 시간
                current_user # ⭐ 자동으로 찍히는 시스템 등록자
            ])
            st.error(f"⚠️ 사고 데이터가 기록되었습니다. (등록자: {current_user})")
            st.rerun()

    st.write("---")
    st.write("#### 📜 해당 기체 사고 기록 조회")

    # [2] 데이터를 가져오는 코드
    all_values = ws.get_all_values() 

    # [3] 데이터가 있을 경우 표로 출력 (빈 열 방지 로직 적용)
    if len(all_values) > 1:
        # 제목 행 처리 (빈 열 제외)
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
                st.info("해당 기체는 등록된 사고 이력이 없습니다.")
    else:
        st.info("전체 시스템에 등록된 사고 기록이 없습니다.")