import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from datetime import datetime
import textwrap

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Dashboard Analitik Media Sosial Berbasis Rating Aplikasi SIGA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).parent
DATA = ROOT / "data"

LOGO_UPN = ROOT / "logo_upn.png"
LOGO_BKKBN = ROOT / "logo_bkkbn.png"

DATASET_FINAL = DATA / "dataset_final.csv"

# Fallback files (kalau dataset_final tidak punya kolom kata kunci topik)
TOP_NEG_FALLBACK = DATA / "ringkasan_topik_negatif.csv"
TOP_POS_FALLBACK = DATA / "ringkasan_topik_positif.csv"

TOPIC_MAP = DATA / "topic_label_map.csv"

PX_TEMPLATE = "plotly_white"

# =========================
# AUTH (WAJIB USER+PASS)
# =========================
# UBAH sesuai kebutuhanmu
USERS = {
    "admin": "admin123",
    "reagen": "siga2025"
}

def auth_ok(username: str, password: str) -> bool:
    return USERS.get(username, None) == password

# session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

# =========================
# FORCE LIGHT THEME + UI/UX CSS
# =========================
st.markdown("""
<script>
try {
  const root = window.parent.document.documentElement;
  root.setAttribute("data-theme", "light");
} catch(e) {}
</script>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ===== FORCE BRIGHT ===== */
html, body, [data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg, #F6FAFF 0%, #ECF3FF 100%) !important;
}
section.main > div{ background: transparent !important; }
[data-testid="stSidebar"]{
  background: #FFFFFF !important;
  border-right: 1px solid rgba(15,23,42,0.10);
}
*{
  color: #0B0F19 !important;
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}
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
  font-size: 34px; font-weight: 950; letter-spacing: -0.02em; line-height: 1.1; margin: 0;
}
.hero-sub{
  margin-top: 8px; font-size: 13px; color: #334155 !important;
}
.badges{ margin-top: 10px; display:flex; flex-wrap:wrap; gap:8px; }
.badge{
  display:inline-flex; align-items:center; gap:6px;
  padding: 6px 10px; border-radius: 999px;
  border: 1px solid rgba(15,23,42,0.12);
  background: rgba(255,255,255,0.78);
  font-size: 12px; font-weight: 750;
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
.card-title{ font-size: 18px; font-weight: 900; margin: 0; }
.card-sub{ margin-top: 6px; margin-bottom: 12px; font-size: 12px; color: #334155 !important; }
.hr{ height: 1px; background: rgba(15,23,42,0.10); margin: 10px 0; }

/* ===== KPI ===== */
.kpi-grid{
  display:grid; grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px; margin: 10px 0 14px 0;
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
  display:inline-block; margin-top: 8px; padding: 3px 8px; border-radius: 999px;
  border: 1px solid rgba(15,23,42,0.12);
  background: rgba(236,243,255,0.65);
  color: #334155 !important; font-size: 11px;
}

/* ===== TABS ===== */
.stTabs [data-baseweb="tab-list"]{ gap: 8px; margin-top: 6px; }
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
  border-radius: 14px; overflow: hidden;
  border: 1px solid rgba(15,23,42,0.10);
}

/* ===== BUTTONS (fix logout looks) ===== */
div[data-testid="stSidebar"] button{
  border-radius: 14px !important;
  font-weight: 900 !important;
}

/* custom logout button wrapper */
.logout-wrap button{
  background: linear-gradient(135deg, rgba(37,99,235,0.18), rgba(99,102,241,0.14)) !important;
  border: 1px solid rgba(37,99,235,0.35) !important;
}
.logout-wrap button:hover{
  background: linear-gradient(135deg, rgba(37,99,235,0.25), rgba(99,102,241,0.20)) !important;
}

/* Login form inputs */
input, textarea, [data-baseweb="select"]{ background: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# =========================
# UI HELPERS
# =========================
def show_logo(path: Path, width: int = 175):
    if path.exists():
        st.image(str(path), width=width)
    else:
        st.warning(f"Logo tidak ditemukan: {path.name} (pastikan sefolder app.py)")

def card_open(title: str, subtitle: str = ""):
    st.markdown(
        f"""<div class="card"><div class="card-title">{title}</div><div class="card-sub">{subtitle}</div>""",
        unsafe_allow_html=True
    )

def card_close():
    st.markdown("</div>", unsafe_allow_html=True)

def safe_read_csv(path: Path) -> pd.DataFrame | None:
    try:
        if path.exists():
            return pd.read_csv(path)
        return None
    except Exception as e:
        st.error(f"Gagal membaca {path.name}: {e}")
        return None

def nice_number(x):
    try:
        return f"{int(x):,}"
    except Exception:
        return str(x)

# =========================
# CORE DATA FUNCTIONS (tetap)
# =========================
def coalesce_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None

def normalize_sentiment(x) -> str:
    if pd.isna(x): return ""
    s = str(x).strip().lower()
    if s in {"positive","positif","pos"}: return "positif"
    if s in {"negative","negatif","neg"}: return "negatif"
    if s in {"neutral","netral","neu"}: return "netral"
    return s

def detect_dataset_schema(df: pd.DataFrame) -> dict:
    sent_col  = coalesce_col(df, ["sentimen","sentiment","label_sentimen","label"])
    topic_col = coalesce_col(df, ["topic_id","topic","topik","dominant_topic","dom_topic"])
    rating_col= coalesce_col(df, ["rating","rate","score","bintang","stars"])
    text_col  = coalesce_col(df, ["text","ulasan","review","komentar","steming_data"])
    # optional: kata kunci topik jika ada
    topwords_col = coalesce_col(df, ["top_words","topwords","keywords","kata_kunci"])
    return {"sent_col": sent_col, "topic_col": topic_col, "rating_col": rating_col, "text_col": text_col, "topwords_col": topwords_col}

def standardize_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict, str | None]:
    schema = detect_dataset_schema(df)
    must = ["sent_col","topic_col","rating_col","text_col"]
    miss = [k for k in must if schema.get(k) is None]
    if miss:
        return df, schema, f"Kolom wajib tidak ditemukan: {', '.join(miss)}"

    tmp = df.copy()
    tmp[schema["sent_col"]] = tmp[schema["sent_col"]].apply(normalize_sentiment)
    tmp[schema["rating_col"]] = pd.to_numeric(tmp[schema["rating_col"]], errors="coerce")
    tmp[schema["topic_col"]] = pd.to_numeric(tmp[schema["topic_col"]], errors="coerce")
    tmp = tmp.dropna(subset=[schema["rating_col"], schema["topic_col"]])

    df_std = pd.DataFrame({
        "sentimen": tmp[schema["sent_col"]].astype(str).str.lower().str.strip(),
        "topic_id": tmp[schema["topic_col"]].astype(int),
        "rating": tmp[schema["rating_col"]].astype(float),
        "text": tmp[schema["text_col"]].astype(str),
    })

    # optional column pass-through (kalau dataset_final hari ini sudah punya top_words per row)
    if schema.get("topwords_col") is not None:
        df_std["top_words"] = tmp[schema["topwords_col"]].astype(str)

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
    for col in ["label","action"]:
        if col not in mp.columns:
            mp[col] = ""
    return mp[["sentimen","topic_id","label","action"]]

def compute_topic_metrics(df_std: pd.DataFrame, sent: str, min_support: int = 20):
    tmp = df_std[df_std["sentimen"] == sent].copy()
    if tmp.empty:
        return None, None, None, "Data kosong setelah filter sentimen."

    topic_summary = (
        tmp.groupby("topic_id")
        .agg(frequency=("topic_id","size"),
             mean_rating=("rating","mean"),
             median_rating=("rating","median"))
        .reset_index()
    )
    topic_summary = topic_summary[topic_summary["frequency"] >= min_support].copy()
    if topic_summary.empty:
        return None, None, None, f"Tidak ada topik dengan support >= {min_support}."

    freq_thr = float(topic_summary["frequency"].median())
    rate_thr = float(topic_summary["mean_rating"].median())

    def assign_priority(row):
        high_freq = row["frequency"] >= freq_thr
        low_rate  = row["mean_rating"] <= rate_thr
        if high_freq and low_rate: return "P1 (Prioritas Tinggi)"
        if high_freq or low_rate:  return "P2 (Prioritas Sedang)"
        return "P3 (Prioritas Rendah)"

    topic_summary["priority"] = topic_summary.apply(assign_priority, axis=1)
    topic_summary = topic_summary.sort_values(["priority","frequency"], ascending=[True, False])
    return topic_summary, tmp, (freq_thr, rate_thr), None

def pick_exemplars(df_sent: pd.DataFrame, topic_id: int, n: int = 5):
    sub = df_sent[df_sent["topic_id"] == topic_id].copy()
    if sub.empty:
        return sub
    sub = sub.drop_duplicates(subset=["text"])
    sub["len"] = sub["text"].astype(str).str.len()
    sub = sub.sort_values(["len","rating"], ascending=[False, True]).head(n)
    return sub[["topic_id","rating","text"]]

# =========================
# LOGIN PAGE
# =========================
def login_page():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.35, 4.3, 1.35], vertical_alignment="center")
    with c1:
        show_logo(LOGO_UPN, width=170)
    with c2:
        st.markdown('<div class="hero-title">Dashboard Analitik Media Sosial Berbasis Rating Aplikasi SIGA</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Silakan login untuk mengakses dashboard (akses dibatasi user & password).</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="badges">
          <span class="badge">🎓 UPN</span>
          <span class="badge">🏛️ BKKBN Jawa Timur</span>
          <span class="badge">🔒 Restricted Access</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        show_logo(LOGO_BKKBN, width=170)
    st.markdown('</div>', unsafe_allow_html=True)

    card_open("Login", "Masukkan username & password yang valid.")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("🔑 Login", use_container_width=True):
        if auth_ok(u, p):
            st.session_state.logged_in = True
            st.session_state.username = u
            st.success("Login berhasil.")
            st.rerun()
        else:
            st.error("Username / password salah.")
    card_close()

# =========================
# TOPIC MODELING: "TERBARU"
# - Prioritas 1: kalau dataset_final punya kolom top_words/keywords per row,
#   kita agregasi ulang per topic_id & sentimen → ini paling "hari ini".
# - Prioritas 2: fallback ke ringkasan_topik_*.csv
# =========================
def topic_summary_from_dataset(df_std: pd.DataFrame) -> dict:
    """
    Return dict: {"negatif": df, "positif": df} kalau bisa dibuat dari dataset_final.
    Jika kolom top_words tidak ada, return {}.
    """
    if "top_words" not in df_std.columns:
        return {}

    # asumsi: top_words per row bisa berisi string kata kunci topik (misal "login, error, ...")
    # kita ambil representatif per topic_id dengan mode/most frequent non-empty
    out = {}
    for sent in ["negatif","positif"]:
        sub = df_std[df_std["sentimen"] == sent].copy()
        if sub.empty:
            out[sent] = pd.DataFrame()
            continue

        # pilih top_words non-empty
        sub["top_words"] = sub["top_words"].astype(str).str.strip()
        sub = sub[sub["top_words"].str.len() > 0].copy()

        if sub.empty:
            out[sent] = pd.DataFrame()
            continue

        # ambil top_words paling sering per topic_id
        agg = (sub.groupby("topic_id")["top_words"]
               .agg(lambda x: x.value_counts().index[0])
               .reset_index())

        # tambah frekuensi ulasan agar lebih informatif
        freq = (df_std[df_std["sentimen"] == sent]
                .groupby("topic_id").size().reset_index(name="jumlah_ulasan"))
        agg = agg.merge(freq, on="topic_id", how="left").sort_values("jumlah_ulasan", ascending=False)

        out[sent] = agg

    return out

# =========================
# MAIN APP
# =========================
if not st.session_state.logged_in:
    login_page()
    st.stop()

# ===== Sidebar (UX) =====
with st.sidebar:
    st.markdown("## 🎛️ Kontrol & Navigasi")
    st.caption(f"Login sebagai: **{st.session_state.username}**")

    # Fix logout button styling with wrapper
    st.markdown('<div class="logout-wrap">', unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    page = st.radio("Halaman", ["Dashboard", "Tentang & Cara Pakai"], index=0)
    st.session_state.active_page = page

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.markdown("### 📁 Status File")
    def ok(p: Path): return "✅" if p.exists() else "❌"
    st.write(f"{ok(DATASET_FINAL)} data/dataset_final.csv (WAJIB)")
    st.write(f"{ok(TOP_NEG_FALLBACK)} data/ringkasan_topik_negatif.csv (fallback)")
    st.write(f"{ok(TOP_POS_FALLBACK)} data/ringkasan_topik_positif.csv (fallback)")
    st.write(f"{ok(TOPIC_MAP)} data/topic_label_map.csv (opsional)")
    st.write(f"{ok(LOGO_UPN)} logo_upn.png (root)")
    st.write(f"{ok(LOGO_BKKBN)} logo_bkkbn.png (root)")

# ===== Load dataset_final =====
if not DATASET_FINAL.exists():
    st.error("dataset_final.csv tidak ditemukan di folder data/.")
    st.stop()

df_raw = load_dataset_final(DATASET_FINAL)
df_std, schema, err = standardize_dataset(df_raw)
if err:
    st.error(f"dataset_final.csv invalid: {err}")
    st.info(f"Skema terdeteksi: {schema}")
    st.stop()

# Optional mapping
topic_map = load_topic_label_map(TOPIC_MAP) if TOPIC_MAP.exists() else pd.DataFrame()

# Global filters in sidebar (after df ready)
with st.sidebar:
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.markdown("### 🔎 Filter Global (opsional)")
    rating_vals = sorted(df_std["rating"].dropna().unique().tolist())
    sent_vals = sorted(df_std["sentimen"].dropna().unique().tolist())
    rating_filter = st.multiselect("Rating", rating_vals)
    sent_filter = st.multiselect("Sentimen", sent_vals)

df_view = df_std.copy()
if rating_filter:
    df_view = df_view[df_view["rating"].isin(rating_filter)]
if sent_filter:
    df_view = df_view[df_view["sentimen"].isin(sent_filter)]

# ===== hero =====
st.markdown('<div class="hero">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1.35, 4.3, 1.35], vertical_alignment="center")
with c1:
    show_logo(LOGO_UPN, width=175)
with c2:
    st.markdown('<div class="hero-title">Dashboard Analitik Media Sosial Berbasis Rating Aplikasi SIGA</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">UI cerah + font hitam + kontras aman untuk presentasi. Data utama: dataset_final.csv (terbaru).</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="badges">
      <span class="badge">🎓 UPN</span>
      <span class="badge">🏛️ BKKBN Jawa Timur</span>
      <span class="badge">📊 Analitik Medsos</span>
      <span class="badge">🧑‍💼 People Analytics</span>
      <span class="badge">🚀 Deployment Streamlit</span>
    </div>
    """, unsafe_allow_html=True)
with c3:
    show_logo(LOGO_BKKBN, width=175)
st.markdown("</div>", unsafe_allow_html=True)

# KPI
total_data = int(len(df_view))
avg_rating = float(df_view["rating"].mean()) if total_data else 0.0
pos_pct = 100.0 * float((df_view["sentimen"] == "positif").mean()) if total_data else 0.0
neg_pct = 100.0 * float((df_view["sentimen"] == "negatif").mean()) if total_data else 0.0

st.markdown(
    f"""
    <div class="kpi-grid">
      <div class="kpi"><div class="kpi-k">Total Ulasan (terfilter)</div><div class="kpi-v">{nice_number(total_data)}</div><div class="kpi-note">dataset_final.csv</div></div>
      <div class="kpi"><div class="kpi-k">Rata-rata Rating</div><div class="kpi-v">{avg_rating:.2f}</div><div class="kpi-note">computed</div></div>
      <div class="kpi"><div class="kpi-k">% Positif</div><div class="kpi-v">{pos_pct:.2f}%</div><div class="kpi-note">computed</div></div>
      <div class="kpi"><div class="kpi-k">% Negatif</div><div class="kpi-v">{neg_pct:.2f}%</div><div class="kpi-note">computed</div></div>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# PAGES
# ============================================================
if st.session_state.active_page == "Tentang & Cara Pakai":
    card_open("Tentang & Cara Pakai", "Narasi siap presentasi (tidak mengubah core).")
    st.markdown("""
**Struktur presentasi yang aman:**
1) **Overview**: distribusi rating & sentimen (kondisi umum).
2) **Topic Modeling**: topik NEGATIF vs POSITIF (apa dikeluhkan vs disukai).
3) **People Analytics**: prioritas P1 (frequency tinggi + rating rendah) + rekomendasi aksi + exemplars.
4) **Deployment**: bukti end-to-end (upload → proses → export).

**Catatan penting**
- LDA dihitung di notebook, aplikasi hanya menampilkan output (lebih stabil).
- Jika `dataset_final.csv` menyimpan `top_words/keywords`, tab Topic Modeling otomatis pakai yang paling baru dari dataset_final.
""")
    card_close()
    st.stop()

# ============================================================
# DASHBOARD TABS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🧩 Topic Modeling", "🧑‍💼 People Analytics", "🚀 Deployment Analytics"])

# ----------------- Overview -----------------
with tab1:
    card_open("Overview", "Distribusi rating & sentimen dari dataset_final.csv (terpengaruh filter global jika dipakai).")
    colA, colB = st.columns(2, gap="large")

    dist_rating = df_view.groupby("rating").size().reset_index(name="jumlah_ulasan").sort_values("rating")
    dist_sent = df_view.groupby("sentimen").size().reset_index(name="jumlah_ulasan").sort_values("jumlah_ulasan", ascending=False)

    with colA:
        st.markdown("**Distribusi Rating**")
        fig = px.bar(dist_rating, x="rating", y="jumlah_ulasan", template=PX_TEMPLATE)
        fig.update_layout(height=360, xaxis_title="Rating", yaxis_title="Jumlah Ulasan")
        st.plotly_chart(fig, use_container_width=True)

    with colB:
        st.markdown("**Distribusi Sentimen**")
        fig2 = px.pie(dist_sent, names="sentimen", values="jumlah_ulasan", template=PX_TEMPLATE)
        fig2.update_layout(height=360)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    with st.expander("🔍 Preview data (verifikasi dataset terbaru)", expanded=False):
        st.dataframe(df_view.head(40), use_container_width=True)
    card_close()

# ----------------- Topic Modeling (FIX: terbaru) -----------------
with tab2:
    card_open(
        "Topic Modeling (Terbaru)",
        "Prioritas: ambil ringkasan topik dari dataset_final.csv (jika ada kolom top_words/keywords). Jika tidak ada, fallback ke file ringkasan_topik_*.csv."
    )

    # 1) Try build from dataset_final (most recent)
    built = topic_summary_from_dataset(df_std)

    # 2) Fallback read files
    fb_neg = safe_read_csv(TOP_NEG_FALLBACK) if TOP_NEG_FALLBACK.exists() else None
    fb_pos = safe_read_csv(TOP_POS_FALLBACK) if TOP_POS_FALLBACK.exists() else None

    # Choose best source
    use_from_dataset = ("negatif" in built and "positif" in built and
                        built["negatif"] is not None and built["positif"] is not None and
                        (not built["negatif"].empty or not built["positif"].empty))

    if use_from_dataset:
        st.success("✅ Menggunakan ringkasan topik dari dataset_final.csv (paling baru).")
        neg_df = built.get("negatif", pd.DataFrame())
        pos_df = built.get("positif", pd.DataFrame())
        # normalize column names for display
        if not neg_df.empty:
            neg_df = neg_df.rename(columns={"top_words": "top_words"})
        if not pos_df.empty:
            pos_df = pos_df.rename(columns={"top_words": "top_words"})
    else:
        st.warning("⚠️ dataset_final.csv tidak memiliki kolom top_words/keywords. Menggunakan file ringkasan (fallback). Pastikan kamu sudah export ringkasan terbaru dari notebook.")
        neg_df = fb_neg if fb_neg is not None else pd.DataFrame()
        pos_df = fb_pos if fb_pos is not None else pd.DataFrame()

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("### NEGATIF")
        if neg_df is None or neg_df.empty:
            st.error("Data topik NEGATIF tidak tersedia.")
        else:
            st.dataframe(neg_df, use_container_width=True)
            st.download_button(
                "⬇️ Download topik_negatif_terpakai.csv",
                data=neg_df.to_csv(index=False).encode("utf-8"),
                file_name="topik_negatif_terpakai.csv",
                mime="text/csv",
                use_container_width=True
            )

    with c2:
        st.markdown("### POSITIF")
        if pos_df is None or pos_df.empty:
            st.error("Data topik POSITIF tidak tersedia.")
        else:
            st.dataframe(pos_df, use_container_width=True)
            st.download_button(
                "⬇️ Download topik_positif_terpakai.csv",
                data=pos_df.to_csv(index=False).encode("utf-8"),
                file_name="topik_positif_terpakai.csv",
                mime="text/csv",
                use_container_width=True
            )

    card_close()

# ----------------- People Analytics -----------------
with tab3:
    card_open("People Analytics", "Frequency × Impact (rating) → matriks prioritas + exemplars + action mapping (opsional).")

    ctrl1, ctrl2, ctrl3 = st.columns([1.2, 1.0, 1.2], gap="large")
    with ctrl1:
        sent_choice = st.selectbox("Sentimen untuk prioritas", ["negatif","positif"], index=0)
    with ctrl2:
        min_support = st.slider("Minimum support", 5, 300, 20, step=5)
    with ctrl3:
        n_ex = st.slider("Exemplars/topik", 3, 12, 5, step=1)

    topic_summary, df_sent, thr, e = compute_topic_metrics(df_view, sent_choice, min_support=min_support)
    if e:
        st.error(e)
        card_close()
    else:
        freq_thr, rate_thr = thr
        if not topic_map.empty:
            mp = topic_map[topic_map["sentimen"] == sent_choice][["topic_id","label","action"]].copy()
            topic_summary = topic_summary.merge(mp, on="topic_id", how="left")

        st.dataframe(topic_summary, use_container_width=True)

        fig = px.scatter(topic_summary, x="frequency", y="mean_rating", color="priority",
                         hover_data=["topic_id","median_rating"], template=PX_TEMPLATE)
        fig.add_vline(x=freq_thr, line_dash="dash")
        fig.add_hline(y=rate_thr, line_dash="dash")
        fig.update_layout(height=420, xaxis_title="Frequency", yaxis_title="Mean Rating")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
        st.markdown("### Exemplars")
        topic_ids = topic_summary["topic_id"].astype(int).tolist()
        pick_topic = st.selectbox("Pilih topic_id", topic_ids, index=0)

        ex_df = pick_exemplars(df_sent, int(pick_topic), n=n_ex)
        if ex_df.empty:
            st.warning("Tidak ada exemplars untuk topik ini.")
        else:
            ex_disp = ex_df.copy()
            ex_disp["text"] = ex_disp["text"].apply(lambda s: "\n".join(textwrap.wrap(str(s), width=110)))
            st.dataframe(ex_disp, use_container_width=True)

        if "action" in topic_summary.columns:
            row = topic_summary[topic_summary["topic_id"] == int(pick_topic)]
            if not row.empty:
                lbl = row["label"].iloc[0] if "label" in row.columns else ""
                act = row["action"].iloc[0] if "action" in row.columns else ""
                if pd.isna(lbl): lbl = ""
                if pd.isna(act): act = ""
                if str(lbl).strip() or str(act).strip():
                    st.success(f"**Label Topik:** {lbl}")
                    st.write(f"**Rekomendasi Aksi:** {act}")
                else:
                    st.info("Isi topic_label_map.csv untuk menampilkan label & rekomendasi aksi.")

    card_close()

# ----------------- Deployment Analytics -----------------
with tab4:
    card_open("Deployment Analytics", "Upload CSV opsional → analitik dinamis → export CSV.")

    uploaded = st.file_uploader("Upload CSV (opsional). Jika kosong, pakai dataset_final.csv (terfilter).", type=["csv"])
    if uploaded is not None:
        raw = pd.read_csv(uploaded)
        df_live, _, e2 = standardize_dataset(raw)
        if e2:
            st.error(f"CSV upload tidak valid: {e2}")
            df_live = None
        else:
            st.success("✅ Dataset upload dipakai.")
    else:
        df_live = df_view
        st.info("ℹ️ Menggunakan dataset_final.csv (terfilter bila filter aktif).")

    if df_live is None or df_live.empty:
        st.warning("Tidak ada data pada tab ini.")
        card_close()
    else:
        c1, c2 = st.columns([1.2, 1.0], gap="large")
        with c1:
            sent_choice = st.selectbox("Sentimen (Deployment)", ["negatif","positif","netral"], index=0)
        with c2:
            min_support = st.slider("Minimum support (Deployment)", 5, 300, 20, step=5)

        topic_summary, df_sent, thr, e3 = compute_topic_metrics(df_live, sent_choice, min_support=min_support)
        if e3:
            st.error(e3)
            card_close()
        else:
            if not topic_map.empty:
                mp = topic_map[topic_map["sentimen"] == sent_choice][["topic_id","label","action"]].copy()
                topic_summary = topic_summary.merge(mp, on="topic_id", how="left")

            st.dataframe(topic_summary, use_container_width=True)

            topic_ids = topic_summary["topic_id"].astype(int).tolist()
            pick_topic = st.selectbox("Pilih topic_id (Deployment)", topic_ids, index=0)
            ex_df = pick_exemplars(df_sent, int(pick_topic), n=5)
            if not ex_df.empty:
                ex_disp = ex_df.copy()
                ex_disp["text"] = ex_disp["text"].apply(lambda s: "\n".join(textwrap.wrap(str(s), width=110)))
                st.dataframe(ex_disp, use_container_width=True)

            st.download_button(
                "⬇️ Download prioritas_masalah.csv",
                data=topic_summary.to_csv(index=False).encode("utf-8"),
                file_name="prioritas_masalah.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.download_button(
                "⬇️ Download exemplars_topik.csv",
                data=ex_df.to_csv(index=False).encode("utf-8"),
                file_name="exemplars_topik.csv",
                mime="text/csv",
                use_container_width=True
            )

    card_close()

# Footer
st.caption(f"© {datetime.now().year} • Build: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • UI bright + black font • Access restricted.")
