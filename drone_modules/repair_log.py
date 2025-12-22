import streamlit as st
import pandas as pd
from datetime import datetime

def show_repair_log(db, drone_id):
    st.write(f"### 🛠️ {drone_id} 수리/교체 내역")
    ws = db.get_worksheet("수리부품")
    
    # [1] 데이터 입력 폼 영역
    with st.form("repair_form"):
        col1, col2 = st.columns(2)
        r_date = col1.date_input("수리 날짜")
        r_part = col2.text_input("교체 부품")
        r_worker = col1.text_input("수리 담당자") # 기존 유지 (수동 입력)
        r_note = st.text_area("상세 내용")
        
        if st.form_submit_button("수리 내역 저장"):
            # 1. [추가] 로그인 세션에서 현재 사용자 이름 가져오기
            current_user = st.session_state.get('user_name', 'Unknown')
            
            # 2. [수정] 데이터 리스트 맨 끝에 current_user 추가
            # 구글 시트 구조: 기체ID, 수리날짜, 부품, 내용, 담당자, 등록시간, 시스템등록자
            ws.append_row([
                drone_id, 
                str(r_date), 
                r_part, 
                r_note, 
                r_worker, # 사용자가 직접 쓴 담당자
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # 저장 시간
                current_user # ⭐ 자동으로 찍히는 시스템 등록자
            ])
            st.success(f"저장되었습니다. (등록자: {current_user})")
            st.rerun()

    st.write("---")
    st.write("#### 📜 해당 기체 수리 이력")

    # [2] 데이터 가져오기
    all_values = ws.get_all_values() 

    # [3] 데이터 출력 (빈 열 방지 로직 포함)
    if len(all_values) > 1:
        # 제목 행 처리 (빈 열 제외하여 Duplicate column 에러 방지)
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
                st.info("기록된 수리 내역이 없습니다.")
    else:
        st.info("등록된 전체 데이터가 없습니다.")