import streamlit as st
import json, os, calendar
from datetime import date, timedelta
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="เช็คชุดนักเรียน", page_icon="📋", layout="wide")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }

/* Status badges */
.badge {
    display:inline-block; padding:2px 10px; border-radius:20px;
    font-size:0.78rem; font-weight:600;
}
.badge-present  { background:#d4edda; color:#155724; }
.badge-late     { background:#fff3cd; color:#856404; }
.badge-absent   { background:#f8d7da; color:#721c24; }
.badge-sick     { background:#d1ecf1; color:#0c5460; }

/* Student card */
.student-card {
    background: #ffffff;
    border: 1px solid #e9ecef;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Metric cards */
.metric-box {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 14px 18px;
    text-align: center;
    border: 1px solid #dee2e6;
}
.metric-box .num { font-size:2rem; font-weight:700; }
.metric-box .lbl { font-size:0.82rem; color:#6c757d; }
</style>
""", unsafe_allow_html=True)

# ── Storage ───────────────────────────────────────────────────────────────────
DATA_FILE   = "data/records.json"
CONFIG_FILE = "data/config.json"
os.makedirs("data", exist_ok=True)

def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def iso(d): return d.isoformat()

def weekdays_in(start, end):
    days, cur = [], start
    while cur <= end:
        if cur.weekday() < 5: days.append(cur)
        cur += timedelta(days=1)
    return days

# ── Default config ─────────────────────────────────────────────────────────────
DEFAULT_CONFIG = {
    "students": [
        "ลีโอ","หยูอี้","ลิลี่","ชัดชา","มาดี","โมญ่า","จินนี่","เคท","มิก","หนูดี",
        "ชีวา","อิ๋ง","วิน","มีนา","จิ๊กซอ","ฟ้า","นิต้า","ภูมิ","พีท","พอต",
        "ของขวัญ","อาโป","ฟอร์จูน","รอบบิ้น","แบงค์","กาย","เคเค","ทอย","แตม","ตรัยคุณ"
    ],
    "missing_items": ["เข็มขัด","บัตร","เข็ม","ถุงเท้า","รองเท้า","เล็บยาว","โบว์","เนคไท","สูท","อื่นๆ"]
}

THAI_DAYS = {0:"จันทร์",1:"อังคาร",2:"พุธ",3:"พฤหัสบดี",4:"ศุกร์",5:"เสาร์",6:"อาทิตย์"}
STATUS_OPTS = ["มาปกติ","มาสาย","ขาดเรียน","ลาป่วย"]
STATUS_EN   = {"มาปกติ":"present","มาสาย":"late","ขาดเรียน":"absent","ลาป่วย":"sick"}
STATUS_COLOR= {"มาปกติ":"#d4edda","มาสาย":"#fff3cd","ขาดเรียน":"#f8d7da","ลาป่วย":"#d1ecf1"}
STATUS_TEXT = {"มาปกติ":"#155724","มาสาย":"#856404","ขาดเรียน":"#721c24","ลาป่วย":"#0c5460"}

config  = load_json(CONFIG_FILE, DEFAULT_CONFIG)
records = load_json(DATA_FILE,   {})

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 📋 เช็คชุดนักเรียน")
today = date.today()
th_day = THAI_DAYS[today.weekday()]
st.sidebar.caption(f"วันนี้: **วัน{th_day} {today.strftime('%d/%m/%Y')}**")
st.sidebar.markdown("---")

page = st.sidebar.radio("เมนู", [
    "📅 เช็คชุดรายวัน",
    "📊 สรุปรายวัน",
    "📈 สรุปรายสัปดาห์",
    "📆 สรุปรายเดือน",
    "⚙️ ตั้งค่า",
], label_visibility="collapsed")

students      = config["students"]
missing_items = config["missing_items"]

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — DAILY CHECK-IN
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📅 เช็คชุดรายวัน":
    st.title("📅 เช็คชุดรายวัน")

    if not students:
        st.warning("ยังไม่มีรายชื่อนักเรียน กรุณาไปที่ ⚙️ ตั้งค่า")
        st.stop()

    sel_date = st.date_input("เลือกวันที่", value=today)
    if sel_date.weekday() >= 5:
        st.info("⚠️ วันเสาร์-อาทิตย์ ไม่มีการเช็คชุด")
        st.stop()

    dk       = iso(sel_date)
    day_data = records.get(dk, {})
    updated  = {}

    st.markdown(f"### วัน{THAI_DAYS[sel_date.weekday()]} {sel_date.strftime('%d/%m/%Y')}")
    st.markdown("---")

    for idx, student in enumerate(students):
        prev = day_data.get(student, {})
        num  = f"{idx+1:02d}"

        with st.container():
            c1, c2, c3, c4 = st.columns([0.4, 1.8, 1.5, 3.3])

            # Number
            c1.markdown(f"<div style='padding-top:8px;color:#6c757d;font-size:0.85rem'>{num}</div>",
                        unsafe_allow_html=True)

            # Name
            c2.markdown(f"<div style='padding-top:8px;font-weight:600'>{student}</div>",
                        unsafe_allow_html=True)

            # Status
            prev_status = prev.get("status", "มาปกติ")
            status = c3.selectbox(
                "สถานะ", STATUS_OPTS,
                index=STATUS_OPTS.index(prev_status),
                key=f"{dk}_{student}_status",
                label_visibility="collapsed",
            )

            # Uniform + missing items (only if present or late)
            if status in ("มาปกติ", "มาสาย"):
                uniform_ok = prev.get("uniform_ok", True)
                missing    = prev.get("missing", [])

                u1, u2 = c4.columns([1.2, 2.8])
                uniform_ok = u1.radio(
                    "ชุด",
                    ["เครื่องแต่งกายครบ", "เครื่องแต่งกายไม่ครบ", "ไม่มาตรวจระเบียบ],
                    index=0 if uniform_ok else 1,
                    key=f"{dk}_{student}_uniform",
                    label_visibility="collapsed",
                    horizontal=False,
                )
                uniform_ok = (uniform_ok == "เครื่องแต่งกายครบ")

                if not uniform_ok:
                    selected_missing = u2.multiselect(
                        "สิ่งที่ขาด/ผิด",
                        missing_items,
                        default=[m for m in missing if m in missing_items],
                        key=f"{dk}_{student}_missing",
                        label_visibility="collapsed",
                        placeholder="เลือกสิ่งที่ขาด/ผิด...",
                    )
                else:
                    selected_missing = []
                    u2.markdown("")
            else:
                uniform_ok       = False
                selected_missing = []
                c4.markdown("<div style='padding-top:8px;color:#aaa'>—</div>", unsafe_allow_html=True)

            updated[student] = {
                "status":     status,
                "uniform_ok": uniform_ok,
                "missing":    selected_missing,
            }

        st.markdown("<hr style='margin:4px 0;border-color:#f0f0f0'>", unsafe_allow_html=True)

    st.markdown("")
    if st.button("💾 บันทึกการเช็คชุดวันนี้", type="primary", use_container_width=True):
        records[dk] = updated
        save_json(DATA_FILE, records)
        st.success(f"✅ บันทึกสำเร็จ! วัน{THAI_DAYS[sel_date.weekday()]} {sel_date.strftime('%d/%m/%Y')}")
        st.balloons()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — DAILY SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 สรุปรายวัน":
    st.title("📊 สรุปรายวัน")

    sel_date = st.date_input("เลือกวันที่", value=today)
    dk       = iso(sel_date)
    day_data = records.get(dk, {})

    if not day_data:
        st.info("ยังไม่มีข้อมูลสำหรับวันนี้")
        st.stop()

    # Counts
    total   = len(students)
    present = sum(1 for s in students if day_data.get(s,{}).get("status") == "มาปกติ")
    late    = sum(1 for s in students if day_data.get(s,{}).get("status") == "มาสาย")
    absent  = sum(1 for s in students if day_data.get(s,{}).get("status") == "ขาดเรียน")
    sick    = sum(1 for s in students if day_data.get(s,{}).get("status") == "ลาป่วย")
    uniform_issues = sum(1 for s in students if not day_data.get(s,{}).get("uniform_ok", True)
                         and day_data.get(s,{}).get("status") in ("มาปกติ","มาสาย"))

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col, num, lbl, color in [
        (c1, total,          "ทั้งหมด",       "#6c757d"),
        (c2, present,        "มาปกติ",         "#28a745"),
        (c3, late,           "มาสาย",          "#ffc107"),
        (c4, absent,         "ขาดเรียน",       "#dc3545"),
        (c5, sick,           "ลาป่วย",          "#17a2b8"),
        (c6, uniform_issues, "ชุดไม่ครบ",      "#fd7e14"),
    ]:
        col.markdown(f"""
        <div class="metric-box">
          <div class="num" style="color:{color}">{num}</div>
          <div class="lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Table
    rows = []
    for s in students:
        d = day_data.get(s, {})
        rows.append({
            "ชื่อ": s,
            "สถานะ": d.get("status", "—"),
            "ชุดนักเรียน": "ครบ ✅" if d.get("uniform_ok") else ("ไม่ครบ ❌" if d.get("status") in ("มาปกติ","มาสาย") else "—"),
            "สิ่งที่ขาด": ", ".join(d.get("missing", [])) or "—",
        })

    df = pd.DataFrame(rows)

    def color_status(val):
        c = {"มาปกติ":"background:#d4edda","มาสาย":"background:#fff3cd",
              "ขาดเรียน":"background:#f8d7da","ลาป่วย":"background:#d1ecf1"}
        return c.get(val, "")

    st.dataframe(
        df.style.applymap(color_status, subset=["สถานะ"]),
        use_container_width=True, hide_index=True, height=700,
    )

    # Missing items breakdown
    all_missing = []
    for s in students:
        all_missing += day_data.get(s,{}).get("missing", [])
    if all_missing:
        st.markdown("---")
        st.subheader("สิ่งที่ขาดบ่อยที่สุดวันนี้")
        miss_df = pd.Series(all_missing).value_counts().reset_index()
        miss_df.columns = ["รายการ","จำนวน"]
        st.bar_chart(miss_df.set_index("รายการ"))

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ ดาวน์โหลด CSV", csv, f"daily_{dk}.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 — WEEKLY SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📈 สรุปรายสัปดาห์":
    st.title("📈 สรุปรายสัปดาห์")

    mon = today - timedelta(days=today.weekday())
    week_start = st.date_input("เริ่มต้นสัปดาห์ (วันจันทร์)", value=mon)
    week_end   = week_start + timedelta(days=4)
    st.caption(f"สัปดาห์: {week_start.strftime('%d/%m/%Y')} → {week_end.strftime('%d/%m/%Y')}")

    days = weekdays_in(week_start, week_end)

    # Attendance table
    st.subheader("ตารางการมาเรียน")
    rows = []
    for s in students:
        row = {"ชื่อ": s}
        for d in days:
            val = records.get(iso(d), {}).get(s, {}).get("status", "—")
            row[f"วัน{THAI_DAYS[d.weekday()]} {d.strftime('%d/%m')}"] = val
        rows.append(row)

    df = pd.DataFrame(rows)

    def color_status(val):
        c = {"มาปกติ":"background:#d4edda","มาสาย":"background:#fff3cd",
              "ขาดเรียน":"background:#f8d7da","ลาป่วย":"background:#d1ecf1"}
        return c.get(val, "")

    day_cols = [c for c in df.columns if c != "ชื่อ"]
    st.dataframe(
        df.style.applymap(color_status, subset=day_cols),
        use_container_width=True, hide_index=True, height=650,
    )

    # Count summary
    st.markdown("---")
    st.subheader("สรุปการมาเรียนรายคน")
    count_rows = []
    for s in students:
        c = {"ชื่อ": s, "มาปกติ":0,"มาสาย":0,"ขาดเรียน":0,"ลาป่วย":0,"ชุดไม่ครบ":0}
        for d in days:
            dd = records.get(iso(d), {}).get(s, {})
            st_ = dd.get("status","—")
            if st_ in c: c[st_] += 1
            if not dd.get("uniform_ok", True) and st_ in ("มาปกติ","มาสาย"):
                c["ชุดไม่ครบ"] += 1
        count_rows.append(c)

    cdf = pd.DataFrame(count_rows)
    st.dataframe(cdf, use_container_width=True, hide_index=True)

    csv = cdf.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ ดาวน์โหลด CSV", csv,
                       f"weekly_{week_start}.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 4 — MONTHLY SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📆 สรุปรายเดือน":
    st.title("📆 สรุปรายเดือน")

    THAI_MONTHS = ["มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","มิถุนายน",
                   "กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]

    col1, col2 = st.columns(2)
    month = col1.selectbox("เดือน", list(range(1,13)),
                           index=today.month-1,
                           format_func=lambda m: THAI_MONTHS[m-1])
    year  = col2.number_input("ปี (ค.ศ.)", min_value=2020, max_value=2099, value=today.year)

    first_day = date(year, month, 1)
    last_day  = date(year, month, calendar.monthrange(year, month)[1])
    days      = weekdays_in(first_day, last_day)
    st.caption(f"**{THAI_MONTHS[month-1]} {year}** — {len(days)} วันเรียน")

    rows = []
    for s in students:
        c = {"ชื่อ": s, "วันเรียนทั้งหมด": len(days),
             "มาปกติ":0,"มาสาย":0,"ขาดเรียน":0,"ลาป่วย":0,"ชุดไม่ครบ":0,"รายการที่ขาดบ่อย":""}
        item_counts = {}
        for d in days:
            dd = records.get(iso(d), {}).get(s, {})
            st_ = dd.get("status","—")
            if st_ in c: c[st_] += 1
            if not dd.get("uniform_ok", True) and st_ in ("มาปกติ","มาสาย"):
                c["ชุดไม่ครบ"] += 1
                for item in dd.get("missing", []):
                    item_counts[item] = item_counts.get(item, 0) + 1
        if item_counts:
            top = sorted(item_counts, key=item_counts.get, reverse=True)[:3]
            c["รายการที่ขาดบ่อย"] = ", ".join(top)
        rows.append(c)

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True, height=650)

    # Leaderboards
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🔴 ขาดเรียนมากสุด")
        top_absent = df[["ชื่อ","ขาดเรียน"]].sort_values("ขาดเรียน",ascending=False).head(5)
        st.dataframe(top_absent, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("🟡 มาสายมากสุด")
        top_late = df[["ชื่อ","มาสาย"]].sort_values("มาสาย",ascending=False).head(5)
        st.dataframe(top_late, hide_index=True, use_container_width=True)

    with col3:
        st.subheader("⚠️ ชุดไม่ครบมากสุด")
        top_uni = df[["ชื่อ","ชุดไม่ครบ"]].sort_values("ชุดไม่ครบ",ascending=False).head(5)
        st.dataframe(top_uni, hide_index=True, use_container_width=True)

    # Missing item totals for month
    st.markdown("---")
    st.subheader("สิ่งที่ขาดสะสมทั้งเดือน")
    all_missing = []
    for d in days:
        for s in students:
            all_missing += records.get(iso(d), {}).get(s, {}).get("missing", [])
    if all_missing:
        miss_df = pd.Series(all_missing).value_counts().reset_index()
        miss_df.columns = ["รายการ","จำนวนครั้ง"]
        st.bar_chart(miss_df.set_index("รายการ"))
    else:
        st.info("ไม่มีข้อมูลชุดไม่ครบในเดือนนี้")

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ ดาวน์โหลด CSV", csv,
                       f"monthly_{year}_{month:02}.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE 5 — SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ ตั้งค่า":
    st.title("⚙️ ตั้งค่า")

    st.subheader("👥 รายชื่อนักเรียน")
    st.caption("ใส่ชื่อหนึ่งคนต่อบรรทัด")
    students_text = st.text_area(
        "รายชื่อ", value="\n".join(config["students"]),
        height=350, label_visibility="collapsed",
    )

    st.markdown("---")
    st.subheader("👔 รายการชุดที่ขาด/ผิด")
    st.caption("ใส่รายการหนึ่งรายการต่อบรรทัด")
    items_text = st.text_area(
        "รายการ", value="\n".join(config["missing_items"]),
        height=220, label_visibility="collapsed",
    )

    st.markdown("---")
    if st.button("💾 บันทึกการตั้งค่า", type="primary", use_container_width=True):
        new_students = [s.strip() for s in students_text.splitlines() if s.strip()]
        new_items    = [i.strip() for i in items_text.splitlines() if i.strip()]
        config["students"]      = new_students
        config["missing_items"] = new_items
        save_json(CONFIG_FILE, config)
        st.success(f"✅ บันทึกสำเร็จ! {len(new_students)} คน, {len(new_items)} รายการ")
        st.rerun()

    st.markdown("---")
    with st.expander("🗑️ ลบข้อมูลทั้งหมด"):
        st.warning("การลบนี้ไม่สามารถยกเลิกได้")
        if st.button("ลบข้อมูลการเช็คชุดทั้งหมด", type="secondary"):
            save_json(DATA_FILE, {})
            st.error("ลบข้อมูลทั้งหมดแล้ว")
