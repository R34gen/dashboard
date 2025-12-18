import json
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Dashboard BKKBN Provinsi Jawa Timur",
    page_icon="📊",
    layout="wide",
)

# =========================
# AUTH (DEMO)
# =========================
USERS = {"mahasiswa": "upnvjt"}  # boleh ganti
if "auth" not in st.session_state:
    st.session_state.auth = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "Medsos & People Analytics"

# =========================
# PATHS
# =========================
DATA_DIR = Path("data")
PEOPLE_JSON = DATA_DIR / "dashboard_data.json"
MONTHLY_CSV = DATA_DIR / "data_clean_monthly.csv"
FORECAST_CSV = DATA_DIR / "forecast_kb_aktif_2025_skenario.csv"
METRICS_CSV = DATA_DIR / "model_summary_metrics.csv"

# =========================
# THEME (expert + mobile)
# =========================
CSS = """
<style>
:root{
  --bg1:#F7FAFF; --bg2:#EAF3FF; --card:#FFFFFF; --border:#E2E8F0;
  --text:#0F172A; --muted:#334155; --subtle:#64748B;
  --primary:#2563EB; --primary2:#1D4ED8;
  --shadow: 0 14px 34px rgba(15,23,42,.08);
  --shadow2: 0 10px 24px rgba(15,23,42,.06);
}
[data-testid="stAppViewContainer"]{
  background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 100%);
}
html, body, [class*="css"]{
  color: var(--text) !important;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Inter, Arial;
}
h1,h2,h3{ color: var(--text) !important; letter-spacing:-0.25px; }
p,span,label,small{ color: var(--muted) !important; }
.block-container{ padding-top: 1rem; }

section[data-testid="stSidebar"]{
  background: rgba(255,255,255,.92);
  border-right: 1px solid var(--border);
  backdrop-filter: blur(10px);
}

.card{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 22px;
  padding: 16px 18px;
  box-shadow: var(--shadow);
  margin-bottom: 14px;
}
.card-soft{
  background: rgba(255,255,255,.75);
  border: 1px solid var(--border);
  border-radius: 22px;
  padding: 16px 18px;
  box-shadow: var(--shadow2);
  margin-bottom: 14px;
}

.badges{ display:flex; gap:8px; justify-content:center; flex-wrap:wrap; }
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

.kpi-grid{
  display:grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap:12px;
  margin-bottom: 12px;
}
.kpi{
  border-radius: 18px;
  padding: 14px 16px;
  background: linear-gradient(135deg, #38BDF8 0%, #6366F1 100%);
  box-shadow: 0 18px 40px rgba(99,102,241,.18);
  position: relative;
  overflow: hidden;
}
.kpi:before{
  content:"";
  position:absolute; inset:-60px -60px auto auto;
  width:140px; height:140px;
  background: rgba(255,255,255,.20);
  border-radius: 999px;
}
.kpi *{ color:#FFFFFF !important; }
.kpi-top{ display:flex; justify-content:space-between; align-items:center; }
.kpi-title{ font-size:13px; opacity:.92; font-weight:800; }
.kpi-value{ font-size:24px; font-weight:950; margin-top:2px; }
.kpi-sub{ display:inline-block; margin-top:8px; font-size:12px; font-weight:800; padding:4px 8px; border-radius:999px; background: rgba(255,255,255,.18); }

.insight{
  border-radius: 18px;
  padding: 14px 16px;
  border: 1px dashed rgba(37,99,235,.28);
  background: rgba(37,99,235,.06);
}

.page{ animation: fadeSlide .42s ease-in-out; }
@keyframes fadeSlide{ from{opacity:0; transform: translateY(10px);} to{opacity:1; transform: translateY(0);} }

@media (max-width: 768px){
  .block-container{ padding: 0.8rem 0.8rem; }
  .card, .card-soft{ border-radius: 18px; padding: 14px 14px; }
  .kpi-grid{ grid-template-columns: 1fr; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# =========================
# LOADERS
# =========================
def must_exist(path: Path, label: str):
    if not path.exists():
        st.error(f"File `{path}` tidak ditemukan. Pastikan ada di folder `data/` pada GitHub (untuk {label}).")
        st.stop()

@st.cache_data(show_spinner=False)
def load_people(path: Path) -> dict:
    must_exist(path, "Medsos & People Analytics")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(show_spinner=False)
def load_csv(path: Path, label: str) -> pd.DataFrame:
    must_exist(path, label)
    return pd.read_csv(path)

def header_center():
    st.markdown('<div class="card-soft page">', unsafe_allow_html=True)
    a, b = st.columns([1, 1], vertical_alignment="center")
    with a:
        st.image("logo_upn.png", width=72)
    with b:
        st.image("logo_bkkbn.png", width=72)

    st.markdown("<h3 style='text-align:center; margin:6px 0 2px;'>Dashboard BKKBN Provinsi Jawa Timur</h3>", unsafe_allow_html=True)
    st.markdown(
        "<div class='badges'><span class='badge'>Perwakilan BKKBN Jawa Timur</span><span class='badge'>Deployment Dashboard • Mobile Friendly</span></div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

def footer():
    st.caption(f"Deployment • Data aktual (JSON/CSV) • Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# =========================
# AUTH
# =========================
def login_page():
    header_center()
    st.markdown('<div class="card page">', unsafe_allow_html=True)
    st.subheader("🔐 Login")
    u = st.text_input("Username", placeholder="contoh: mahasiswa")
    p = st.text_input("Password", type="password", placeholder="contoh: upnvjt")
    if st.button("Login", use_container_width=True):
        if u in USERS and USERS[u] == p:
            st.session_state.auth = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Username / password salah.")
    st.caption("Catatan: login ini untuk demo (kuliah). Untuk produksi gunakan secrets.")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# PAGES (per mata kuliah)
# =========================
def page_people():
    header_center()
    st.markdown("### 🧠 Analitik Medsos & People Analytics")
    st.caption("Sumber data: `dashboard_data.json` (ringkasan hasil analisis).")

    data = load_people(PEOPLE_JSON)
    ov = data.get("overview", {})
    topic = pd.DataFrame(data.get("topic_summary", []))
    ins = data.get("people_insight", {})

    pct = ov.get("sentimen_pct", {})
    total_reviews = int(ov.get("total_reviews", 0))
    avg_rating = float(ov.get("avg_rating", 0))

    # FILTER ringan (biar interaktif)
    top_n = st.slider("Tampilkan Top-N Topic", 2, max(2, len(topic)) if len(topic) else 4, 4)

    st.markdown(
        f"""
        <div class="kpi-grid">
          <div class="kpi">
            <div class="kpi-top"><div class="kpi-title">Total Reviews</div><div>📝</div></div>
            <div class="kpi-value">{total_reviews:,}</div>
            <div class="kpi-sub">Ringkasan JSON</div>
          </div>
          <div class="kpi">
            <div class="kpi-top"><div class="kpi-title">Avg Rating</div><div>⭐</div></div>
            <div class="kpi-value">{avg_rating:.2f}</div>
            <div class="kpi-sub">Skala 1–5</div>
          </div>
          <div class="kpi">
            <div class="kpi-top"><div class="kpi-title">Negatif (%)</div><div>⚠️</div></div>
            <div class="kpi-value">{float(pct.get("negatif", 0)):.2f}%</div>
            <div class="kpi-sub">Pos {float(pct.get("positif",0)):.2f}% • Net {float(pct.get("netral",0)):.2f}%</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔎 Detail", "⬇️ Export"])

    with tab1:
        # Sentiment
        sent_df = pd.DataFrame({"sentimen": list(pct.keys()), "persen": list(pct.values())})
        if not sent_df.empty:
            fig_sent = px.bar(sent_df.sort_values("persen", ascending=False), x="sentimen", y="persen", text="persen")
            fig_sent.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig_sent.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_sent, use_container_width=True)

        # Topic
        if not topic.empty:
            topic = topic.rename(columns={"jumlah": "topik"})
            topic_view = topic.sort_values("count", ascending=False).head(top_n)
            fig_topic = px.bar(topic_view.sort_values("count"), x="count", y="topik", orientation="h", text="persentase")
            fig_topic.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig_topic.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_topic, use_container_width=True)

        # Insight
        mc = ins.get("most_complained", {})
        mp = ins.get("most_praised", {})
        ma = ins.get("most_adequate", {})
        st.markdown('<div class="insight">', unsafe_allow_html=True)
        st.markdown("**Key Takeaways:**")
        if mc:
            st.write(f"- Paling dikeluhkan: **{mc.get('topic')}** (n={mc.get('n')}, avg {mc.get('avg_rating')}).")
        if mp:
            st.write(f"- Paling dipuji: **{mp.get('topic')}** (n={mp.get('n')}, avg {mp.get('avg_rating')}).")
        if ma:
            st.write(f"- Paling netral: **{ma.get('topic')}** (n={ma.get('n')}, avg {ma.get('avg_rating')}).")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔎 Tabel Ringkasan Topic")
        st.dataframe(topic if not topic.empty else pd.DataFrame(), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("⬇️ Export")
        st.download_button(
            "Download dashboard_data.json",
            data=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name="dashboard_data.json",
            mime="application/json",
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    footer()


def page_timeseries_policy():
    header_center()
    st.markdown("### ⏳ Deret Waktu & Analisis Kebijakan")
    st.caption("Sumber data: data bulanan + forecast skenario + ringkasan evaluasi model (CSV).")

    monthly = load_csv(MONTHLY_CSV, "data_clean_monthly.csv")
    forecast = load_csv(FORECAST_CSV, "forecast_kb_aktif_2025_skenario.csv")
    metrics = load_csv(METRICS_CSV, "model_summary_metrics.csv")

    # Parse tanggal
    monthly["bulan"] = pd.to_datetime(monthly["bulan"])
    forecast["bulan"] = pd.to_datetime(forecast["bulan"])

    # FILTER interaktif
    min_d, max_d = monthly["bulan"].min(), monthly["bulan"].max()
    date_range = st.slider(
        "Rentang Bulan (Historis)",
        min_value=min_d.to_pydatetime(),
        max_value=max_d.to_pydatetime(),
        value=(min_d.to_pydatetime(), max_d.to_pydatetime()),
    )
    show_pus = st.toggle("Tampilkan PUS", value=True)
    skenario = st.selectbox("Skenario Forecast", ["Base", "Up(+2%)", "Down(-2%)"], index=0)

    mview = monthly[(monthly["bulan"] >= pd.to_datetime(date_range[0])) & (monthly["bulan"] <= pd.to_datetime(date_range[1]))].copy()

    tab1, tab2, tab3 = st.tabs(["📈 Tren Historis", "🔮 Forecast 2025", "📌 Evaluasi Model"])

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mview["bulan"], y=mview["kb_aktif"], name="KB Aktif"))
        if show_pus:
            fig.add_trace(go.Scatter(x=mview["bulan"], y=mview["pus"], name="PUS"))
        fig.update_layout(height=440, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="insight">', unsafe_allow_html=True)
        st.markdown("**Catatan kebijakan (template):**")
        st.write("- Tentukan tanggal intervensi kebijakan → bandingkan rata-rata before–after.")
        st.write("- Tambahkan indikator eksternal (mis. program/anggaran/edukasi) untuk interpretasi.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        figf = go.Figure()
        figf.add_trace(go.Scatter(x=forecast["bulan"], y=forecast[skenario], name=f"Forecast: {skenario}"))

        # band CI
        if "CI_U" in forecast.columns and "CI_L" in forecast.columns:
            figf.add_trace(go.Scatter(x=forecast["bulan"], y=forecast["CI_U"], line=dict(width=0), showlegend=False, name="CI Upper"))
            figf.add_trace(go.Scatter(x=forecast["bulan"], y=forecast["CI_L"], fill="tonexty", line=dict(width=0), name="Confidence Interval"))

        figf.update_layout(height=440, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h"))
        st.plotly_chart(figf, use_container_width=True)

        with st.expander("Lihat tabel forecast"):
            st.dataframe(forecast, use_container_width=True)

    with tab3:
        row = metrics.iloc[0].to_dict() if len(metrics) else {}

        st.markdown(
            f"""
            <div class="kpi-grid">
              <div class="kpi">
                <div class="kpi-top"><div class="kpi-title">Benchmark MAPE</div><div>📏</div></div>
                <div class="kpi-value">{float(row.get("benchmark_mape", np.nan)):.2f}</div>
                <div class="kpi-sub">lebih kecil lebih baik</div>
              </div>
              <div class="kpi">
                <div class="kpi-top"><div class="kpi-title">SARIMAX MAPE</div><div>🧠</div></div>
                <div class="kpi-value">{float(row.get("sarimax_mape", np.nan)):.2f}</div>
                <div class="kpi-sub">model utama</div>
              </div>
              <div class="kpi">
                <div class="kpi-top"><div class="kpi-title">Walkforward MAPE</div><div>🔁</div></div>
                <div class="kpi-value">{float(row.get("walkforward_mape", np.nan)):.2f}</div>
                <div class="kpi-sub">uji rolling</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Ringkasan Parameter Terbaik")
        st.write(f"- best_order: `{row.get('best_order')}`")
        st.write(f"- best_seasonal: `{row.get('best_seasonal')}`")
        st.write(f"- pearson_r: `{row.get('pearson_r')}` • pearson_p: `{row.get('pearson_p')}`")
        st.markdown("</div>", unsafe_allow_html=True)

    # Export
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("⬇️ Export")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("Download data_clean_monthly.csv", monthly.to_csv(index=False).encode("utf-8"),
                           file_name="data_clean_monthly.csv", mime="text/csv", use_container_width=True)
    with c2:
        st.download_button("Download forecast_kb_aktif_2025_skenario.csv", forecast.to_csv(index=False).encode("utf-8"),
                           file_name="forecast_kb_aktif_2025_skenario.csv", mime="text/csv", use_container_width=True)
    with c3:
        st.download_button("Download model_summary_metrics.csv", metrics.to_csv(index=False).encode("utf-8"),
                           file_name="model_summary_metrics.csv", mime="text/csv", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    footer()

# =========================
# ROUTER
# =========================
def app():
    if not st.session_state.auth:
        login_page()
        return

    with st.sidebar:
        st.markdown("## 🎓 Navigasi Mata Kuliah")
        st.caption("Dipisah sesuai scope project")
        st.write(f"Login: **{st.session_state.user}**")

        page = st.radio(
            "Pilih Halaman",
            ["Medsos & People Analytics", "Deret Waktu & Analisis Kebijakan"],
            index=0 if st.session_state.page == "Medsos & People Analytics" else 1,
        )
        st.session_state.page = page

        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.auth = False
            st.session_state.user = None
            st.rerun()

    if st.session_state.page == "Medsos & People Analytics":
        page_people()
    else:
        page_timeseries_policy()

app()

