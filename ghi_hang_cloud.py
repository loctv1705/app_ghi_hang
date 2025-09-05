import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import re, pytz

# --- Kiểm tra mật khẩu ---
def check_password():
    """Hộp thoại nhập mật khẩu"""
    def password_entered():
        if st.session_state["password"] == st.secrets["auth"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # không giữ mật khẩu trong RAM
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Hiện hộp nhập mật khẩu
        st.text_input("🔑 Nhập mật khẩu:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔑 Nhập mật khẩu:", type="password", on_change=password_entered, key="password")
        st.error("❌ Sai mật khẩu, thử lại.")
        return False
    else:
        return True

if check_password():
    # --- Kết nối Google Sheets ---
    SHEET_ID = "1aU9gv0ZUgLqgHA5uYL8t61yp4_hXvvwQeVh66pB4sMo"
    
    creds_dict = st.secrets["gcp_service_account"]
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(dict(creds_dict), scopes=scope)
    client = gspread.authorize(creds)
    
    # Mở Google Sheet
    sheet = client.open_by_key(SHEET_ID)
    
    st.title("📦 Ghi số lượng hàng")
    vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    thoi_gian = datetime.now(vn_tz).strftime("%d/%m/%Y %H:%M")
    st.write("🕒 Ngày giờ:", thoi_gian)
    
    nguon_hang = st.selectbox("Nhà:", ['Khang', 'Tú Thảo', 'Đạt', 'Ái'])
    
    def ghi_hang(nguon_hang=nguon_hang):
        loai_hang = {
            'Tú Thảo': ['Sơ mi cầu vai', 'Sơ mi không cầu vai', 'Quần dài', 'Quần short', 'Áo thun'],
            'Khang': ['Sơ mi', 'Quần dài', 'Quần short', 'Áo thun'],
            'Đạt': ['5 nút', '6 nút', '7 nút', 'Quần', 'Áo thun'],
            'Ái': ['Khuy lưng', 'Sọc sườn']
        }
    
        loai_hang = st.selectbox("Loại hàng:", loai_hang[nguon_hang])
    
        if loai_hang not in ['Quần dài', 'Quần short', 'Áo thun', 'Quần'] and nguon_hang != 'Ái':
            gender = st.selectbox("Nam/nữ:", ["Nam", "Nữ"])
        else:
            gender = None
    
        so_luong = st.number_input("Nhập số lượng:", min_value=0, step=1)
        ds_truong = {
            'Tú Thảo': ['Lữ Gia', 'Lê Lợi', 'Đoàn Thị Điểm', 'Collete', 'Trần Phú', 
                        'CMT8', 'Sương Nguyệt Anh', 'Không'],
            'Khang': ['An Nhơn', 'Phạm Hữu Lầu', 'Yên Thế', 'Rạng Đông', 'Không'],
            'Đạt': ['Lê Văn Nghề', 'Không']
        }
        if not re.match(r"(^Quần)", loai_hang) and nguon_hang != 'Ái':
            truong = st.selectbox("Trường:", ds_truong[nguon_hang])
        else:
            truong = None
        ghi_chu = st.text_input("Ghi chú (tùy chọn):")
    
        now = datetime.now(vn_tz)
        ngay = now.strftime('%d/%m/%Y')
        gio = now.strftime('%H:%M:%S')
    
        new_data = pd.DataFrame(
            [[ngay, gio, nguon_hang, loai_hang, gender, so_luong, truong, ghi_chu]],
            columns=["Ngày", "Giờ", "Nguồn", "Loại hàng", "Nam/Nữ", "Số lượng", "Trường", "Mô tả"]
        )
        
        return new_data
    
    # --- Hiển thị trước khi ghi ---
    new_data = ghi_hang(nguon_hang=nguon_hang)
    st.write("Xác nhận lại trước khi ghi dữ liệu")
    st.dataframe(new_data)
    
    if st.button("Ghi dữ liệu"):
        try:
            # Nếu sheet con (worksheet) đã tồn tại
            try:
                worksheet = sheet.worksheet(nguon_hang)
            except gspread.exceptions.WorksheetNotFound:
                # Nếu chưa có, tạo mới và thêm header
                worksheet = sheet.add_worksheet(title=nguon_hang, rows="1000", cols="20")
                worksheet.append_row(new_data.columns.tolist())  
    
            # Chỉ append dữ liệu mới, không append header nữa
            worksheet.append_row(new_data.values.tolist()[0])  
    
            st.success("✅ Đã ghi dữ liệu vào Google Sheets!")
        except Exception as e:
            st.error(f"❌ Lỗi: {e}")
    
    if st.button("Xem dữ liệu"):
        try:
            worksheet = sheet.worksheet(nguon_hang)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            st.dataframe(df)
        except gspread.exceptions.WorksheetNotFound:
            st.warning("⚠️ Sheet chưa có dữ liệu!")

