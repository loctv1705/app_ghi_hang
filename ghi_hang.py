import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re

FILENAME = "data.xlsx"

st.title("📦 Ghi số lượng hàng hóa mỗi ngày")
thoi_gian = datetime.now().strftime("%d/%m/%Y %H:%M")
st.write("🕒 Ngày giờ:", thoi_gian)

nguon_hang = st.selectbox("Nhà:", ['Khang', 'Tú Thảo', 'Đạt', 'Ái'])

def ghi_hang(nguon_hang=nguon_hang):
    loai_hang = {'Tú Thảo': ['Sơ mi cầu vai', 'Sơ mi không cầu vai', 'Quần dài', 'Quần short', 'Áo thun'],
                'Khang': ['Sơ mi', 'Quần dài', 'Quần short', 'Áo thun'],
                'Đạt': ['5 nút', '6 nút', '7 nút', 'Quần', 'Áo thun'],
                'Ái': ['Khuy lưng', 'Sọc sườn']}

    loai_hang = st.selectbox("Loại hàng:", loai_hang[nguon_hang])

    if loai_hang not in ['Quần dài', 'Quần short', 'Áo thun', 'Quần'] and nguon_hang != 'Ái':
        gender = st.selectbox("Nam/nữ:", ["Nam", "Nữ"])
    else:
        gender = None

    so_luong = st.number_input("Nhập số lượng:", min_value=0, step=1)
    ds_truong = {'Tú Thảo': ['Lữ Gia', 'Lê Lợi', 'Đoàn Thị Điểm', 'Collete', 'Trần Phú', 
                            'CMT8', 'Sương Nguyệt Anh', 'Không'],
                'Khang': ['An Nhơn', 'Phạm Hữu Lầu', 'Yên Thế', 'Rạng Đông', 'Không'],
                'Đạt': ['Lê Văn Nghề', 'Không']}
    if not re.match(r"(^Quần)", loai_hang) and nguon_hang != 'Ái':
        truong = st.selectbox("Trường:", ds_truong[nguon_hang])
    else:
        truong = None
    ghi_chu = st.text_input("Ghi chú (tùy chọn):")

    now = datetime.now()
    ngay = now.strftime('%d/%m/%Y')
    gio = now.strftime('%H:%M:%S')

    new_data = pd.DataFrame([[ngay, gio, nguon_hang, loai_hang, gender, so_luong, truong, ghi_chu]],
                            columns=["Ngày", "Giờ", "Nguồn", "Loại hàng", "Nam/Nữ", "Số lượng", "Trường", "Mô tả"])
    
    return new_data

new_data = ghi_hang(nguon_hang=nguon_hang)
st.write("Xác nhận lại trước khi ghi dữ liệu") # reset lại index và bỏ index cũ
st.dataframe(new_data)

if st.button("Ghi dữ liệu"):

    if not os.path.exists(FILENAME):
        with pd.ExcelWriter(FILENAME, engine='openpyxl') as writer:
            new_data.to_excel(writer, sheet_name=nguon_hang, index=False)
    else:
        # Nếu file đã tồn tại
        try:
            df_old = pd.read_excel(FILENAME, sheet_name=nguon_hang)
            df = pd.concat([df_old, new_data], ignore_index=True)
        except ValueError:
            # Sheet chưa tồn tại → bắt lỗi
            df = new_data

        # Ghi đè lại đúng sheet
        with pd.ExcelWriter(FILENAME, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=nguon_hang, index=False)

    st.success("✅ Đã ghi dữ liệu!")

if st.button("Xem dữ liệu"):
    df = pd.read_excel(FILENAME)
    st.dataframe(df)