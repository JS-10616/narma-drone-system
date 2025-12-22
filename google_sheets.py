#구글시트 데이터베이스 모듈
import gspread
import pandas as pd

class GoogleSheetsDB:
    def __init__(self, json_file, sheet_name):
        self.gc = gspread.service_account(filename=json_file)
        self.sh = self.gc.open(sheet_name)

    def get_worksheet(self, title):
        try:
            return self.sh.worksheet(title)
        except gspread.exceptions.WorksheetNotFound:
            # 시트가 없으면 헤더와 함께 생성
            if "기체" in title:
                ws = self.sh.add_worksheet(title=title, rows="1000", cols="10")
                ws.append_row(["ID", "모델명", "담당자", "등록일"])
            else:
                ws = self.sh.add_worksheet(title=title, rows="1000", cols="10")
                ws.append_row(["ID", "충전횟수", "상태", "등록일"])
            return ws

    def fetch_data(self, ws, id_value):
        all_data = ws.get_all_records()
        df = pd.DataFrame(all_data)
        if not df.empty and id_value in df.iloc[:, 0].values:
            return df[df.iloc[:, 0] == id_value].iloc[0]
        return None