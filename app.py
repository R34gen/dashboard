# app.py
# ============================================================
# Dashboard Analitik Media Sosial Berbasis Rating Aplikasi SIGA
# Konversi: Analitik Media Sosial • People Analytics • Deployment Aplikasi
# UI/UX: Bright theme, black font, large logos, clean cards, helpful controls
# Core project tetap:
# - sumber data utama: data/dataset_final.csv
# - topic modeling: data/ringkasan_topik_negatif.csv + data/ringkasan_topik_positif.csv (opsional)
# - mapping label & action: data/topic_label_map.csv (opsional)
# - people analytics: frequency/impact/priority + exemplars
# - deployment analytics: upload CSV opsional + export CSV
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from datetime import datetime
import io
import textwrap

# ------------------------------------------------------------
# 0) PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Analitik Media Sosial Berbasis Rating Aplikasi SIGA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# 1) PATHS & FILE NAMES
# ------------------------------------------------------------
ROOT = Path(__file__).parent
DATA = ROOT / "data"

LOGO_UPN = ROOT / "logo_upn.png"
LOGO_BKKBN = ROOT / "logo_bkkbn.png"

DATASET_FINAL = DATA / "dataset_final.csv"
TOP_NEG = DATA / "ringkasan_topik_negatif.csv"
TOP_POS = DATA / "ringkasan_topik_positif.csv"
TOPIC_MAP = DATA / "topic_label_map.csv"

PX_TEMPLATE = "plotly_white"

# ------------------------------------------------------------
# 2) SESSION STATE (LOGIN/LOGOUT + UI STATE)
# ------------------------------------------------------------
if "logged_in" not in st.session_state:
    # Default TRUE agar tidak mengganggu alurmu, tapi fitur logout tetap ada
    st.session_state.logged_in = True

if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

# ------------------------------------------------------------
# 3) FORCE LIGHT THEME + UI/UX CSS
#    - Tujuan: background cerah beneran + font hitam + box tidak nabrak
# ------------------------------------------------------------
st.markdown(
    """
<script>
/* Soft attempt to hint light theme (CSS below is the real force) */
try {
  const root = window.parent.document.documentElement;
  root.setAttribute("data-theme", "light");
} catch(e) {}
</script>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
/* ===== GLOBAL: FORCE LIGHT LOOK ===== */
html, body, [data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg, #F6FAFF 0%, #ECF3FF 100%) !important;
}
section.main > div{
  background: transparent !important;
}
[data-testid="stSidebar"]{
  background: #FFFFFF !important;
  border-right: 1px solid rgba(15,23,42,0.10);
}
*{
  color: #0B0F19 !important;
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}

/* ===== LAYOUT ===== */
.block-container{
  max-width: 1280px;
  padding-top: 0.9rem;
  padding-bottom: 2.0rem;
}

/* ===== HERO ===== */
.hero{
  background: linear-gradient(135deg, rgba(37,99,235,0.16), rgba(99,102,241,0.12)) !important;
  border: 1px solid rgba(15,23,42,0.10);
  border-radius: 24px;
  padding: 18px 18px;
  box-shadow: 0 14px 32px rgba(2,6,23,0.10);
  margin-bottom: 14px;
}
.hero-title{
  font-size: 34px;
  font-weight: 950;
  letter-spacing: -0.02em;
  line-height: 1.1;
  margin: 0;
}
.hero-sub{
  margin-top: 8px;
  font-size: 13px;
  color: #334155 !important;
}
.badges{
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.badge{
  display:inline-flex;
  align-items:center;
  gap:6px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(15,23,42,0.12);
  background: rgba(255,255,255,0.75);
  font-size: 12px;
  font-weight: 750;
  color: #0B0F19 !important;
}

/* ===== CARDS ===== */
.card{
  background: #FFFFFF !important;
  border: 1px solid rgba(15,23,42,0.10) !important;
  border-radius: 18px;
  padding: 16px 16px 14px 16px;
  box-shadow: 0 10px 24px rgba(2,6,23,0.08) !important;
  margin-bottom: 14px;
}
.card-title{
  font-size: 18px;
  font-weight: 900;
  margin: 0;
}
.card-sub{
  margin-top: 6px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #334155 !important;
}

/* ===== KPI ===== */
.kpi-grid{
  display:grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin: 10px 0 14px 0;
}
.kpi{
  background: #FFFFFF !important;
  border: 1px solid rgba(15,23,42,0.10) !important;
  border-radius: 16px;
  padding: 14px 14px;
  box-shadow: 0 8px 20px rgba(2,6,23,0.06) !important;
}
.kpi-k{ font-size: 12px; font-weight: 850; color: #334155 !important; }
.kpi-v{ font-size: 26px; font-weight: 950; margin-top: 6px; }
.kpi-note{
  display:inline-block;
  margin-top: 8px;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid rgba(15,23,42,0.12);
  background: rgba(236,243,255,0.65);
  color: #334155 !important;
  font-size: 11px;
}

/* ===== TABS as pills ===== */
.stTabs [data-baseweb="tab-list"]{
  gap: 8px;
  margin-top: 6px;
}
.stTabs [data-baseweb="tab"]{
  background: rgba(255,255,255,0.65) !important;
  border: 1px solid rgba(15,23,42,0.10) !important;
  border-radius: 999px !important;
  padding: 8px 12px !important;
  font-weight: 800 !important;
}
.stTabs [aria-selected="true"]{
  background: #FFFFFF !important;
  border: 1px solid rgba(37,99,235,0.35) !important;
}

/* ===== DATAFRAME ===== */
[data-testid="stDataFrame"]{
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(15,23,42,0.10);
}

/* ===== INPUTS / SELECTS ===== */
input, textarea, [data-baseweb="select"]{
  background: #FFFFFF !important;
}
button[kind="primary"]{
  border-radius: 12px !important;
  font-weight: 900 !important;
}

/* ===== SMALL TEXT ===== */
.small-muted{
  color: #334155 !important;
  font-size: 12px;
}
.hr{
  height: 1px;
  background: rgba(15,23,42,0.10);
  margin: 10px 0;
}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# 4) UI HELPERS
# ------------------------------------------------------------
def show_logo(path: Path, width: int = 170):
    if path.exists():
        st.image(str(path), width=width)
    else:
        st.warning(f"Logo tidak ditemukan: {path.name} (pastikan sefolder dengan app.py)")

def card_open(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="card">
          <div class="card-title">{title}</div>
          <div class="card-sub">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )

def card_close():
    st.markdown("</div>", unsafe_allow_html=True)

def nice_number(x: float | int) -> str:
    try:
        return f"{int(x):,}"
    except Exception:
        return str(x)

def safe_read_csv(path: Path) -> pd.DataFrame | None:
    try:
        if path.exists():
            return pd.read_csv(path)
        return None
    except Exception as e:
        st.error(f"Gagal membaca {path.name}: {e}")
        return None

# ------------------------------------------------------------
# 5) CORE DATA FUNCTIONS (tetap inti)
# ------------------------------------------------------------
def coalesce_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None

def normalize_sentiment(x) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip().lower()
    if s in {"positive", "positif", "pos"}:
        return "positif"
    if s in {"negative", "negatif", "neg"}:
        return "negatif"
    if s in {"neutral", "netral", "neu"}:
        return "netral"
    return s

def detect_dataset_schema(df: pd.DataFrame) -> dict:
    sent_col = coalesce_col(df, ["sentimen", "sentiment", "label_sentimen", "label"])
    topic_col = coalesce_col(df, ["topic_id", "topic", "topik", "dominant_topic", "dom_topic"])
    rating_col = coalesce_col(df, ["rating", "rate", "score", "bintang", "stars"])
    text_col = coalesce_col(df, ["text", "ulasan", "review", "komentar", "steming_data"])
    return {"sent_col": sent_col, "topic_col": topic_col, "rating_col": rating_col, "text_col": text_col}

def standardize_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict, str | None]:
    schema = detect_dataset_schema(df)
    missing = [k for k, v in schema.items() if v is None]
    if missing:
        return df, schema, f"Kolom wajib tidak ditemukan: {', '.join(missing)}"

    tmp = df.copy()
    tmp[schema["sent_col"]] = tmp[schema["sent_col"]].apply(normalize_sentiment)
    tmp[schema["rating_col"]] = pd.to_numeric(tmp[schema["rating_col"]], errors="coerce")
    tmp[schema["topic_col"]] = pd.to_numeric(tmp[schema["topic_col"]], errors="coerce")
    tmp = tmp.dropna(subset=[schema["rating_col"], schema["topic_col"]])

    df_std = pd.DataFrame(
        {
            "sentimen": tmp[schema["sent_col"]].astype(str).str.lower().str.strip(),
            "topic_id": tmp[schema["topic_col"]].astype(int),
            "rating": tmp[schema["rating_col"]].astype(float),
            "text": tmp[schema["text_col"]].astype(str),
        }
    )
    return df_std, schema, None

@st.cache_data(show_spinner=False)
def load_dataset_final(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_topic_label_map(path: Path) -> pd.DataFrame:
    mp = pd.read_csv(path)
    mp["sentimen"] = mp["sentimen"].astype(str).str.lower().str.strip()
    mp["topic_id"] = pd.to_numeric(mp["topic_id"], errors="coerce")
    mp = mp.dropna(subset=["topic_id"]).copy()
    mp["topic_id"] = mp["topic_id"].astype(int)

    for col in ["label", "action"]:
        if col not in mp.columns:
            mp[col] = ""

    return mp[["sentimen", "topic_id", "label", "action"]]

def compute_topic_metrics(df_std: pd.DataFrame, sent: str, min_support: int = 20):
    tmp = df_std[df_std["sentimen"] == sent].copy()
    if tmp.empty:
        return None, None, None, "Data kosong setelah filter sentimen."

    topic_summary = (
        tmp.groupby("topic_id")
        .agg(
            frequency=("topic_id", "size"),
            mean_rating=("rating", "mean"),
            median_rating=("rating", "median"),
        )
        .reset_index()
    )

    topic_summary = topic_summary[topic_summary["frequency"] >= min_support].copy()
    if topic_summary.empty:
        return None, None, None, f"Tidak ada topik dengan support >= {min_support}."

    freq_thr = float(topic_summary["frequency"].median())
    rate_thr = float(topic_summary["mean_rating"].median())

    def assign_priority(row):
        high_freq = row["frequency"] >= freq_thr
        low_rate = row["mean_rating"] <= rate_thr
        if high_freq and low_rate:
            return "P1 (Prioritas Tinggi)"
        if high_freq or low_rate:
            return "P2 (Prioritas Sedang)"
        return "P3 (Prioritas Rendah)"

    topic_summary["priority"] = topic_summary.apply(assign_priority, axis=1)
    topic_summary = topic_summary.sort_values(["priority", "frequency"], ascending=[True, False])

    return topic_summary, tmp, (freq_thr, rate_thr), None

def pick_exemplars(df_sent: pd.DataFrame, topic_id: int, n: int = 5):
    sub = df_sent[df_sent["topic_id"] == topic_id].copy()
    if sub.empty:
        return sub
    sub = sub.drop_duplicates(subset=["text"])
    sub["len"] = sub["text"].astype(str).str.len()
    # Representatif: lebih panjang = lebih informatif, rating rendah dulu untuk negatif (bisa berubah tergantung sentimen)
    sub = sub.sort_values(["len", "rating"], ascending=[False, True]).head(n)
    return sub[["topic_id", "rating", "text"]]

# ------------------------------------------------------------
# 6) SIDEBAR: NAV + LOGOUT + GLOBAL FILTERS + FILE STATUS
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎛️ Kontrol & Navigasi")

    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Page nav (UX improvement: user can jump)
    page = st.radio(
        "Halaman",
        ["Dashboard", "Tentang & Cara Pakai"],
        index=0 if st.session_state.active_page == "Dashboard" else 1,
        help="Dashboard = analitik & visualisasi. Tentang = deskripsi metode + interpretasi untuk laporan."
    )
    st.session_state.active_page = page

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.markdown("### 📁 Status File")
    st.caption("Agar tidak error saat presentasi, file wajib/opsional dicek di sini.")

    def file_ok(p: Path) -> str:
        return "✅" if p.exists() else "❌"

    st.write(f"{file_ok(DATASET_FINAL)} dataset_final.csv (WAJIB)")
    st.write(f"{file_ok(TOP_NEG)} ringkasan_topik_negatif.csv (opsional)")
    st.write(f"{file_ok(TOP_POS)} ringkasan_topik_positif.csv (opsional)")
    st.write(f"{file_ok(TOPIC_MAP)} topic_label_map.csv (opsional)")
    st.write(f"{file_ok(LOGO_UPN)} logo_upn.png (root)")
    st.write(f"{file_ok(LOGO_BKKBN)} logo_bkkbn.png (root)")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.markdown("### 🔎 Filter Global (opsional)")
    st.caption("Filter ini mempengaruhi Overview & People Analytics & Deployment (kalau tidak upload CSV).")

# ------------------------------------------------------------
# 7) LOGIN GATE
# ------------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown(
        """
        <div class="card">
          <div class="card-title">Kamu sudah logout</div>
          <div class="card-sub">Klik tombol login untuk kembali ke dashboard.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🔑 Login lagi", use_container_width=True):
        st.session_state.logged_in = True
        st.rerun()
    st.stop()

# ------------------------------------------------------------
# 8) LOAD DATASET FINAL (Wajib)
# ------------------------------------------------------------
if not DATASET_FINAL.exists():
    st.error("dataset_final.csv tidak ditemukan di folder data/. Pastikan ada di data/dataset_final.csv")
    st.stop()

try:
    df_raw = load_dataset_final(DATASET_FINAL)
except Exception as e:
    st.error(f"Gagal membaca dataset_final.csv: {e}")
    st.stop()

df_std, schema, err = standardize_dataset(df_raw)
if err:
    st.error(f"dataset_final.csv invalid: {err}")
    st.info(f"Skema terdeteksi: {schema}")
    st.stop()

# Sidebar filters (setelah dataset tersedia)
with st.sidebar:
    rating_vals = sorted(df_std["rating"].dropna().unique().tolist())
    sent_vals = sorted(df_std["sentimen"].dropna().unique().tolist())

    rating_filter = st.multiselect("Rating", rating_vals)
    sent_filter = st.multiselect("Sentimen", sent_vals)

df_view = df_std.copy()
if rating_filter:
    df_view = df_view[df_view["rating"].isin(rating_filter)]
if sent_filter:
    df_view = df_view[df_view["sentimen"].isin(sent_filter)]

# Optional files
top_neg = safe_read_csv(TOP_NEG) if TOP_NEG.exists() else None
top_pos = safe_read_csv(TOP_POS) if TOP_POS.exists() else None
topic_map = load_topic_label_map(TOPIC_MAP) if TOPIC_MAP.exists() else pd.DataFrame()

# ------------------------------------------------------------
# 9) COMPUTE OVERVIEW METRICS (core tetap)
# ------------------------------------------------------------
total_data = int(len(df_view))
avg_rating = float(df_view["rating"].mean()) if total_data else 0.0
pos_pct = 100.0 * float((df_view["sentimen"] == "positif").mean()) if total_data else 0.0
neg_pct = 100.0 * float((df_view["sentimen"] == "negatif").mean()) if total_data else 0.0

dist_rating = (
    df_view.groupby("rating")
    .size()
    .reset_index(name="jumlah_ulasan")
    .sort_values("rating")
)
dist_sent = (
    df_view.groupby("sentimen")
    .size()
    .reset_index(name="jumlah_ulasan")
    .sort_values("jumlah_ulasan", ascending=False)
)

# ------------------------------------------------------------
# 10) HERO HEADER (LOGO BESAR + TITLE)
# ------------------------------------------------------------
st.markdown('<div class="hero">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1.35, 4.3, 1.35], vertical_alignment="center")

with c1:
    show_logo(LOGO_UPN, width=175)

with c2:
    st.markdown(
        """
        <div class="hero-title">Dashboard Analitik Media Sosial Berbasis Rating Aplikasi SIGA</div>
        <div class="hero-sub">
          Dashboard cerah untuk presentasi: ringkas, kontras tinggi, dan siap dipakai dosen/penilai.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="badges">
          <span class="badge">🎓 UPN</span>
          <span class="badge">🏛️ BKKBN Jawa Timur</span>
          <span class="badge">📊 Analitik Medsos</span>
          <span class="badge">🧑‍💼 People Analytics</span>
          <span class="badge">🚀 Streamlit Deployment</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    show_logo(LOGO_BKKBN, width=175)

st.markdown("</div>", unsafe_allow_html=True)

# KPI Row
st.markdown(
    f"""
    <div class="kpi-grid">
      <div class="kpi"><div class="kpi-k">Total Ulasan (setelah filter)</div><div class="kpi-v">{nice_number(total_data)}</div><div class="kpi-note">dataset_final.csv</div></div>
      <div class="kpi"><div class="kpi-k">Rata-rata Rating</div><div class="kpi-v">{avg_rating:.2f}</div><div class="kpi-note">computed</div></div>
      <div class="kpi"><div class="kpi-k">% Positif</div><div class="kpi-v">{pos_pct:.2f}%</div><div class="kpi-note">computed</div></div>
      <div class="kpi"><div class="kpi-k">% Negatif</div><div class="kpi-v">{neg_pct:.2f}%</div><div class="kpi-note">computed</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# UX improvement: quick notes about filters
if rating_filter or sent_filter:
    st.caption("ℹ️ Kamu sedang memakai filter global (sidebar). KPI & grafik mengikuti filter tersebut.")

# ------------------------------------------------------------
# 11) PAGE ROUTING
# ------------------------------------------------------------
if st.session_state.active_page == "Tentang & Cara Pakai":
    card_open("Tentang Dashboard", "Ringkasan metode & cara menjelaskan saat presentasi (tanpa mengubah core analitik).")

    st.markdown(
        """
**Tujuan proyek**
- **Analitik Media Sosial**: memahami apa yang sering dibicarakan pada ulasan **positif vs negatif**.
- **People Analytics**: mengubah insight topik menjadi **prioritas aksi** (frequency × impact) dan bukti contoh ulasan.
- **Deployment Aplikasi**: menyajikan hasil analitik dalam bentuk aplikasi interaktif (Streamlit), lengkap dengan export.

**Data yang dipakai**
- Sumber utama aplikasi ini: **`data/dataset_final.csv`**.
- Kolom minimal (boleh nama kolom berbeda, tapi harus terdeteksi): `sentimen`, `topic_id`, `rating`, `text`.

**Topic Modeling**
- LDA dihitung di notebook → hasilnya diexport sebagai:
  - `data/ringkasan_topik_negatif.csv`
  - `data/ringkasan_topik_positif.csv`
- Aplikasi menampilkan ringkasan agar stabil dan cepat (tidak hitung LDA di server).

**People Analytics**
- Menghitung:
  - `frequency` (berapa banyak ulasan per topic)
  - `mean_rating` & `median_rating` sebagai proxy impact
  - label prioritas: **P1/P2/P3** berdasarkan ambang median (frequency tinggi & rating rendah → P1).

**Deployment Analytics**
- Kamu bisa upload CSV baru (opsional) untuk melihat output berubah.
- Bisa export:
  - `prioritas_masalah.csv`
  - `exemplars_topik.csv`

**Cara presentasi singkat (struktur aman)**
1) Tunjukkan KPI & distribusi rating/sentimen.
2) Tunjukkan ringkasan topik (positif vs negatif).
3) Tunjukkan People Analytics: prioritas P1 dan rekomendasi aksi.
4) Tunjukkan Deployment: export hasil sebagai bukti aplikasi bekerja end-to-end.
        """
    )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.markdown("### Checklist sebelum presentasi")
    ok_list = [
        ("dataset_final.csv ada", DATASET_FINAL.exists()),
        ("logo_upn.png ada (root)", LOGO_UPN.exists()),
        ("logo_bkkbn.png ada (root)", LOGO_BKKBN.exists()),
        ("ringkasan_topik_negatif.csv ada (opsional)", TOP_NEG.exists()),
        ("ringkasan_topik_positif.csv ada (opsional)", TOP_POS.exists()),
        ("topic_label_map.csv ada (opsional)", TOPIC_MAP.exists()),
    ]
    for label, ok in ok_list:
        st.write(("✅ " if ok else "❌ ") + label)

    card_close()
    st.stop()

# ------------------------------------------------------------
# 12) DASHBOARD: TABS (CORE tetap)
# ------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Overview", "🧩 Topic Modeling", "🧑‍💼 People Analytics", "🚀 Deployment Analytics"]
)

# ============================================================
# TAB 1 — OVERVIEW
# ============================================================
with tab1:
    card_open(
        "Overview: Distribusi Rating & Sentimen",
        "Visualisasi ringkas untuk pembuka presentasi. Semua dihitung dari dataset_final.csv (terfilter bila filter aktif).",
    )

    colA, colB = st.columns(2, gap="large")

    with colA:
        st.markdown("**Distribusi Rating**")
        if dist_rating.empty:
            st.warning("Tidak ada data setelah filter.")
        else:
            fig = px.bar(dist_rating, x="rating", y="jumlah_ulasan", template=PX_TEMPLATE)
            fig.update_layout(height=360, xaxis_title="Rating", yaxis_title="Jumlah Ulasan")
            st.plotly_chart(fig, use_container_width=True)

    with colB:
        st.markdown("**Distribusi Sentimen**")
        if dist_sent.empty:
            st.warning("Tidak ada data setelah filter.")
        else:
            fig2 = px.pie(dist_sent, names="sentimen", values="jumlah_ulasan", template=PX_TEMPLATE)
            fig2.update_layout(height=360)
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # UX improvement: quick insight text
    st.markdown("### Insight Cepat (Auto)")
    if total_data > 0:
        st.write(
            f"- Total ulasan yang dianalisis: **{nice_number(total_data)}**"
            f"\n- Rata-rata rating: **{avg_rating:.2f}**"
            f"\n- Proporsi negatif: **{neg_pct:.2f}%** | positif: **{pos_pct:.2f}%**"
        )
        if neg_pct > 60:
            st.info("Interpretasi: dominasi sentimen negatif cukup tinggi → fokus People Analytics pada prioritas perbaikan (P1).")
        elif pos_pct > 60:
            st.success("Interpretasi: dominasi sentimen positif → fokus mempertahankan fitur/experience yang disukai.")
        else:
            st.warning("Interpretasi: proporsi cukup seimbang → prioritasi perlu kombinasi frequency & impact per topik.")
    else:
        st.warning("Tidak ada data untuk menghasilkan insight cepat (kemungkinan filter terlalu ketat).")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # UX improvement: data preview in expander (tidak mengganggu tampilan)
    with st.expander("🔍 Lihat preview data (untuk verifikasi saat presentasi)", expanded=False):
        st.caption("Menunjukkan bahwa aplikasi benar-benar membaca data terbaru.")
        st.dataframe(df_view.head(50), use_container_width=True)

    card_close()

# ============================================================
# TAB 2 — TOPIC MODELING (display ringkasan LDA dari notebook)
# ============================================================
with tab2:
    card_open(
        "Topic Modeling: Ringkasan Topik LDA (Positif vs Negatif)",
        "Menampilkan output LDA dari notebook (CSV ringkasan). Stabil & cepat untuk deployment.",
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("### NEGATIF")
        if top_neg is None or top_neg.empty:
            st.warning("File ringkasan_topik_negatif.csv belum ada atau kosong.")
        else:
            st.dataframe(top_neg, use_container_width=True)

            # UX improvement: quick download ringkasan
            st.download_button(
                "⬇️ Download ringkasan_topik_negatif.csv",
                data=top_neg.to_csv(index=False).encode("utf-8"),
                file_name="ringkasan_topik_negatif.csv",
                mime="text/csv",
                use_container_width=True,
            )

    with col2:
        st.markdown("### POSITIF")
        if top_pos is None or top_pos.empty:
            st.warning("File ringkasan_topik_positif.csv belum ada atau kosong.")
        else:
            st.dataframe(top_pos, use_container_width=True)

            st.download_button(
                "⬇️ Download ringkasan_topik_positif.csv",
                data=top_pos.to_csv(index=False).encode("utf-8"),
                file_name="ringkasan_topik_positif.csv",
                mime="text/csv",
                use_container_width=True,
            )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # UX improvement: auto narrative based on top words (if column exists)
    st.markdown("### Narasi Singkat (Auto) untuk Laporan")
    def auto_narrative(df: pd.DataFrame, label: str) -> str:
        if df is None or df.empty:
            return f"- {label}: belum ada ringkasan topik."
        cols = [c.lower() for c in df.columns]
        # try to find top_words column
        tw_col = None
        for c in df.columns:
            if c.lower() in {"top_words", "keywords", "kata_kunci", "topwords"}:
                tw_col = c
                break
        if tw_col is None:
            return f"- {label}: ringkasan tersedia, tapi kolom kata kunci tidak ditemukan."
        # take first 3 topics
        lines = []
        for i, row in df.head(3).iterrows():
            words = str(row[tw_col])
            short = ", ".join([w.strip() for w in words.split(",")[:6]])
            lines.append(f"  - Topik {i}: {short}")
        return f"- {label}: contoh kata kunci topik teratas:\n" + "\n".join(lines)

    st.write(auto_narrative(top_neg, "NEGATIF"))
    st.write(auto_narrative(top_pos, "POSITIF"))

    st.info(
        "Catatan: Label topik sebaiknya ditulis di laporan (interpretasi manusia), "
        "bukan dipaksakan otomatis oleh model. Ini lebih aman untuk akademik."
    )

    card_close()

# ============================================================
# TAB 3 — PEOPLE ANALYTICS (priority matrix + exemplars + actions)
# ============================================================
with tab3:
    card_open(
        "People Analytics: Prioritas Masalah & Rekomendasi Aksi",
        "Frequency × Impact (rating) + contoh ulasan representatif + mapping label/action (opsional).",
    )

    # Controls at top (UX)
    ctrl1, ctrl2, ctrl3 = st.columns([1.2, 1.0, 1.2], gap="large")
    with ctrl1:
        sent_choice = st.selectbox("Sentimen untuk prioritas", ["negatif", "positif"], index=0)
    with ctrl2:
        min_support = st.slider("Minimum support", 5, 300, 20, step=5)
    with ctrl3:
        n_ex = st.slider("Jumlah exemplars/topik", 3, 12, 5, step=1)

    topic_summary, df_sent, thr, e = compute_topic_metrics(df_view, sent_choice, min_support=min_support)
    if e:
        st.error(e)
        card_close()
    else:
        freq_thr, rate_thr = thr

        # merge label/action mapping if available
        if not topic_map.empty:
            mp = topic_map[topic_map["sentimen"] == sent_choice][["topic_id", "label", "action"]].copy()
            topic_summary = topic_summary.merge(mp, on="topic_id", how="left")

        # UX: summary chips
        p1 = int((topic_summary["priority"] == "P1 (Prioritas Tinggi)").sum())
        p2 = int((topic_summary["priority"] == "P2 (Prioritas Sedang)").sum())
        p3 = int((topic_summary["priority"] == "P3 (Prioritas Rendah)").sum())
        st.markdown(
            f"""
            <div class="badges">
              <span class="badge">Ambang Frequency (median): {freq_thr:.0f}</span>
              <span class="badge">Ambang Mean Rating (median): {rate_thr:.2f}</span>
              <span class="badge">P1: {p1} topik</span>
              <span class="badge">P2: {p2} topik</span>
              <span class="badge">P3: {p3} topik</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        st.markdown("### Tabel Prioritas")
        st.dataframe(topic_summary, use_container_width=True)

        # Scatter matrix (priority)
        st.markdown("### Matriks Prioritas (Frequency vs Impact)")
        fig = px.scatter(
            topic_summary,
            x="frequency",
            y="mean_rating",
            color="priority",
            hover_data=["topic_id", "median_rating"],
            template=PX_TEMPLATE,
        )
        fig.add_vline(x=freq_thr, line_dash="dash")
        fig.add_hline(y=rate_thr, line_dash="dash")
        fig.update_layout(height=420, xaxis_title="Frequency", yaxis_title="Mean Rating")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        # Exemplars per topic
        st.markdown("### Bukti: Contoh Ulasan Representatif (Exemplars)")
        topic_ids = topic_summary["topic_id"].astype(int).tolist()
        pick_topic = st.selectbox("Pilih topic_id untuk lihat contoh ulasan", topic_ids, index=0)

        ex_df = pick_exemplars(df_sent, int(pick_topic), n=n_ex)
        if ex_df.empty:
            st.warning("Tidak ada exemplars untuk topic_id ini.")
        else:
            # UX: show wrapped text
            ex_df_disp = ex_df.copy()
            ex_df_disp["text"] = ex_df_disp["text"].apply(lambda s: "\n".join(textwrap.wrap(str(s), width=110)))
            st.dataframe(ex_df_disp, use_container_width=True)

        # Action suggestions (if mapping exists)
        if "action" in topic_summary.columns:
            st.markdown("### Rekomendasi Aksi (dari topic_label_map.csv)")
            row = topic_summary[topic_summary["topic_id"] == int(pick_topic)]
            if not row.empty:
                lbl = row["label"].iloc[0] if "label" in row.columns else ""
                act = row["action"].iloc[0] if "action" in row.columns else ""
                if pd.isna(lbl): lbl = ""
                if pd.isna(act): act = ""
                if str(lbl).strip() == "" and str(act).strip() == "":
                    st.info("Untuk menampilkan rekomendasi aksi, isi topic_label_map.csv (kolom label & action).")
                else:
                    st.success(f"**Label Topik:** {lbl}")
                    st.write(f"**Aksi yang disarankan:** {act}")

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        # Export for report
        st.markdown("### Export untuk Laporan")
        st.download_button(
            "⬇️ Download people_analytics_prioritas.csv",
            data=topic_summary.to_csv(index=False).encode("utf-8"),
            file_name="people_analytics_prioritas.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.download_button(
            "⬇️ Download exemplars_topic.csv",
            data=ex_df.to_csv(index=False).encode("utf-8"),
            file_name="exemplars_topic.csv",
            mime="text/csv",
            use_container_width=True,
        )

    card_close()

# ============================================================
# TAB 4 — DEPLOYMENT ANALYTICS (dynamic input + export)
# ============================================================
with tab4:
    card_open(
        "Deployment Analytics (Dynamic)",
        "Upload/Filter → output berubah → export untuk laporan & presentasi. Core logic sama seperti People Analytics.",
    )

    st.markdown("### Input Data")
    uploaded = st.file_uploader(
        "Upload CSV (opsional). Jika kosong, aplikasi pakai dataset_final.csv (dengan filter global jika aktif).",
        type=["csv"],
    )

    if uploaded is not None:
        try:
            raw = pd.read_csv(uploaded)
            df_live, _, e2 = standardize_dataset(raw)
            if e2:
                st.error(f"CSV upload tidak valid: {e2}")
                df_live = None
            else:
                st.success("✅ Dataset upload dipakai (di-standarkan ke kolom sentimen/topic_id/rating/text).")
        except Exception as e:
            st.error(f"Gagal membaca CSV upload: {e}")
            df_live = None
    else:
        df_live = df_view
        st.info("ℹ️ Menggunakan dataset_final.csv (terpengaruh filter global di sidebar bila dipakai).")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    if df_live is None or df_live.empty:
        st.warning("Tidak ada data yang bisa dianalisis pada tab Deployment.")
        card_close()
    else:
        st.markdown("### Konfigurasi Analitik")
        c1, c2, c3 = st.columns([1.2, 1.0, 1.2], gap="large")
        with c1:
            sent_choice = st.selectbox("Sentimen (Deployment)", ["negatif", "positif", "netral"], index=0)
        with c2:
            min_support = st.slider("Minimum support (Deployment)", 5, 300, 20, step=5)
        with c3:
            n_ex = st.slider("Exemplars/topik (Deployment)", 3, 12, 5, step=1)

        topic_summary, df_sent, thr, e3 = compute_topic_metrics(df_live, sent_choice, min_support=min_support)
        if e3:
            st.error(e3)
            card_close()
        else:
            # merge mapping if exists
            if not topic_map.empty:
                mp = topic_map[topic_map["sentimen"] == sent_choice][["topic_id", "label", "action"]].copy()
                topic_summary = topic_summary.merge(mp, on="topic_id", how="left")

            st.markdown("### Output Prioritas (Dynamic)")
            st.dataframe(topic_summary, use_container_width=True)

            # exemplars
            st.markdown("### Exemplars (Dynamic)")
            topic_ids = topic_summary["topic_id"].astype(int).tolist()
            pick_topic = st.selectbox("Pilih topic_id (Deployment)", topic_ids, index=0)
            ex_df = pick_exemplars(df_sent, int(pick_topic), n=n_ex)
            if not ex_df.empty:
                ex_df_disp = ex_df.copy()
                ex_df_disp["text"] = ex_df_disp["text"].apply(lambda s: "\n".join(textwrap.wrap(str(s), width=110)))
                st.dataframe(ex_df_disp, use_container_width=True)

            st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

            # UX: report snippet generator (no change core, just helpful)
            st.markdown("### Generator Teks Laporan (Auto)")
            with st.expander("Klik untuk generate paragraf laporan", expanded=False):
                # choose top P1 topics
                p1_df = topic_summary[topic_summary["priority"] == "P1 (Prioritas Tinggi)"].head(5)
                if p1_df.empty:
                    st.write("Tidak ada P1 untuk konfigurasi ini. Coba turunkan min_support atau ganti sentimen.")
                else:
                    lines = []
                    for _, r in p1_df.iterrows():
                        tid = int(r["topic_id"])
                        freq = int(r["frequency"])
                        meanr = float(r["mean_rating"])
                        label = r["label"] if "label" in p1_df.columns else ""
                        if pd.isna(label): label = ""
                        if str(label).strip() != "":
                            lines.append(f"- Topik {tid} ({label}): frequency {freq}, mean rating {meanr:.2f}")
                        else:
                            lines.append(f"- Topik {tid}: frequency {freq}, mean rating {meanr:.2f}")

                    para = (
                        f"Pada sentimen **{sent_choice}**, matriks prioritas menunjukkan beberapa topik dengan prioritas tinggi (P1), "
                        f"ditandai oleh frekuensi ulasan yang tinggi dan/atau rating yang relatif rendah. "
                        f"Topik P1 yang paling dominan adalah:\n" + "\n".join(lines) +
                        "\n\nTemuan ini dapat digunakan sebagai dasar rekomendasi perbaikan produk/layanan untuk meningkatkan pengalaman pengguna."
                    )
                    st.text_area("Teks siap copy ke laporan", para, height=220)

            # Export
            st.markdown("### Export (Dynamic)")
            st.download_button(
                "⬇️ Download prioritas_masalah.csv",
                data=topic_summary.to_csv(index=False).encode("utf-8"),
                file_name="prioritas_masalah.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.download_button(
                "⬇️ Download exemplars_topik.csv",
                data=ex_df.to_csv(index=False).encode("utf-8"),
                file_name="exemplars_topik.csv",
                mime="text/csv",
                use_container_width=True,
            )

            st.caption("Catatan: Tab ini membuktikan deployment analytics bekerja end-to-end (input → process → output → export).")

            card_close()

# ------------------------------------------------------------
# 13) FOOTER
# ------------------------------------------------------------
st.markdown(
    f"<div class='small-muted'>© {datetime.now().year} • Dashboard cerah + font hitam + logo besar • "
    f"Core analitik tidak diubah • Build time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>",
    unsafe_allow_html=True,
)
