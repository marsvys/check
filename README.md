# 📋 ระบบเช็คชุดนักเรียน (Uniform Check-In App)

Streamlit web app สำหรับเช็คชุดและการมาเรียนทุกวันจันทร์–ศุกร์

---

## ฟีเจอร์

| หน้า | รายละเอียด |
|------|------------|
| 📅 เช็คชุดรายวัน | เช็คชื่อ, สถานะการมา, ชุดครบ/ไม่ครบ, เลือกรายการที่ขาด |
| 📊 สรุปรายวัน | ตาราง + กราฟรายการที่ขาดบ่อย + ดาวน์โหลด CSV |
| 📈 สรุปรายสัปดาห์ | ตารางสีตามสถานะ + นับจำนวนรายคน + CSV |
| 📆 สรุปรายเดือน | ภาพรวมทั้งเดือน + อันดับขาดมาก/สายมาก/ชุดไม่ครบ + กราฟ |
| ⚙️ ตั้งค่า | แก้ไขรายชื่อนักเรียนและรายการชุด |

---

## 🚀 วิธี Deploy บน Streamlit Cloud (ฟรี)

### ขั้นตอนที่ 1 — อัปโหลดขึ้น GitHub

1. เข้า [github.com](https://github.com) แล้วสร้าง repository ใหม่ (เช่น `uniform-checker`)
2. อัปโหลดไฟล์ทั้งหมด:
   ```
   uniform-checker/
   ├── app.py
   ├── requirements.txt
   ├── .gitignore
   └── README.md
   ```
3. Push ขึ้น branch `main`

### ขั้นตอนที่ 2 — Deploy บน Streamlit Cloud

1. ไปที่ [share.streamlit.io](https://share.streamlit.io) แล้ว Sign in ด้วย GitHub
2. กด **"New app"**
3. เลือก Repository → Branch `main` → Main file: `app.py`
4. กด **"Deploy!"**

แอปจะ live ที่ URL แบบนี้:
`https://your-username-uniform-checker-app-xxxx.streamlit.app`

---

## ⚠️ หมายเหตุเรื่องข้อมูล

ข้อมูลจะถูกเก็บใน `data/` folder บนเซิร์ฟเวอร์ของ Streamlit Cloud  
บน free tier ข้อมูลอาจหายเมื่อแอป restart (เมื่อไม่มีคนใช้นานๆ)

**แนะนำ:** ดาวน์โหลด CSV รายสัปดาห์/รายเดือนเก็บไว้เป็น backup เสมอ

---

## 💻 รันบนเครื่องตัวเอง

```bash
pip install -r requirements.txt
streamlit run app.py
```

เปิด `http://localhost:8501` ในเบราว์เซอร์
