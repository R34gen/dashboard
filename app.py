import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Dashboard TES", page_icon="📊", layout="wide")

# =========================
# AUTH (DEMO)
# =========================
USERS = {"mahasiswa": "upnvjt"}
if "login" not in st.session_state:
    st.session_state.login = False

# =========================
# FILES
# =========================
DATA = Path("data")

def pick_file(*names: str) -> Path:
    for n in names:
        p = DATA / n
        if p.exists():
            return p
    st.error("File tidak ditemukan di folder `data/`.")
    st.write("Dicari:", list(names))
    st.stop()

@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def safe_col(df: pd.DataFrame, *names: str):
    for n in names:
        if n in df.columns:
            return n
    return None

# Overview
p_rating     = pick_file("distribusi_rating.csv")
p_sentiment  = pick_file("distribusi_sentimen.csv", "distribusi_sentimen (1).csv")

# Topic modeling
p_top_neg    = pick_file("ringkasan_topik_negatif.csv")
p_top_neg_f  = pick_file("hasil_topic_negatif_full.csv")
p_top_pos    = pick_file("ringkasan_topik_positif.csv")
p_top_pos_f  = pick_file("hasil_topic_positif_full.csv")

# People analytics
p_people_sum = pick_file("people_analytics_summary.csv")
p_keluhan4   = pick_file("rating_4keatas_tapi_keluhan.csv", "rating_4keatas_tapi_keluhan (1).csv")
p_rating2    = pick_file("rating_2kebawah_semua_ulasan.csv")

rating_df    = load_csv(p_rating)
sent_df      = load_csv(p_sentiment)
top_neg      = load_csv(p_top_neg)
top_neg_full = load_csv(p_top_neg_f)
top_pos      = load_csv(p_top_pos)
top_pos_full = load_csv(p_top_pos_f)
people_sum   = load_csv(p_people_sum)
keluhan4_df  = load_csv(p_keluhan4)
rating2_df   = load_csv(p_rating2)

# =========================
# KPI (dark text, calm colors)
# =========================
col_r_rate  = safe_col(rating_df, "rating", "score")
col_r_count = safe_col(rating_df, "jumlah_ulasan", "jumlah", "count")
total_data = int(rating_df[col_r_count].sum()) if col_r_count else int(len(rating_df))
avg_rating = float((rating_df[col_r_rate] * rating_df[col_r_count]).sum() / max(total_data, 1)) if (col_r_rate and col_r_count) else np.nan

col_s_name  = safe_col(sent_df, "sentimen", "sentiment")
col_s_pct   = safe_col(sent_df, "persentase", "pct", "percentage")
col_s_count = safe_col(sent_df, "jumlah_ulasan", "jumlah", "count")

def get_sent_pct(name: str) -> float:
    if not col_s_name:
        return np.nan
    row = sent_df[sent_df[col_s_name].astype(str).str.lower() == name.lower()]
    if row.empty:
        return 0.0
    if col_s_pct:
        return float(row[col_s_pct].iloc[0])
    if col_s_count:
        return float(row[col_s_count].iloc[0] / max(total_data, 1) * 100)
    return np.nan

pct_positif = get_sent_pct("positif")
pct_negatif = get_sent_pct("negatif")
pct_netral  = get_sent_pct("netral")

# =========================
# PLOTLY STYLE (consistent)
# =========================
PX_TEMPLATE = "simple_white"
AXIS = dict(showgrid=True, gridcolor="rgba(15,23,42,0.08)", zeroline=False)

# =========================
# UI / UX THEME (FIXED)
# =========================
st.markdown("""
<style>
:root{
  --bg: #F5F7FB;         /* soft gray-blue */
  --surface: #FFFFFF;    /* cards */
  --border: rgba(15,23,42,0.10);
  --shadow: 0 10px 30px rgba(15,23,42,0.06);

  --text: #0F172A;       /* slate-900 */
  --muted: #334155;      /* slate-700 */
  --subtle: #64748B;     /* slate-500 */

  --brand: #1E3A8A;      /* navy */
  --brand2: #2563EB;     /* blue */
  --soft: rgba(37,99,235,0.08);
}

[data-testid="stAppViewContainer"]{
  background: var(--bg);
}

/* DO NOT override all text to bright! Keep dark. */
html, body, [class*="css"]{
  color: var(--text) !important;
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial;
}

/* Headings */
h1,h2,h3{ color: var(--text) !important; letter-spacing: -0.3px; }
p,span,label,small,div{ color: var(--muted); }

/* Cards */
.card{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 22px;
  padding: 18px 18px;
  box-shadow: var(--shadow);
  margin-bottom: 14px;
}
.card-title{
  font-size: 18px;
  font-weight: 900;
  color: var(--text) !important;
  margin: 0 0 4px 0;
}
.card-sub{
  font-size: 13px;
  color: var(--subtle) !important;
  margin: 0;
}

/* Center header */
.center{ text-align: center; }
.badges{ display:flex; justify-content:center; flex-wrap:wrap; gap:8px; margin-top:10px; }
.badge{
  font-size: 12px;
  font-weight: 800;
  padding: 7px 12px;
  border-radius: 999px;
  background: var(--soft);
  border: 1px solid rgba(30,58,138,0.18);
  color: var(--brand) !important;
}

/* KPI cards (not too bright) */
.kpi-grid{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}
.kpi{
  border-radius: 18px;
  padding: 16px;
  border: 1px solid rgba(15,23,42,0.10);
  background: linear-gradient(135deg, rgba(30,58,138,0.98), rgba(37,99,235,0.92));
  position: relative;
  overflow: hidden;
}
.kpi:before{
  content:"";
  position:absolute;
  right:-60px; top:-60px;
  width:150px; height:150px;
  background: rgba(255,255,255,0.14);
  border-radius:999px;
}
.kpi .title{ font-size: 13px; font-weight: 900; color: rgba(255,255,255,0.92) !important; }
.kpi .value{ font-size: 26px; font-weight: 950; color: #FFFFFF !important; margin-top: 4px; }
.kpi .pill{
  display:inline-block;
  margin-top: 8px;
  font-size: 12px;
  font-weight: 800;
  padding: 4px 9px;
  border-radius: 999px;
  background: rgba(255,255,255,0.14);
  color: rgba(255,255,255,0.92) !important;
}

/* Buttons */
.stButton>button{
  border-radius: 14px !important;
  border: 1px solid rgba(15,23,42,0.10) !important;
  background: var(--brand) !important;
  color: #fff !important;
  padding: 10px 14px !important;
}
.stButton>button:hover{
  background: #162E6E !important;
}

/* Inputs */
div[data-testid="stTextInput"] input{
  border-radius: 14px !important;
  border: 1px solid rgba(15,23,42,0.12) !important;
  background: #fff !important;
  color: var(--text) !important;
}
div[data-testid="stTextInput"] input::placeholder{ color: var(--subtle) !important; }

/* Smooth transition */
.page{ animation: fadeUp .38s ease; }
@keyframes fadeUp{ from{opacity:0; transform: translateY(10px)} to{opacity:1; transform: translateY(0)} }

/* Mobile */
@media (max-width: 768px){
  .block-container{ padding: .8rem .8rem; }
  .kpi-grid{ grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

# =========================
# COMPONENTS
# =========================
def header_center(title: str, subtitle: str):
    st.markdown("<div class='card center page'>", unsafe_allow_html=True)
    st.image("logo_upn.png", width=74)
    st.image("logo_bkkbn.png", width=74)
    st.markdown(f"## {title}")
    st.markdown(f"<p class='card-sub'>{subtitle}</p>", unsafe_allow_html=True)
    st.markdown(
        "<div class='badges'>"
        "<span class='badge'>BKKBN Provinsi Jawa Timur</span>"
        "<span class='badge'>People Analytics</span>"
        "<span class='badge'>Topic Modeling</span>"
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

def login_page():
    header_center("People Analytics Dashboard", "Login untuk mengakses dashboard (demo kuliah)")
    st.markdown("<div class='card page'>", unsafe_allow_html=True)
    u = st.text_input("Username", placeholder="contoh: mahasiswa")
    p = st.text_input("Password", type="password", placeholder="contoh: upnvjt")
    if st.button("Login", use_container_width=True):
        if USERS.get(u) == p:
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Username atau password salah.")
    st.caption("Login demo. Untuk produksi: pakai Streamlit Secrets.")
    st.markdown("</div>", unsafe_allow_html=True)

def dashboard():
    header_center("People Analytics Dashboard", "Overview • Topic Modeling • People Analytics Evidence")

    st.markdown(
        f"""
        <div class="kpi-grid page">
          <div class="kpi">
            <div class="title">Total Ulasan</div>
            <div class="value">{total_data:,}</div>
            <div class="pill">distribusi_rating.csv</div>
          </div>
          <div class="kpi">
            <div class="title">Rata-rata Rating</div>
            <div class="value">{avg_rating:.2f}</div>
            <div class="pill">weighted average</div>
          </div>
          <div class="kpi">
            <div class="title">Sentimen Positif</div>
            <div class="value">{pct_positif:.2f}%</div>
            <div class="pill">Neg {pct_negatif:.2f}% • Net {pct_netral:.2f}%</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🧩 Topic Modeling", "🧑‍💼 People Analytics"])

    # ---------- OVERVIEW ----------
    with tab1:
        st.markdown("<div class='card page'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Distribusi Rating & Sentimen</div>", unsafe_allow_html=True)
        st.markdown("<p class='card-sub'>Ringkasan kuantitatif untuk cepat membaca kondisi.</p>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(rating_df, x=col_r_rate, y=col_r_count, text=col_r_count, template=PX_TEMPLATE)
            fig.update_traces(textposition="outside")
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
            fig.update_xaxes(**AXIS)
            fig.update_yaxes(**AXIS)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            val_col = col_s_count if col_s_count else col_s_pct
            fig = px.pie(sent_df, names=col_s_name, values=val_col, hole=0.55, template=PX_TEMPLATE)
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- TOPIC MODELING ----------
    with tab2:
        st.markdown("<div class='card page'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Topik Dominan</div>", unsafe_allow_html=True)
        st.markdown("<p class='card-sub'>Top-N topic positif & negatif (ringkasan) + detail evidence (full).</p>", unsafe_allow_html=True)

        pos_topic = safe_col(top_pos, "topic_label", "topik", "topic")
        pos_cnt   = safe_col(top_pos, "jumlah_ulasan", "jumlah", "count", "freq")
        neg_topic = safe_col(top_neg, "topic_label", "topik", "topic")
        neg_cnt   = safe_col(top_neg, "jumlah_ulasan", "jumlah", "count", "freq")

        topn = st.slider("Top-N topic", 5, 20, 10)

        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(top_pos.head(topn).sort_values(pos_cnt),
                         x=pos_cnt, y=pos_topic, orientation="h", template=PX_TEMPLATE)
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10))
            fig.update_xaxes(**AXIS); fig.update_yaxes(**AXIS)
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("Detail: hasil_topic_positif_full.csv"):
                st.dataframe(top_pos_full, use_container_width=True)

        with c2:
            fig = px.bar(top_neg.head(topn).sort_values(neg_cnt),
                         x=neg_cnt, y=neg_topic, orientation="h", template=PX_TEMPLATE)
            fig.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10))
            fig.update_xaxes(**AXIS); fig.update_yaxes(**AXIS)
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("Detail: hasil_topic_negatif_full.csv"):
                st.dataframe(top_neg_full, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- PEOPLE ANALYTICS ----------
    with tab3:
        st.markdown("<div class='card page'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>People Analytics</div>", unsafe_allow_html=True)
        st.markdown("<p class='card-sub'>Ringkasan perilaku + evidence ekstrem untuk rekomendasi aksi.</p>", unsafe_allow_html=True)

        st.markdown("<div class='card-sub'><b>Ringkasan:</b> people_analytics_summary.csv</div>", unsafe_allow_html=True)
        st.dataframe(people_sum, use_container_width=True)

        st.markdown("<hr style='border:none; border-top:1px solid rgba(15,23,42,0.10); margin:14px 0;'/>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Rating ≥ 4 tapi keluhan**")
            st.dataframe(keluhan4_df.head(30), use_container_width=True)
        with c2:
            st.markdown("**Rating ≤ 2 (semua ulasan)**")
            st.dataframe(rating2_df.head(30), use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.caption(f"© {datetime.now().year} • People Analytics • Data aktual (CSV) • UI/UX vFinal")

# =========================
# ROUTER
# =========================
if not st.session_state.login:
    login_page()
else:
    dashboard()
