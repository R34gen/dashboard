import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="Dashboard Analitik Media Sosial",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# AUTH
# =====================================================
USERS = {"mahasiswa": "upnvjt"}
if "login" not in st.session_state:
    st.session_state.login = False

# =====================================================
# DATA LOADER
# =====================================================
DATA = Path("data")

@st.cache_data
def load(name):
    return pd.read_csv(DATA / name)

# =====================================================
# GLOBAL STYLE (EXPERT UI)
# =====================================================
st.markdown("""
<style>
:root{
  --bg:#F8FAFC;
  --card:#FFFFFF;
  --border:#E5E7EB;
  --text:#0F172A;
  --muted:#475569;
  --primary:#1E3A8A;
  --primary-soft:#EFF6FF;
}
[data-testid="stAppViewContainer"]{
  background:var(--bg);
}
*{font-family:Inter,system-ui,sans-serif;}
.card{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:20px;
  padding:22px;
  margin-bottom:18px;
  animation:fadeUp .4s ease;
}
@keyframes fadeUp{
  from{opacity:0;transform:translateY(10px)}
  to{opacity:1;transform:translateY(0)}
}
.center{text-align:center;}
.kpi{
  background:linear-gradient(135deg,#2563EB,#1E3A8A);
  color:white;
  border-radius:18px;
  padding:20px;
}
.kpi *{color:white;}
.section-title{
  font-size:20px;
  font-weight:700;
  margin-bottom:6px;
}
.caption{
  font-size:13px;
  color:var(--muted);
}
.highlight{
  background:var(--primary-soft);
  border-left:4px solid var(--primary);
  padding:14px 16px;
  border-radius:12px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# LOGIN PAGE
# =====================================================
def login_page():
    st.markdown("<div class='card center'>", unsafe_allow_html=True)

    col = st.columns([1,2,1])[1]
    with col:
        st.image("logo_upn.png", width=80)
        st.image("logo_bkkbn.png", width=80)
        st.markdown("## **People Analytics Dashboard**")
        st.caption("BKKBN Provinsi Jawa Timur • Deployment Aplikasi")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        if USERS.get(u) == p:
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Username atau password salah")

    st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# MAIN DASHBOARD
# =====================================================
def dashboard():
    # Load data
    summary = load("people_analytics_summary.csv")
    rating = load("distribusi_rating.csv")
    sentiment = load("distribusi_sentimen.csv")
    top_pos = load("ringkasan_topik_positif.csv")
    top_neg = load("ringkasan_topik_negatif.csv")
    keluhan = load("rating_4keatas_tapi_keluhan.csv")

    # HEADER
    st.markdown("<div class='card center'>", unsafe_allow_html=True)
    st.image("logo_upn.png", width=70)
    st.image("logo_bkkbn.png", width=70)
    st.markdown("## **People Analytics Dashboard**")
    st.caption("Analisis Media Sosial • BKKBN Provinsi Jawa Timur")
    st.markdown("</div>", unsafe_allow_html=True)

    # KPI
    k1,k2,k3 = st.columns(3)
    with k1:
        st.markdown("<div class='kpi'>", unsafe_allow_html=True)
        st.markdown("### Total Data")
        st.markdown(f"## {int(summary['total_data'][0]):,}")
        st.markdown("</div>", unsafe_allow_html=True)
    with k2:
        st.markdown("<div class='kpi'>", unsafe_allow_html=True)
        st.markdown("### Rata-rata Rating")
        st.markdown(f"## {summary['avg_rating'][0]:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    with k3:
        st.markdown("<div class='kpi'>", unsafe_allow_html=True)
        st.markdown("### Sentimen Positif")
        st.markdown(f"## {summary['sentimen_positif'][0]:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)

    # DISTRIBUTION
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Distribusi Rating & Sentimen</div>", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        fig = px.bar(rating, x="rating", y="jumlah",
                     color_discrete_sequence=["#1E3A8A"])
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.pie(sentiment, names="sentimen", values="jumlah",
                     color_discrete_sequence=["#1E3A8A","#60A5FA","#CBD5E1"])
        fig.update_layout(height=360)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # TOPICS
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Topik Dominan</div>", unsafe_allow_html=True)

    t1,t2 = st.columns(2)
    with t1:
        fig = px.bar(top_pos.head(8), x="jumlah", y="topik",
                     orientation="h",
                     color_discrete_sequence=["#2563EB"])
        st.plotly_chart(fig, use_container_width=True)
    with t2:
        fig = px.bar(top_neg.head(8), x="jumlah", y="topik",
                     orientation="h",
                     color_discrete_sequence=["#64748B"])
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # INSIGHT
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Insight Utama</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='highlight'>
    <b>1.</b> Terdapat <b>rating tinggi namun tetap mengandung keluhan</b>, menandakan kepuasan parsial.<br>
    <b>2.</b> Topik negatif berulang → prioritas peningkatan kualitas layanan.<br>
    <b>3.</b> Sentimen positif dominan → persepsi publik relatif baik namun perlu konsistensi.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Lihat contoh rating tinggi tapi masih ada keluhan"):
        st.dataframe(keluhan.head(10), use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.caption("© 2025 • People Analytics • Streamlit Cloud Deployment")

# =====================================================
# ROUTER
# =====================================================
if not st.session_state.login:
    login_page()
else:
    dashboard()
