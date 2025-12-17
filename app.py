import time
import streamlit as st
import pandas as pd
import numpy as np

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Dashboard BKKBN Provinsi Jawa Timur",
    page_icon="📊",
    layout="wide"
)

# =========================
# AUTH (DEMO)
# =========================
USERS = {"mahasiswa": "upnvjt"}  # ubah jika perlu

if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "Beranda"

# =========================
# THEME (CONSISTENT PALETTE)
# Referensi gaya: Tailwind/shadcn (slate + blue/sky) + kontras teks (Apple/Material)
# =========================
CSS = """
<style>
:root{
  /* Surfaces */
  --bg: #F7FAFF;          /* soft */
  --bg2:#EAF3FF;          /* soft */
  --card:#FFFFFF;         /* surface */
  --border:#E2E8F0;       /* slate-200 */

  /* Typography */
  --text:#0F172A;         /* slate-900 */
  --muted:#334155;        /* slate-700 */
  --subtle:#64748B;       /* slate-500 */

  /* Brand */
  --primary:#2563EB;      /* blue-600 */
  --primary2:#1D4ED8;     /* blue-700 */
  --accent:#38BDF8;       /* sky-400 */

  /* Sidebar */
  --side:#FFFFFFF2;
  --sideBtn:#F8FAFC;      /* slate-50 */
  --sideBtnHover:#EFF6FF; /* blue-50 */

  /* Shadows */
  --shadow: 0 14px 34px rgba(15,23,42,.08);
  --shadow2: 0 10px 24px rgba(15,23,42,.06);
}

/* App background */
[data-testid="stAppViewContainer"]{
  background: linear-gradient(135deg, var(--bg) 0%, var(--bg2) 100%);
}

/* Global typography */
html, body, [class*="css"]{
  color: var(--text) !important;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Inter, Arial;
}
h1,h2,h3,h4{
  color: var(--text) !important;
  letter-spacing: -0.2px;
}
p, span, label, small{
  color: var(--muted) !important;
}

/* Reduce top padding a bit */
.block-container{ padding-top: 1.0rem; }

/* Sidebar glass */
section[data-testid="stSidebar"]{
  background: var(--side);
  border-right: 1px solid var(--border);
  backdrop-filter: blur(10px);
}

/* Buttons - unify all Streamlit buttons */
.stButton > button{
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
  background: var(--primary) !important;
  color: #FFFFFF !important;
  padding: 10px 14px !important;
  box-shadow: var(--shadow2);
  transition: transform .12s ease, box-shadow .12s ease, background .12s ease;
}
.stButton > button:hover{
  background: var(--primary2) !important;
  transform: translateY(-1px);
  box-shadow: 0 18px 40px rgba(37,99,235,.18);
}

/* Sidebar nav buttons look lighter (override only sidebar area) */
section[data-testid="stSidebar"] .stButton > button{
  background: var(--sideBtn) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  box-shadow: 0 8px 18px rgba(15,23,42,.05);
}
section[data-testid="stSidebar"] .stButton > button:hover{
  background: var(--sideBtnHover) !important;
  border-color: #BFDBFE !important;
}

/* Active nav style (we apply via HTML badge) */
.active-pill{
  display:inline-block;
  padding:6px 10px;
  border-radius:999px;
  background: rgba(37,99,235,.12);
  border: 1px solid rgba(37,99,235,.22);
  color: #0B3B9E;
  font-size: 12px;
  font-weight: 800;
}

/* Cards */
.ds-card{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 22px;
  padding: 16px 18px;
  box-shadow: var(--shadow);
  margin-bottom: 14px;
}

/* Header card (wrap header nicely) */
.header-wrap{
  background: rgba(255,255,255,.75);
  border: 1px solid var(--border);
  border-radius: 26px;
  padding: 16px 18px;
  box-shadow: var(--shadow2);
}

/* Badges */
.badge{
  display:inline-block;
  padding: 7px 12px;
  border-radius: 999px;
  background: rgba(56,189,248,.14);
  border: 1px solid rgba(37,99,235,.20);
  color: #0B4AA2 !important;
  font-size: 12px;
  font-weight: 800;
}

/* Inputs (login) */
div[data-testid="stTextInput"] input{
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
  background: #FFFFFF !important;
  color: var(--text) !important;
}
div[data-testid="stTextInput"] input::placeholder{
  color: var(--subtle) !important;
}
div[data-testid="stTextInput"] input:focus{
  border-color: #93C5FD !important;
  box-shadow: 0 0 0 4px rgba(147,197,253,.35) !important;
}

/* KPI */
.kpi{display:flex;gap:12px;flex-wrap:wrap}
.kpi .box{
  flex:1; min-width: 190px;
  border-radius: 18px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #38BDF8 0%, #6366F1 100%);
  box-shadow: 0 18px 40px rgba(99,102,241,.18);
  transition: transform .14s ease, box-shadow .14s ease;
}
.kpi .box:hover{
  transform: translateY(-3px);
  box-shadow: 0 24px 54px rgba(99,102,241,.22);
}
.kpi .box *{ color:#FFFFFF !important; }
.small{font-size:13px;opacity:.9}
.big{font-size:22px;font-weight:900}

/* Charts in card style */
[data-testid="stChart"], [data-testid="stPlotlyChart"], [data-testid="stVegaLiteChart"]{
  background: #FFFFFF;
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 10px;
  box-shadow: var(--shadow2);
}

/* Smooth transition */
.page{ animation: fadeSlide .42s ease-in-out; }
@keyframes fadeSlide{
  from { opacity:0; transform: translateY(10px); }
  to   { opacity:1; transform: translateY(0); }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# =========================
# HELPERS
# =========================
def soft_loading(label="Memuat…", ms=180):
    with st.spinner(label):
        time.sleep(ms / 1000)

def set_page(p):
    st.session_state.page = p
    st.rerun()

def header_centered():
    # LOGO DI TENGAH (bukan kiri/kanan)
    st.markdown('<div class="header-wrap">', unsafe_allow_html=True)

    # Row logos (centered)
    lc1, lc2, lc3 = st.columns([3, 2, 3], vertical_alignment="center")
    with lc2:
        # dua logo berdampingan, sama-sama di tengah
        l1, l2 = st.columns(2)
        with l1:
            st.image("logo_upn.png", width=74)
        with l2:
            st.image("logo_bkkbn.png", width=74)

    # Title + badges (centered)
    st.markdown(
        """
        <div style="text-align:center; margin-top:8px;">
          <h2 style="margin:0; color: var(--text);">Dashboard BKKBN Provinsi Jawa Timur</h2>
          <div style="margin-top:10px;">
            <span class="badge">Perwakilan BKKBN Jawa Timur</span>
            <span class="badge" style="margin-left:6px;">People Analytics • Time Series • Policy</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)
    st.write("")  # spacing kecil

# =========================
# PAGES
# =========================
def login_page():
    st.markdown('<div class="page">', unsafe_allow_html=True)
    header_centered()

    # form login di card
    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
    st.subheader("🔐 Login")

    u = st.text_input("Username", placeholder="contoh: mahasiswa")
    p = st.text_input("Password", type="password", placeholder="contoh: upnvjt")

    if st.button("Login", use_container_width=True):
        if u in USERS and USERS[u] == p:
            st.session_state.auth = True
            st.session_state.user = u
            soft_loading("Menyiapkan dashboard…", 220)
            st.rerun()
        else:
            st.error("Username / password salah.")

    st.caption("Mode demo kuliah: autentikasi sederhana (tanpa database).")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def page_home():
    st.markdown('<div class="page">', unsafe_allow_html=True)
    header_centered()

    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
    st.write(f"Halo **{st.session_state.user}** 👋")
    st.write("Gunakan menu kiri untuk membuka 2 halaman project:")
    st.write("1) **People Analytics – Analisis Media Sosial**")
    st.write("2) **Time Series – Statistika Sains Data & Analisis Kebijakan**")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
    st.subheader("Tujuan")
    st.write("- Menyajikan ringkasan KPI dan tren untuk dukungan insight berbasis data.")
    st.write("- Prototipe deployment (dummy saat preview; data final tinggal plug-in).")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def page_people():
    st.markdown('<div class="page">', unsafe_allow_html=True)
    header_centered()

    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
    st.subheader("🧠 People Analytics – Analisis Media Sosial")
    st.write("Dummy preview: KPI + tren engagement + insight ringkas.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="kpi">
          <div class="box"><div class="small">Total Post</div><div class="big">12,340</div></div>
          <div class="box"><div class="small">Engagement Rate</div><div class="big">4.8%</div></div>
          <div class="box"><div class="small">Sentimen Positif</div><div class="big">62%</div></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    soft_loading("Memuat grafik…", 180)
    df = pd.DataFrame({"hari": range(1, 15), "engagement": np.random.randint(120, 520, 14)}).set_index("hari")
    st.line_chart(df)

    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
    st.subheader("Insight (contoh)")
    st.write("- Ada lonjakan engagement pada periode tertentu → indikasi isu/event.")
    st.write("- Final: tambah top keyword/topik dominan + distribusi sentimen.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def page_timeseries():
    st.markdown('<div class="page">', unsafe_allow_html=True)
    header_centered()

    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
    st.subheader("⏳ Time Series – Analisis Kebijakan")
    st.write("Dummy preview: deret waktu + narasi forecast & evaluasi.")
    st.markdown("</div>", unsafe_allow_html=True)

    soft_loading("Memuat grafik…", 180)
    t = pd.date_range("2024-01-01", periods=120, freq="D")
    y = np.cumsum(np.random.randn(120)) + 50
    ts = pd.DataFrame({"date": t, "value": y}).set_index("date")
    st.line_chart(ts)

    st.markdown('<div class="ds-card">', unsafe_allow_html=True)
    st.subheader("Forecast & Evaluasi (contoh)")
    st.write("- Model: ARIMA / ETS / Prophet (pilih salah satu).")
    st.write("- Metrik: MAE, RMSE, MAPE.")
    st.write("- Kebijakan: bandingkan sebelum–sesudah tanggal intervensi.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# APP ROUTER
# =========================
def app():
    if not st.session_state.auth:
        login_page()
        return

    with st.sidebar:
        st.markdown("## 🚀 Navigasi")
        st.markdown(
            f'<span class="active-pill">Aktif: {st.session_state.page}</span>',
            unsafe_allow_html=True
        )
        st.write("")

        if st.button("🏠 Beranda", use_container_width=True):
            set_page("Beranda")
        if st.button("🧠 People Analytics", use_container_width=True):
            set_page("People Analytics")
        if st.button("⏳ Time Series & Kebijakan", use_container_width=True):
            set_page("Time Series & Kebijakan")

        st.divider()
        st.write(f"Login: **{st.session_state.user}**")
        if st.button("Logout", use_container_width=True):
            st.session_state.auth = False
            st.session_state.user = None
            st.session_state.page = "Beranda"
            st.rerun()

    if st.session_state.page == "Beranda":
        page_home()
    elif st.session_state.page == "People Analytics":
        page_people()
    else:
        page_timeseries()

app()
