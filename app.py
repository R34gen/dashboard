import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from datetime import datetime
import textwrap

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

# assets
LOGO_UPN = ROOT / "logo_upn.png"
LOGO_BKKBN = ROOT / "logo_bkkbn.png"

# required master
DATASET_FINAL = DATA / "dataset_final.csv"

# exports you uploaded (topic modeling)
NEG_TOPICS = DATA / "neg_topics.csv"
POS_TOPICS = DATA / "pos_topics.csv"
NEG_SUPPORT = DATA / "neg_support.csv"
POS_SUPPORT = DATA / "pos_support.csv"
NEG_EXEMPLARS = DATA / "neg_exemplars.csv"
POS_EXEMPLARS = DATA / "pos_exemplars.csv"
NEG_EVAL = DATA / "neg_eval.csv"
POS_EVAL = DATA / "pos_eval.csv"
SUMMARY_COUNTS = DATA / "summary_counts.csv"

# people analytics export
NEG_ACTION = DATA / "neg_action.csv"

# optional: recommended extra files (if you add later)
TOPIC_LABEL_MAP = DATA / "topic_label_map.csv"   # recommended (manual labels/actions)
RATING_COUNTS = DATA / "rating_counts.csv"       # recommended (rating distribution export)

PX_TEMPLATE = "plotly_white"

# ============================================================
# 1) AUTH (LOGIN WAJIB USER+PASS)
#    - Prefer secrets: Streamlit Cloud -> Settings -> Secrets
#      [auth]
#      admin="admin123"
#      reagen="siga2025"
# ============================================================
def load_users():
    try:
        if "auth" in st.secrets:
            d = dict(st.secrets["auth"])
            return {k: str(v) for k, v in d.items()}
    except Exception:
        pass
    return {
        "admin": "admin123",
        "reagen": "siga2025"
    }

USERS = load_users()

def auth_ok(username: str, password: str) -> bool:
    return USERS.get(username, None) == password

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ============================================================
# 2) FORCE BRIGHT UI + CSS (lebih profesional)
# ============================================================
st.markdown("""
<script>
try { window.parent.document.documentElement.setAttribute("data-theme", "light"); } catch(e) {}
</script>
""", unsafe_allow_html=True)

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg, #F7FBFF 0%, #EEF5FF 100%) !important;
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
  background: linear-gradient(135deg, rgba(37,99,235,0.18), rgba(99,102,241,0.12)) !important;
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
  background: rgba(255,255,255,0.80);
  font-size: 12px; font-weight: 800;
}

.card{
  background: #FFFFFF !important;
  border: 1px solid rgba(15,23,42,0.10) !important;
  border-radius: 18px;
  padding: 16px 16px 14px 16px;
  box-shadow: 0 10px 24px rgba(2,6,23,0.08) !important;
  margin-bottom: 14px;
}
.card-title{ font-size: 18px; font-weight: 950; margin: 0; }
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
.kpi-k{ font-size: 12px; font-weight: 900; color: #334155 !important; }
.kpi-v{ font-size: 26px; font-weight: 980; margin-top: 6px; }
.kpi-note{
  display:inline-block; margin-top: 8px; padding: 3px 8px; border-radius: 999px;
  border: 1px solid rgba(15,23,42,0.12);
  background: rgba(236,243,255,0.70);
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

[data-testid="stDataFrame"]{
  border-radius: 14px; overflow: hidden;
  border: 1px solid rgba(15,23,42,0.10);
}

div[data-testid="stSidebar"] button{
  border-radius: 14px !important;
  font-weight: 950 !important;
}

/* Logout button: hijau-biru lembut (tidak gelap seperti screenshot kamu) */
.logout-wrap button{
  background: linear-gradient(135deg, rgba(16,185,129,0.18), rgba(59,130,246,0.14)) !important;
  border: 1px solid rgba(16,185,129,0.35) !important;
}
.logout-wrap button:hover{
  background: linear-gradient(135deg, rgba(16,185,129,0.28), rgba(59,130,246,0.22)) !important;
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
    st.markdown(
        f"""<div class="card"><div class="card-title">{title}</div><div class="card-sub">{subtitle}</div>""",
        unsafe_allow_html=True
    )

def card_close():
    st.markdown("</div>", unsafe_allow_html=True)

def nice_number(x):
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

def file_ok(p: Path) -> bool:
    return p.exists()

def file_status_line(p: Path, required=False) -> str:
    if p.exists():
        ts = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        return f"✅ {p.name} (modified {ts})"
    return f"{'❌' if required else '⚠️'} {p.name} (tidak ditemukan)"

def wrap_text(s: str, width=110) -> str:
    return "\n".join(textwrap.wrap(str(s), width=width))

# ============================================================
# 4) CORE STANDARDIZATION (dataset_final)
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

def standardize_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict, str | None]:
    sent_col  = coalesce_col(df, ["sentimen","sentiment","label_sentimen","label"])
    topic_col = coalesce_col(df, ["topic_id","topic","topik","dominant_topic","dom_topic"])
    rating_col= coalesce_col(df, ["rating","rate","score","bintang","stars"])
    text_col  = coalesce_col(df, ["text","ulasan","review","komentar","steming_data"])

    schema = {"sent_col": sent_col, "topic_col": topic_col, "rating_col": rating_col, "text_col": text_col}
    if any(v is None for v in schema.values()):
        miss = [k for k, v in schema.items() if v is None]
        return df, schema, f"Kolom wajib tidak ditemukan: {', '.join(miss)}"

    tmp = df.copy()
    tmp[sent_col] = tmp[sent_col].apply(normalize_sentiment)
    tmp[rating_col] = pd.to_numeric(tmp[rating_col], errors="coerce")
    tmp[topic_col] = pd.to_numeric(tmp[topic_col], errors="coerce")
    tmp = tmp.dropna(subset=[rating_col, topic_col]).copy()

    out = pd.DataFrame({
        "sentimen": tmp[sent_col].astype(str).str.lower().str.strip(),
        "topic_id": tmp[topic_col].astype(int),
        "rating": tmp[rating_col].astype(float),
        "text": tmp[text_col].astype(str),
    })
    return out, schema, None

@st.cache_data(show_spinner=False)
def load_dataset_final(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

# ============================================================
# 5) LOGIN PAGE
# ============================================================
def login_page():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.35, 4.3, 1.35], vertical_alignment="center")
    with c1:
        show_logo(LOGO_UPN, 170)
    with c2:
        st.markdown('<div class="hero-title">Dashboard Analitik Media Sosial Berbasis Rating Aplikasi SIGA</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Akses dibatasi. Login dengan username & password.</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="badges">
          <span class="badge">🔒 Restricted Login</span>
          <span class="badge">📊 Medsos + People Analytics</span>
          <span class="badge">🚀 Streamlit Deployment</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        show_logo(LOGO_BKKBN, 170)
    st.markdown("</div>", unsafe_allow_html=True)

    card_open("Login", "Masukkan kredensial yang valid (user+password).")
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

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ============================================================
# 6) LOAD FILES (dataset_final + exports)
# ============================================================
if not DATASET_FINAL.exists():
    st.error("File wajib tidak ditemukan: data/dataset_final.csv")
    st.stop()

df_raw = load_dataset_final(DATASET_FINAL)
df_std, schema, err = standardize_dataset(df_raw)
if err:
    st.error(f"dataset_final.csv invalid: {err}")
    st.info(f"Skema terdeteksi: {schema}")
    st.stop()

# exports
neg_topics = safe_read_csv(NEG_TOPICS)
pos_topics = safe_read_csv(POS_TOPICS)
neg_support = safe_read_csv(NEG_SUPPORT)
pos_support = safe_read_csv(POS_SUPPORT)
neg_ex = safe_read_csv(NEG_EXEMPLARS)
pos_ex = safe_read_csv(POS_EXEMPLARS)
neg_eval = safe_read_csv(NEG_EVAL)
pos_eval = safe_read_csv(POS_EVAL)
summary_counts = safe_read_csv(SUMMARY_COUNTS)
neg_action = safe_read_csv(NEG_ACTION)

# optional
topic_label_map = safe_read_csv(TOPIC_LABEL_MAP)
rating_counts = safe_read_csv(RATING_COUNTS)

# ============================================================
# 7) SIDEBAR (logout + file status + global filters)
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
    st.markdown("### 📁 Status File (data/)")
    st.write(file_status_line(DATASET_FINAL, required=True))
    st.write(file_status_line(SUMMARY_COUNTS, required=True))
    st.write(file_status_line(NEG_TOPICS))
    st.write(file_status_line(POS_TOPICS))
    st.write(file_status_line(NEG_SUPPORT))
    st.write(file_status_line(POS_SUPPORT))
    st.write(file_status_line(NEG_EXEMPLARS))
    st.write(file_status_line(POS_EXEMPLARS))
    st.write(file_status_line(NEG_EVAL))
    st.write(file_status_line(POS_EVAL))
    st.write(file_status_line(NEG_ACTION))
    st.write(file_status_line(TOPIC_LABEL_MAP))
    st.write(file_status_line(RATING_COUNTS))

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
    st.markdown('<div class="hero-title">Dashboard Analitik Media Sosial Berbasis Rating Aplikasi SIGA</div>', unsafe_allow_html=True)
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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🧩 Topic Modeling (Export)",
    "🧑‍💼 People Analytics (Prioritas & Aksi)",
    "🧪 Model Quality (Coherence/Perplexity)",
    "🚀 Deployment (Upload & Export)"
])

# ------------------------------------------------------------
# TAB 1: OVERVIEW
# ------------------------------------------------------------
with tab1:
    card_open("Overview", "Ringkasan dataset + distribusi rating + distribusi sentimen.")

    # Sentiment counts: prefer summary_counts.csv if exists
    if summary_counts is not None and not summary_counts.empty and set(["sentimen","jumlah"]).issubset(summary_counts.columns):
        sc = summary_counts.copy()
        sc["sentimen"] = sc["sentimen"].astype(str).str.lower().str.strip()
        st.markdown("### Ringkasan jumlah ulasan per sentimen (export)")
        st.dataframe(sc, use_container_width=True)
        fig_sc = px.bar(sc, x="sentimen", y="jumlah", template=PX_TEMPLATE)
        fig_sc.update_layout(height=280, xaxis_title="Sentimen", yaxis_title="Jumlah")
        st.plotly_chart(fig_sc, use_container_width=True)
    else:
        st.warning("summary_counts.csv tidak tersedia / format tidak sesuai. Menghitung dari dataset_final.")
        sc = df_std.groupby("sentimen").size().reset_index(name="jumlah").sort_values("jumlah", ascending=False)
        st.dataframe(sc, use_container_width=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Rating distribution: prefer rating_counts.csv if later added
    st.markdown("### Distribusi rating")
    if rating_counts is not None and not rating_counts.empty and set(["rating","jumlah"]).issubset(rating_counts.columns):
        rc = rating_counts.copy()
        rc["rating"] = pd.to_numeric(rc["rating"], errors="coerce")
        rc["jumlah"] = pd.to_numeric(rc["jumlah"], errors="coerce")
        rc = rc.dropna().sort_values("rating")
        st.caption("Sumber: rating_counts.csv (export, disarankan untuk konsistensi laporan)")
    else:
        rc = df_view.groupby("rating").size().reset_index(name="jumlah").sort_values("rating")
        st.caption("Sumber: dataset_final.csv (computed)")
    fig_rc = px.bar(rc, x="rating", y="jumlah", template=PX_TEMPLATE)
    fig_rc.update_layout(height=320, xaxis_title="Rating", yaxis_title="Jumlah Ulasan")
    st.plotly_chart(fig_rc, use_container_width=True)

    with st.expander("🔍 Preview dataset_final (validasi data terbaru)", expanded=False):
        st.dataframe(df_view.head(60), use_container_width=True)

    card_close()

# ------------------------------------------------------------
# TAB 2: TOPIC MODELING (EXPORT-FIRST)
# ------------------------------------------------------------
with tab2:
    card_open(
        "Topic Modeling (Export)",
        "Menampilkan topik POSITIF vs NEGATIF dari file export kamu (tidak menghitung ulang LDA di Streamlit)."
    )

    left, right = st.columns(2, gap="large")

    # NEGATIVE topics
    with left:
        st.markdown("### NEGATIF — Topik & Kata Kunci")
        if neg_topics is None or neg_topics.empty:
            st.error("neg_topics.csv tidak ditemukan / kosong.")
        else:
            st.dataframe(neg_topics, use_container_width=True)
            if "topic" in neg_topics.columns:
                # Try to join with support if available
                if neg_support is not None and not neg_support.empty and "topic" in neg_support.columns:
                    join = neg_topics.merge(neg_support, on="topic", how="left")
                else:
                    join = neg_topics.copy()

                # Visual: valid_docs if exists, else just show nothing
                if "valid_docs" in join.columns:
                    fig = px.bar(join.sort_values("valid_docs", ascending=False), x="topic", y="valid_docs", template=PX_TEMPLATE)
                    fig.update_layout(height=280, xaxis_title="Topic", yaxis_title="Valid Docs")
                    st.plotly_chart(fig, use_container_width=True)

            st.download_button(
                "⬇️ Download neg_topics.csv",
                data=neg_topics.to_csv(index=False).encode("utf-8"),
                file_name="neg_topics.csv",
                mime="text/csv",
                use_container_width=True
            )

    # POSITIVE topics
    with right:
        st.markdown("### POSITIF — Topik & Kata Kunci")
        if pos_topics is None or pos_topics.empty:
            st.error("pos_topics.csv tidak ditemukan / kosong.")
        else:
            st.dataframe(pos_topics, use_container_width=True)
            if "topic" in pos_topics.columns:
                if pos_support is not None and not pos_support.empty and "topic" in pos_support.columns:
                    join = pos_topics.merge(pos_support, on="topic", how="left")
                else:
                    join = pos_topics.copy()

                if "valid_docs" in join.columns:
                    fig = px.bar(join.sort_values("valid_docs", ascending=False), x="topic", y="valid_docs", template=PX_TEMPLATE)
                    fig.update_layout(height=280, xaxis_title="Topic", yaxis_title="Valid Docs")
                    st.plotly_chart(fig, use_container_width=True)

            st.download_button(
                "⬇️ Download pos_topics.csv",
                data=pos_topics.to_csv(index=False).encode("utf-8"),
                file_name="pos_topics.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    # Exemplars viewer (important for academic validity)
    st.markdown("### Bukti: Contoh Ulasan yang Mewakili Topik (Exemplars)")
    sent_choice = st.radio("Pilih sentimen exemplars", ["negatif", "positif"], horizontal=True)

    if sent_choice == "negatif":
        ex_df = neg_ex
    else:
        ex_df = pos_ex

    if ex_df is None or ex_df.empty:
        st.warning("File exemplars tidak ada / kosong.")
    else:
        # required cols: topic, text, rating
        need = {"topic", "text", "rating"}
        if not need.issubset(set(ex_df.columns)):
            st.error(f"Format exemplars tidak sesuai. Kolom minimal: {need}")
        else:
            topics = sorted(ex_df["topic"].dropna().unique().tolist())
            pick_topic = st.selectbox("Pilih topic", topics, index=0)
            n_show = st.slider("Jumlah contoh ditampilkan", 3, 20, 8, step=1)

            sub = ex_df[ex_df["topic"] == pick_topic].copy()
            sub = sub.head(n_show).copy()

            sub_disp = sub.copy()
            sub_disp["text"] = sub_disp["text"].apply(lambda s: wrap_text(s, 115))
            st.dataframe(sub_disp[["topic", "rating", "dom_prob", "overlap_topwords", "text"]]
                         if set(["dom_prob", "overlap_topwords"]).issubset(sub_disp.columns)
                         else sub_disp[["topic", "rating", "text"]],
                         use_container_width=True)

            st.download_button(
                "⬇️ Download exemplars (filtered)",
                data=sub.to_csv(index=False).encode("utf-8"),
                file_name=f"{sent_choice}_exemplars_topic_{pick_topic}.csv",
                mime="text/csv",
                use_container_width=True
            )

    card_close()

# ------------------------------------------------------------
# TAB 3: PEOPLE ANALYTICS (NEGATIVE PRIORITY + ACTIONS + LABEL BUILDER)
# ------------------------------------------------------------
with tab3:
    card_open(
        "People Analytics",
        "Mengubah insight topik menjadi prioritas perbaikan (frequency × impact) + rekomendasi aksi + bukti exemplars. "
        "Ini inti konversi mata kuliah People Analytics."
    )

    # People Analytics is strongest for NEGATIVE (you provided neg_action.csv)
    st.markdown("### A) Prioritas Masalah (NEGATIF) — dari neg_action.csv")
    if neg_action is None or neg_action.empty:
        st.error("neg_action.csv tidak ditemukan / kosong. Tab People Analytics butuh file ini.")
        card_close()
    else:
        # Normalize column names if needed
        na = neg_action.copy()

        # dom_topic -> topic for consistency
        if "dom_topic" in na.columns and "topic" not in na.columns:
            na = na.rename(columns={"dom_topic": "topic"})

        # Validate required cols
        required_cols = {"topic", "priority", "frequency", "mean_rating", "median_rating", "top_words"}
        if not required_cols.issubset(set(na.columns)):
            st.error(f"neg_action.csv kolom tidak lengkap. Butuh: {required_cols}")
            card_close()
        else:
            # Optional: merge label map
            label_map = topic_label_map.copy() if (topic_label_map is not None and not topic_label_map.empty) else pd.DataFrame()
            if not label_map.empty:
                # expecting: sentimen, topic_id, label, action
                # your topics are numeric; map topic->topic_id
                if set(["sentimen","topic_id","label","action"]).issubset(label_map.columns):
                    lm = label_map.copy()
                    lm["sentimen"] = lm["sentimen"].astype(str).str.lower().str.strip()
                    lm["topic_id"] = pd.to_numeric(lm["topic_id"], errors="coerce")
                    lm = lm.dropna(subset=["topic_id"]).copy()
                    lm["topic_id"] = lm["topic_id"].astype(int)
                    # topic in na might already be int
                    na["topic"] = pd.to_numeric(na["topic"], errors="coerce")
                    na = na.dropna(subset=["topic"]).copy()
                    na["topic"] = na["topic"].astype(int)
                    lm_neg = lm[lm["sentimen"] == "negatif"].copy()
                    na = na.merge(lm_neg, left_on="topic", right_on="topic_id", how="left").drop(columns=["topic_id"])
                else:
                    st.warning("topic_label_map.csv ada, tapi format kolom tidak sesuai (butuh sentimen,topic_id,label,action).")

            # Filters
            c1, c2, c3 = st.columns([1.0, 1.0, 1.5], gap="large")
            with c1:
                min_freq = st.slider("Min frequency", 1, int(na["frequency"].max()), 20)
            with c2:
                show_only_p1 = st.checkbox("Tampilkan hanya P1", value=False)
            with c3:
                st.caption("Interpretasi: P1 = prioritas tinggi (masalah sering & impact besar).")

            na_f = na[na["frequency"] >= min_freq].copy()
            if show_only_p1:
                na_f = na_f[na_f["priority"].astype(str).str.contains("P1", na=False)].copy()

            # Table
            cols_show = ["topic", "priority", "frequency", "mean_rating", "median_rating", "top_words"]
            if "label" in na_f.columns: cols_show.insert(1, "label")
            if "action" in na_f.columns: cols_show.append("action")

            st.dataframe(na_f[cols_show].sort_values(["priority", "frequency"], ascending=[True, False]), use_container_width=True)

            # Priority matrix scatter (frequency vs mean_rating)
            fig = px.scatter(
                na_f,
                x="frequency",
                y="mean_rating",
                color="priority",
                hover_data=["topic"],
                template=PX_TEMPLATE,
            )
            fig.update_layout(height=420, xaxis_title="Frequency", yaxis_title="Mean Rating (Impact)")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

            # Exemplars integrated with people analytics
            st.markdown("### B) Bukti: Exemplars untuk Topik Negatif")
            if neg_ex is None or neg_ex.empty:
                st.warning("neg_exemplars.csv tidak tersedia. Exemplars sangat disarankan untuk presentasi.")
            else:
                topics = sorted(neg_ex["topic"].dropna().unique().tolist())
                pick_topic = st.selectbox("Pilih topic untuk exemplars (negatif)", topics, index=0)
                n_show = st.slider("Jumlah exemplars", 3, 20, 8, step=1, key="pa_ex_n")

                sub = neg_ex[neg_ex["topic"] == pick_topic].head(n_show).copy()
                sub_disp = sub.copy()
                sub_disp["text"] = sub_disp["text"].apply(lambda s: wrap_text(s, 115))
                st.dataframe(sub_disp[["topic", "rating", "dom_prob", "overlap_topwords", "text"]]
                             if set(["dom_prob","overlap_topwords"]).issubset(sub_disp.columns)
                             else sub_disp[["topic","rating","text"]],
                             use_container_width=True)

            st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

            # POSITIVE "people analytics" (what to maintain) - derive from pos exemplars count or dataset
            st.markdown("### C) People Analytics (POSITIVE) — Hal yang Dipertahankan")
            st.caption("Kamu belum punya pos_action.csv. Untuk tetap kuat secara akademik, kita buat ringkasan positif dari frekuensi exemplars/topik atau dataset.")

            if pos_ex is not None and not pos_ex.empty and "topic" in pos_ex.columns:
                pos_freq = pos_ex.groupby("topic").size().reset_index(name="frequency_exemplars").sort_values("frequency_exemplars", ascending=False)
                st.success("✅ Ringkasan positif dibuat dari pos_exemplars.csv (frekuensi contoh per topik).")
            else:
                # fallback from dataset_final
                pos_freq = df_view[df_view["sentimen"] == "positif"].groupby("topic_id").size().reset_index(name="frequency").rename(columns={"topic_id":"topic"})
                st.warning("⚠️ pos_exemplars.csv tidak tersedia, ringkasan positif dihitung dari dataset_final (fallback).")

            # Join with pos_topics keywords if possible
            if pos_topics is not None and not pos_topics.empty and set(["topic","top_words"]).issubset(pos_topics.columns):
                pos_freq = pos_freq.merge(pos_topics, on="topic", how="left")

            st.dataframe(pos_freq.head(15), use_container_width=True)

            st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

            # Recommended: Label & Action Builder (in-app) -> download topic_label_map.csv
            st.markdown("### D) (Saran yang aku lakukan) Label & Action Builder (untuk laporan & dashboard)")
            st.caption(
                "Kamu butuh label topik + rekomendasi aksi yang manusiawi. Kalau topic_label_map.csv belum ada, "
                "kamu bisa buat di sini lalu download CSV."
            )

            # Build base template from available topics
            neg_topic_ids = sorted(pd.to_numeric(na["topic"], errors="coerce").dropna().astype(int).unique().tolist())
            pos_topic_ids = []
            if pos_topics is not None and "topic" in pos_topics.columns:
                pos_topic_ids = sorted(pd.to_numeric(pos_topics["topic"], errors="coerce").dropna().astype(int).unique().tolist())

            template_rows = []
            for t in neg_topic_ids:
                template_rows.append({"sentimen":"negatif", "topic_id":t, "label":"", "action":""})
            for t in pos_topic_ids:
                template_rows.append({"sentimen":"positif", "topic_id":t, "label":"", "action":""})

            template_df = pd.DataFrame(template_rows)

            if topic_label_map is not None and not topic_label_map.empty and set(["sentimen","topic_id","label","action"]).issubset(topic_label_map.columns):
                base = topic_label_map.copy()
                base["sentimen"] = base["sentimen"].astype(str).str.lower().str.strip()
                base["topic_id"] = pd.to_numeric(base["topic_id"], errors="coerce")
                base = base.dropna(subset=["topic_id"]).copy()
                base["topic_id"] = base["topic_id"].astype(int)
                # merge to preserve your previous edits
                template_df = template_df.merge(base, on=["sentimen","topic_id"], how="left", suffixes=("", "_old"))
                # if existing values exist, prefer them
                for col in ["label","action"]:
                    if f"{col}_old" in template_df.columns:
                        template_df[col] = template_df[f"{col}_old"].fillna(template_df[col])
                        template_df = template_df.drop(columns=[f"{col}_old"])

            edited = st.data_editor(
                template_df,
                use_container_width=True,
                num_rows="dynamic",
                hide_index=True
            )

            st.download_button(
                "⬇️ Download topic_label_map.csv (hasil edit)",
                data=edited.to_csv(index=False).encode("utf-8"),
                file_name="topic_label_map.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.info(
                "Cara pakai: download topic_label_map.csv → taruh ke folder data/ → redeploy. "
                "Setelah itu, tabel prioritas akan otomatis menampilkan kolom label & action."
            )

    card_close()

# ------------------------------------------------------------
# TAB 4: MODEL QUALITY (EVAL + SUPPORT)
# ------------------------------------------------------------
with tab4:
    card_open(
        "Model Quality (Academic)",
        "Bagian ini menguatkan laporan: pemilihan jumlah topik (K) dengan coherence/perplexity dan kualitas topik (support)."
    )

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("### NEGATIVE — K Selection (coherence/perplexity)")
        if neg_eval is None or neg_eval.empty:
            st.warning("neg_eval.csv tidak tersedia.")
        else:
            st.dataframe(neg_eval, use_container_width=True)
            if set(["K","coherence_cv"]).issubset(neg_eval.columns):
                fig = px.line(neg_eval, x="K", y="coherence_cv", markers=True, template=PX_TEMPLATE)
                fig.update_layout(height=280, xaxis_title="K (jumlah topik)", yaxis_title="Coherence (c_v)")
                st.plotly_chart(fig, use_container_width=True)
            if set(["K","log_perplexity_test"]).issubset(neg_eval.columns):
                fig2 = px.line(neg_eval, x="K", y="log_perplexity_test", markers=True, template=PX_TEMPLATE)
                fig2.update_layout(height=280, xaxis_title="K", yaxis_title="Log Perplexity (test)")
                st.plotly_chart(fig2, use_container_width=True)

    with c2:
        st.markdown("### POSITIVE — K Selection (coherence/perplexity)")
        if pos_eval is None or pos_eval.empty:
            st.warning("pos_eval.csv tidak tersedia.")
        else:
            st.dataframe(pos_eval, use_container_width=True)
            if set(["K","coherence_cv"]).issubset(pos_eval.columns):
                fig = px.line(pos_eval, x="K", y="coherence_cv", markers=True, template=PX_TEMPLATE)
                fig.update_layout(height=280, xaxis_title="K (jumlah topik)", yaxis_title="Coherence (c_v)")
                st.plotly_chart(fig, use_container_width=True)
            if set(["K","log_perplexity_test"]).issubset(pos_eval.columns):
                fig2 = px.line(pos_eval, x="K", y="log_perplexity_test", markers=True, template=PX_TEMPLATE)
                fig2.update_layout(height=280, xaxis_title="K", yaxis_title="Log Perplexity (test)")
                st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.markdown("### Topic Support (kualitas topik per topik)")
    s1, s2 = st.columns(2, gap="large")
    with s1:
        st.markdown("**NEGATIF — Support**")
        if neg_support is None or neg_support.empty:
            st.warning("neg_support.csv tidak tersedia.")
        else:
            st.dataframe(neg_support, use_container_width=True)
    with s2:
        st.markdown("**POSITIF — Support**")
        if pos_support is None or pos_support.empty:
            st.warning("pos_support.csv tidak tersedia.")
        else:
            st.dataframe(pos_support, use_container_width=True)

    card_close()

# ------------------------------------------------------------
# TAB 5: DEPLOYMENT (UPLOAD & EXPORT)
# ------------------------------------------------------------
with tab5:
    card_open(
        "Deployment (Upload & Export)",
        "Untuk konversi mata kuliah deployment aplikasi: bukti aplikasi bisa menerima input baru (CSV) dan mengeluarkan output (export). "
        "Namun, topic modeling tetap export-first agar stabil."
    )

    st.markdown("### Upload CSV opsional")
    uploaded = st.file_uploader("Upload CSV (opsional). Jika kosong, pakai dataset_final.csv (terfilter).", type=["csv"])

    if uploaded is not None:
        try:
            raw = pd.read_csv(uploaded)
            df_u, schema_u, err_u = standardize_dataset(raw)
            if err_u:
                st.error(f"CSV upload tidak valid: {err_u}")
                df_live = df_view
                st.info("Fallback ke dataset_final (terfilter).")
            else:
                df_live = df_u
                st.success("✅ Upload valid. Dataset upload dipakai untuk overview & export.")
        except Exception as e:
            st.error(f"Gagal membaca CSV upload: {e}")
            df_live = df_view
    else:
        df_live = df_view
        st.info("ℹ️ Menggunakan dataset_final (terfilter bila filter aktif).")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    st.markdown("### Output cepat (untuk bukti deployment)")
    # Export small summaries from uploaded or dataset_final
    out_sent = df_live.groupby("sentimen").size().reset_index(name="jumlah").sort_values("jumlah", ascending=False)
    out_rate = df_live.groupby("rating").size().reset_index(name="jumlah").sort_values("rating")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("**Distribusi Sentimen (dynamic)**")
        fig = px.bar(out_sent, x="sentimen", y="jumlah", template=PX_TEMPLATE)
        fig.update_layout(height=280, xaxis_title="Sentimen", yaxis_title="Jumlah")
        st.plotly_chart(fig, use_container_width=True)
        st.download_button(
            "⬇️ Download sentiment_counts_dynamic.csv",
            data=out_sent.to_csv(index=False).encode("utf-8"),
            file_name="sentiment_counts_dynamic.csv",
            mime="text/csv",
            use_container_width=True
        )

    with c2:
        st.markdown("**Distribusi Rating (dynamic)**")
        fig2 = px.bar(out_rate, x="rating", y="jumlah", template=PX_TEMPLATE)
        fig2.update_layout(height=280, xaxis_title="Rating", yaxis_title="Jumlah")
        st.plotly_chart(fig2, use_container_width=True)
        st.download_button(
            "⬇️ Download rating_counts_dynamic.csv",
            data=out_rate.to_csv(index=False).encode("utf-8"),
            file_name="rating_counts_dynamic.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)
    st.markdown("### Export ringkas untuk laporan")
    st.caption("Kamu bisa export subset data untuk lampiran (contoh 200 baris).")

    n_rows = st.slider("Jumlah baris export (subset)", 50, 1000, 200, step=50)
    subset = df_live.head(n_rows).copy()
    st.download_button(
        "⬇️ Download dataset_subset.csv",
        data=subset.to_csv(index=False).encode("utf-8"),
        file_name="dataset_subset.csv",
        mime="text/csv",
        use_container_width=True
    )

    card_close()

# ============================================================
# 10) FOOTER
# ============================================================
st.caption(
    f"© {datetime.now().year} • Export-first dashboard (stabil untuk presentasi) • "
    f"Build: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
