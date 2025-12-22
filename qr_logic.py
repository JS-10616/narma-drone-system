#QR코드 검증
def verify_qr(qr_code, expected_mode):
    """스캔된 QR이 현재 화면(기체/배터리) 규격에 맞는지 검증"""
    if expected_mode == "기체" and qr_code.startswith("Narma_AF_"):
        return True
    if expected_mode == "배터리" and qr_code.startswith("NARMA_BT_"):
        return True
    return False