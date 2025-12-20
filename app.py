import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from datetime import datetime
import textwrap
import glob

# ============================================================
# 0) PAGE CONFIG
# ============================================================
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

PX_TEMPLATE = "plotly_white"

# ============================================================
# 1) AUTH (LOGIN WAJIB USER+PASS)
#    - Disarankan taruh credential di Streamlit Secrets:
#      [auth]
#      admin="admin123"
#      reagen="siga2025"
# ============================================================
def load_users():
    # Prefer secrets (lebih aman)
    try:
        if "auth" in st.secrets:
            d = dict(st.secrets["auth"])
            return {k: str(v) for k, v in d.items()}
    except Exception:
        pass
    # Fallback hardcode (kalau secrets belum diset)
    return {
        "admin": "admin123",
        "reagen": "siga2025",
    }

USERS = load_users()

def auth_ok(username: str, password: str) -> bool:
    return USERS.get(username, None) == password

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ============================================================
# 2) FORCE BRIGHT UI + CSS (cerah, font hitam, tidak nabrak)
# ============================================================
st.markdown("""
<script>
try { window.parent.document.documentElement.setAttribute("data-theme", "light"); } catch(e) {}
</script>
""", unsafe_allow_html=True)

st.markdown("""
<style>
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

.stTabs [data-baseweb="tab-list"]{ gap: 8px; margin-top: 6px; }
.stTabs [data-baseweb="tab"]{
  background: rgba(255,255,255,0.70) !important;
  border: 1px solid rgba(15,23,42,0.10) !important;
  border-radius: 999px !important;
  padding: 8px 12px !important;
  font-weight: 900 !important;
}
.stTabs [aria-selected="true"]{
  background: #FFFFFF !important;
  border: 1px solid rgba(37,99,235,0.35) !important;
}

/* Dataframe */
[data-testid="stDataFrame"]{
  border-radius: 14px; overflow: hidden;
  border: 1px solid rgba(15,23,42,0.10);
}

/* Sidebar buttons */
div[data-testid="stSidebar"] button{
  border-radius: 14px !important;
  font-weight: 900 !important;
}

/* Logout style */
.logout-wrap button{
  background: linear-gradient(135deg, rgba(16,185,129,0.18), rgba(59,130,246,0.14)) !important;
  border: 1px solid rgba(16,185,129,0.35) !important;
}
.logout-wrap button:hover{
  background: linear-gradient(135deg, rgba(16,185,129,0.25), rgba(59,130,246,0.20)) !important;
}

/* Inputs */
input, textarea, [data-baseweb="select"]{ background: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3) HELPERS
# ============================================================
def show_logo(path: Path, width: int = 175):
    if path.exists():
        st.image(str(path), width=width)
    else:
        st.warning(f"Logo tidak ditemukan: {path.name} (pastikan sefolder app.py)")

def card_open(title: str, subtitle: str = ""):
    st.markdown(f"""<div class="card"><div class="card-title">{title}</div><div class="card-sub">{subtitle}</div>""",
                unsafe_allow_html=True)

def card_close():
    st.markdown("</div>", unsafe_allow_html=True)

def nice_number(x):
    try:
        return f"{int(x):,}"
    except Exception:
        return str(x)

def safe_read_csv(path: Path) -> pd.DataFrame | None:
    try:
        if path and path.exists():
            return pd.read_csv(path)
        return None
    except Exception as e:
        st.error(f"Gagal membaca {path.name}: {e}")
        return None

def pick_latest(patterns: list[str]) -> Path | None:
    """
    Ambil file terbaru berdasarkan modified time untuk menghindari 'pakai file lama'
    Contoh patterns: ["ringkasan_topik_negatif*.csv", "ringkasan_topik_neg*.csv"]
    """
    found = []
    for pat in patterns:
        found += glob.glob(str(DATA / pat))
    if not found:
        return None
    found_paths = [Path(x) for x in found]
    found_paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return found_paths[0]

def file_info(p: Path | None) -> str:
    if p is None:
        return "❌ tidak ada"
    ts = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    return f"✅ {p.name} (modified: {ts})"

# ============================================================
# 4) CORE DATA STANDARDIZATION (core tetap)
# ============================================================
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

def detect_schema(df: pd.DataFrame) -> dict:
    sent_col  = coalesce_col(df, ["sentimen","sentiment","label_sentimen","label"])
    topic_col = coalesce_col(df, ["topic_id","topic","topik","dominant_topic","dom_topic"])
    rating_col= coalesce_col(df, ["rating","rate","score","bintang","stars"])
    text_col  = coalesce_col(df, ["text","ulasan","review","komentar","steming_data"])
    return {"sent_col": sent_col, "topic_col": topic_col, "rating_col": rating_col, "text_col": text_col}

def standardize_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict, str | None]:
    schema = detect_schema(df)
    miss = [k for k, v in schema.items() if v is None]
    if miss:
        return df, schema, f"Kolom wajib tidak ditemukan: {', '.join(miss)}"

    tmp = df.copy()
    tmp[schema["sent_col"]] = tmp[schema["sent_col"]].apply(normalize_sentiment)
    tmp[schema["rating_col"]] = pd.to_numeric(tmp[schema["rating_col"]], errors="coerce")
    tmp[schema["topic_col"]] = pd.to_numeric(tmp[schema["topic_col"]], errors="coerce")
    tmp = tmp.dropna(subset=[schema["rating_col"], schema["topic_col"]]).copy()

    out = pd.DataFrame({
        "sentimen": tmp[schema["sent_col"]].astype(str).str.lower().str.strip(),
        "topic_id": tmp[schema["topic_col"]].astype(int),
        "rating": tmp[schema["rating_col"]].astype(float),
        "text": tmp[schema["text_col"]].astype(str),
    })
    return out, schema, None

@st.cache_data(show_spinner=False)
def load_dataset(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_topic_map(path: Path) -> pd.DataFrame:
    mp = pd.read_csv(path)
    mp["sentimen"] = mp["sentimen"].astype(str).str.lower().str.strip()
    mp["topic_id"] = pd.to_numeric(mp["topic_id"], errors="coerce")
    mp = mp.dropna(subset=["topic_id"]).copy()
    mp["topic_id"] = mp["topic_id"].astype(int)
    for c in ["label","action"]:
        if c not in mp.columns:
            mp[c] = ""
    return mp[["sentimen","topic_id","label","action"]]

def compute_priority(df_std: pd.DataFrame, sent: str, min_support: int = 20):
    tmp = df_std[df_std["sentimen"] == sent].copy()
    if tmp.empty:
        return None, None, None, "Data kosong untuk sentimen ini."

    summ = (tmp.groupby("topic_id")
              .agg(frequency=("topic_id","size"),
                   mean_rating=("rating","mean"),
                   median_rating=("rating","median"))
              .reset_index())

    summ = summ[summ["frequency"] >= min_support].copy()
    if summ.empty:
        return None, None, None, f"Tidak ada topik dengan support >= {min_support}"

    freq_thr = float(summ["frequency"].median())
    rate_thr = float(summ["mean_rating"].median())

    def pri(r):
        hf = r["frequency"] >= freq_thr
        lr = r["mean_rating"] <= rate_thr
        if hf and lr: return "P1 (Prioritas Tinggi)"
        if hf or lr:  return "P2 (Prioritas Sedang)"
        return "P3 (Prioritas Rendah)"

    summ["priority"] = summ.apply(pri, axis=1)
    summ = summ.sort_values(["priority","frequency"], ascending=[True, False])
    return summ, tmp, (freq_thr, rate_thr), None

def exemplars(df_sent: pd.DataFrame, topic_id: int, n: int = 5):
    sub = df_sent[df_sent["topic_id"] == topic_id].drop_duplicates("text").copy()
    if sub.empty:
        return sub
    sub["len"] = sub["text"].astype(str).str.len()
    sub = sub.sort_values(["len","rating"], ascending=[False, True]).head(n)
    return sub[["topic_id","rating","text"]]

# ============================================================
# 5) LOGIN PAGE (restricted)
# ============================================================
def login_page():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.35, 4.3, 1.35], vertical_alignment="center")
    with c1:
        show_logo(LOGO_UPN, 170)
    with c2:
        st.markdown('<div class="hero-title">Dashboard Analitik Media Sosial Berbasis Rating Aplikasi SIGA</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Akses dibatasi. Login dengan username & password.</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div class="badges">
          <span class="badge">🔒 Restricted Access</span>
          <span class="badge">📊 Medsos + People Analytics</span>
          <span class="badge">🚀 Streamlit Deployment</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        show_logo(LOGO_BKKBN, 170)
    st.markdown("</div>", unsafe_allow_html=True)

    card_open("Login", "Masukkan kredensial yang valid.")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("🔑 Login", use_container_width=True):
        if auth_ok(u, p):
            st.session_state.logged_in = True
            st.session_state.username = u
            st.rerun()
        else:
            st.error("Username / password salah.")
    card_close()

# Gate
if not st.session_state.logged_in:
    login_page()
    st.stop()

# ============================================================
# 6) LOAD REQUIRED DATA
# ============================================================
if not DATASET_FINAL.exists():
    st.error("File wajib tidak ditemukan: data/dataset_final.csv")
    st.stop()

df_raw = load_dataset(DATASET_FINAL)
df_std, schema, err = standardize_dataset(df_raw)
if err:
    st.error(f"dataset_final.csv invalid: {err}")
    st.info(f"Skema terdeteksi: {schema}")
    st.stop()

# Latest export files (avoid old)
p_top_neg = pick_latest(["ringkasan_topik_negatif*.csv", "topik_negatif*.csv"])
p_top_pos = pick_latest(["ringkasan_topik_positif*.csv", "topik_positif*.csv"])
p_topic_map = pick_latest(["topic_label_map*.csv"])
p_people_priority = pick_latest(["people_priority*.csv", "people_analytics_prioritas*.csv"])
p_exemplars = pick_latest(["topic_exemplars*.csv", "exemplars_topik*.csv", "exemplars_topic*.csv"])

top_neg = safe_read_csv(p_top_neg) if p_top_neg else None
top_pos = safe_read_csv(p_top_pos) if p_top_pos else None
topic_map = load_topic_map(p_topic_map) if p_topic_map else pd.DataFrame()
people_priority = safe_read_csv(p_people_priority) if p_people_priority else None
exemplars_file = safe_read_csv(p_exemplars) if p_exemplars else None

# ============================================================
# 7) SIDEBAR (logout + filters + file status)
# ============================================================
with st.sidebar:
    st.markdown("## 🎛️ Kontrol & Navigasi")
    st.caption(f"Login sebagai: **{st.session_state.username}**")

    st.markdown('<div class="logout-wrap">', unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.markdown("### 📁 Export yang sedang dipakai")
    st.write(f"dataset_final: ✅ {DATASET_FINAL.name}")
    st.write(f"top_neg: {file_info(p_top_neg)}")
    st.write(f"top_pos: {file_info(p_top_pos)}")
    st.write(f"topic_label_map: {file_info(p_topic_map)}")
    st.write(f"people_priority: {file_info(p_people_priority)}")
    st.write(f"topic_exemplars: {file_info(p_exemplars)}")

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

# ============================================================
# 8) HERO + KPI
# ============================================================
st.markdown('<div class="hero">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1.35, 4.3, 1.35], vertical_alignment="center")
with c1:
    show_logo(LOGO_UPN, 175)
with c2:
    st.markdown('<div class="hero-title">Dashboard Analitik Media Sosial Berbasis Rating Aplikasi SIGA</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Cerah, kontras aman, dan konsisten untuk presentasi + laporan akademik.</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="badges">
      <span class="badge">🎓 UPN</span>
      <span class="badge">🏛️ BKKBN Jawa Timur</span>
      <span class="badge">📊 Analitik Medsos</span>
      <span class="badge">🧑‍💼 People Analytics</span>
      <span class="badge">🚀 Deployment</span>
    </div>
    """, unsafe_allow_html=True)
with c3:
    show_logo(LOGO_BKKBN, 175)
st.markdown("</div>", unsafe_allow_html=True)

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
# 9) TABS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🧩 Topic Modeling (Export)", "🧑‍💼 People Analytics", "🚀 Deployment Analytics"])

# ------------------------------------------------------------
# TAB 1: Overview
# ------------------------------------------------------------
with tab1:
    card_open("Overview", "Distribusi rating & sentimen. Ini dasar untuk narasi pembuka presentasi.")
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

    st.markdown("### Insight cepat (auto)")
    if total_data > 0:
        st.write(f"- Total ulasan: **{nice_number(total_data)}**")
        st.write(f"- Rata-rata rating: **{avg_rating:.2f}**")
        st.write(f"- Sentimen negatif: **{neg_pct:.2f}%** | positif: **{pos_pct:.2f}%**")
        if neg_pct >= 60:
            st.info("Dominasi negatif tinggi → fokus People Analytics pada topik P1 untuk prioritas perbaikan.")
    else:
        st.warning("Data kosong setelah filter.")

    with st.expander("🔍 Preview dataset (validasi data terbaru)", expanded=False):
        st.dataframe(df_view.head(50), use_container_width=True)

    card_close()

# ------------------------------------------------------------
# TAB 2: Topic Modeling (pakai export terbaru)
# ------------------------------------------------------------
with tab2:
    card_open(
        "Topic Modeling (menggunakan file export terbaru)",
        "Tab ini sengaja membaca file export terbaru agar konsisten dengan notebook & laporan. Tidak hitung LDA ulang di Streamlit."
    )

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("### Topik NEGATIF (Export)")
        if top_neg is None or top_neg.empty:
            st.error("File topik negatif tidak ditemukan / kosong. Pastikan export ringkasan_topik_negatif*.csv ke folder data/.")
        else:
            st.caption(f"Terpakai: {p_top_neg.name}")
            st.dataframe(top_neg, use_container_width=True)

            # visual: jumlah ulasan per topic jika kolom tersedia
            col_topic = None
            for cand in ["topic_id","topic","topik"]:
                if cand in top_neg.columns:
                    col_topic = cand
                    break
            col_jml = None
            for cand in ["jumlah_ulasan","count","freq","frequency"]:
                if cand in top_neg.columns:
                    col_jml = cand
                    break

            if col_topic and col_jml:
                fig = px.bar(top_neg, x=col_topic, y=col_jml, template=PX_TEMPLATE)
                fig.update_layout(height=320, xaxis_title="Topic", yaxis_title="Jumlah Ulasan")
                st.plotly_chart(fig, use_container_width=True)

            st.download_button(
                "⬇️ Download topik_negatif_terpakai.csv",
                data=top_neg.to_csv(index=False).encode("utf-8"),
                file_name="topik_negatif_terpakai.csv",
                mime="text/csv",
                use_container_width=True
            )

    with c2:
        st.markdown("### Topik POSITIF (Export)")
        if top_pos is None or top_pos.empty:
            st.error("File topik positif tidak ditemukan / kosong. Pastikan export ringkasan_topik_positif*.csv ke folder data/.")
        else:
            st.caption(f"Terpakai: {p_top_pos.name}")
            st.dataframe(top_pos, use_container_width=True)

            col_topic = None
            for cand in ["topic_id","topic","topik"]:
                if cand in top_pos.columns:
                    col_topic = cand
                    break
            col_jml = None
            for cand in ["jumlah_ulasan","count","freq","frequency"]:
                if cand in top_pos.columns:
                    col_jml = cand
                    break

            if col_topic and col_jml:
                fig = px.bar(top_pos, x=col_topic, y=col_jml, template=PX_TEMPLATE)
                fig.update_layout(height=320, xaxis_title="Topic", yaxis_title="Jumlah Ulasan")
                st.plotly_chart(fig, use_container_width=True)

            st.download_button(
                "⬇️ Download topik_positif_terpakai.csv",
                data=top_pos.to_csv(index=False).encode("utf-8"),
                file_name="topik_positif_terpakai.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.info("Jika ada banyak file versi lama, app otomatis memilih file terbaru berdasarkan modified time. Jadi tidak akan keambil yang lama lagi.")
    card_close()

# ------------------------------------------------------------
# TAB 3: People Analytics (pakai export bila tersedia, fallback hitung)
# ------------------------------------------------------------
with tab3:
    card_open(
        "People Analytics",
        "Prioritas masalah (frequency × impact) + label & rekomendasi aksi + contoh ulasan (exemplars)."
    )

    ctrl1, ctrl2, ctrl3 = st.columns([1.2, 1.0, 1.2], gap="large")
    with ctrl1:
        sent_choice = st.selectbox("Sentimen", ["negatif","positif"], index=0)
    with ctrl2:
        min_support = st.slider("Minimum support", 5, 300, 20, step=5)
    with ctrl3:
        n_ex = st.slider("Jumlah exemplars/topik", 3, 12, 5)

    # 1) PRIORITY: pakai export kalau ada dan cocok
    use_export_priority = False
    if people_priority is not None and not people_priority.empty and "sentimen" in people_priority.columns:
        use_export_priority = True

    if use_export_priority:
        st.success(f"✅ Menggunakan export prioritas: {p_people_priority.name}")
        pri_df = people_priority.copy()
        pri_df["sentimen"] = pri_df["sentimen"].astype(str).str.lower().str.strip()
        pri_df = pri_df[pri_df["sentimen"] == sent_choice].copy()

        # pastikan topic_id int
        if "topic_id" in pri_df.columns:
            pri_df["topic_id"] = pd.to_numeric(pri_df["topic_id"], errors="coerce")
            pri_df = pri_df.dropna(subset=["topic_id"])
            pri_df["topic_id"] = pri_df["topic_id"].astype(int)

        # fallback filter min_support jika kolom frequency ada
        if "frequency" in pri_df.columns:
            pri_df = pri_df[pri_df["frequency"] >= min_support].copy()

        df_sent = df_view[df_view["sentimen"] == sent_choice].copy()
        thr = None
    else:
        st.warning("⚠️ Export people_priority belum ada. App menghitung prioritas dari dataset_final (fallback).")
        pri_df, df_sent, thr, e = compute_priority(df_view, sent_choice, min_support=min_support)
        if e:
            st.error(e)
            card_close()
            st.stop()

    # 2) Merge label/action kalau mapping ada
    if not topic_map.empty:
        mp = topic_map[topic_map["sentimen"] == sent_choice][["topic_id","label","action"]].copy()
        pri_df = pri_df.merge(mp, on="topic_id", how="left")

    st.dataframe(pri_df, use_container_width=True)

    # 3) Scatter matrix (kalau punya frequency & mean_rating)
    if "frequency" in pri_df.columns and "mean_rating" in pri_df.columns:
        fig = px.scatter(
            pri_df,
            x="frequency",
            y="mean_rating",
            color="priority" if "priority" in pri_df.columns else None,
            hover_data=["topic_id"],
            template=PX_TEMPLATE
        )
        fig.update_layout(height=420, xaxis_title="Frequency", yaxis_title="Mean Rating")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # 4) Exemplars: pakai export jika ada, fallback hitung
    st.markdown("### Exemplars (contoh ulasan representatif per topik)")
    if "topic_id" not in pri_df.columns or pri_df.empty:
        st.warning("Tidak ada topik untuk dipilih.")
        card_close()
        st.stop()

    topic_ids = pri_df["topic_id"].astype(int).unique().tolist()
    pick_topic = st.selectbox("Pilih topic_id", topic_ids, index=0)

    use_export_ex = False
    if exemplars_file is not None and not exemplars_file.empty:
        cols = set([c.lower() for c in exemplars_file.columns])
        if {"sentimen","topic_id","rating","text"}.issubset(cols):
            use_export_ex = True

    if use_export_ex:
        st.success(f"✅ Menggunakan export exemplars: {p_exemplars.name}")
        ex = exemplars_file.copy()
        ex.columns = [c.lower() for c in ex.columns]
        ex["sentimen"] = ex["sentimen"].astype(str).str.lower().str.strip()
        ex["topic_id"] = pd.to_numeric(ex["topic_id"], errors="coerce")
        ex = ex.dropna(subset=["topic_id"])
        ex["topic_id"] = ex["topic_id"].astype(int)
        ex = ex[(ex["sentimen"] == sent_choice) & (ex["topic_id"] == int(pick_topic))].copy()
        ex = ex.head(n_ex)
        ex = ex[["topic_id","rating","text"]]
    else:
        st.warning("⚠️ Export exemplars belum ada. App memilih exemplars dari dataset_final (fallback).")
        ex = exemplars(df_sent, int(pick_topic), n=n_ex)

    if ex is None or ex.empty:
        st.warning("Tidak ada exemplars untuk topik ini.")
    else:
        ex_disp = ex.copy()
        ex_disp["text"] = ex_disp["text"].apply(lambda s: "\n".join(textwrap.wrap(str(s), width=110)))
        st.dataframe(ex_disp, use_container_width=True)

    # 5) Show action suggestion if exists
    if "action" in pri_df.columns:
        row = pri_df[pri_df["topic_id"] == int(pick_topic)]
        if not row.empty:
            lbl = row["label"].iloc[0] if "label" in row.columns else ""
            act = row["action"].iloc[0] if "action" in row.columns else ""
            lbl = "" if pd.isna(lbl) else str(lbl)
            act = "" if pd.isna(act) else str(act)
            if lbl.strip() or act.strip():
                st.success(f"**Label Topik:** {lbl}")
                st.write(f"**Rekomendasi Aksi:** {act}")
            else:
                st.info("Isi topic_label_map.csv untuk menampilkan label & rekomendasi aksi.")

    # Exports from app view
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.markdown("### Export untuk laporan (dari hasil yang sedang tampil)")
    st.download_button(
        "⬇️ Download prioritas_tampil.csv",
        data=pri_df.to_csv(index=False).encode("utf-8"),
        file_name="prioritas_tampil.csv",
        mime="text/csv",
        use_container_width=True
    )
    st.download_button(
        "⬇️ Download exemplars_tampil.csv",
        data=ex.to_csv(index=False).encode("utf-8"),
        file_name="exemplars_tampil.csv",
        mime="text/csv",
        use_container_width=True
    )

    card_close()

# ------------------------------------------------------------
# TAB 4: Deployment Analytics (upload CSV opsional)
# ------------------------------------------------------------
with tab4:
    card_open("Deployment Analytics", "Bukti end-to-end: upload → proses → output → export. Ini menguatkan mata kuliah deployment aplikasi.")

    uploaded = st.file_uploader("Upload CSV (opsional). Jika kosong, pakai dataset_final (terfilter).", type=["csv"])
    if uploaded is not None:
        try:
            raw = pd.read_csv(uploaded)
            df_live, _, e2 = standardize_dataset(raw)
            if e2:
                st.error(f"CSV upload tidak valid: {e2}")
                df_live = None
            else:
                st.success("✅ Dataset upload dipakai.")
        except Exception as e:
            st.error(f"Gagal membaca CSV upload: {e}")
            df_live = None
    else:
        df_live = df_view
        st.info("ℹ️ Menggunakan dataset_final (terfilter bila filter aktif).")

    if df_live is None or df_live.empty:
        st.warning("Tidak ada data untuk dianalisis.")
        card_close()
    else:
        sent_choice = st.selectbox("Sentimen (Deployment)", ["negatif","positif","netral"], index=0)
        min_support = st.slider("Minimum support (Deployment)", 5, 300, 20, step=5)

        pri_df, df_sent, thr, e = compute_priority(df_live, sent_choice, min_support=min_support)
        if e:
            st.error(e)
            card_close()
        else:
            if not topic_map.empty:
                mp = topic_map[topic_map["sentimen"] == sent_choice][["topic_id","label","action"]].copy()
                pri_df = pri_df.merge(mp, on="topic_id", how="left")

            st.dataframe(pri_df, use_container_width=True)

            topic_ids = pri_df["topic_id"].astype(int).tolist()
            pick_topic = st.selectbox("Pilih topic_id (Deployment)", topic_ids, index=0)
            ex = exemplars(df_sent, int(pick_topic), n=5)
            if not ex.empty:
                ex_disp = ex.copy()
                ex_disp["text"] = ex_disp["text"].apply(lambda s: "\n".join(textwrap.wrap(str(s), width=110)))
                st.dataframe(ex_disp, use_container_width=True)

            st.download_button(
                "⬇️ Download prioritas_masalah.csv",
                data=pri_df.to_csv(index=False).encode("utf-8"),
                file_name="prioritas_masalah.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.download_button(
                "⬇️ Download exemplars_topik.csv",
                data=ex.to_csv(index=False).encode("utf-8"),
                file_name="exemplars_topik.csv",
                mime="text/csv",
                use_container_width=True
            )

    card_close()

# Footer
st.caption(f"© {datetime.now().year} • Build: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • UI bright + restricted login • Export-first deployment.")
