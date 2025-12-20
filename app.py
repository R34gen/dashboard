import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Dashboard Analitik Media Sosial Berbasis Rating Aplikasi SIGA",
    page_icon="📊",
    layout="wide"
)

ROOT = Path(__file__).parent
DATA = ROOT / "data"

LOGO_UPN_PATH = ROOT / "logo_upn.png"
LOGO_BKKBN_PATH = ROOT / "logo_bkkbn.png"

PX_TEMPLATE = "plotly_white"

# =========================
# UI THEME (BRIGHT + BLACK TEXT)
# =========================
st.markdown(
    """
<style>
/* Light, bright background */
.main{
  background: linear-gradient(180deg, #F8FAFF 0%, #EEF2FF 100%);
}

/* Typography: keep it BLACK / dark */
html, body, [class*="css"]{
  color: #0B0F19 !important;
}

/* Layout width */
.block-container{
  max-width: 1240px;
  padding-top: 1.0rem;
}

/* Header container */
.hero{
  background: linear-gradient(135deg, rgba(59,130,246,0.22), rgba(99,102,241,0.18));
  border: 1px solid rgba(15,23,42,0.12);
  border-radius: 22px;
  padding: 18px 18px;
  box-shadow: 0 14px 32px rgba(2,6,23,0.10);
  margin-bottom: 14px;
}
.hero-title{
  font-size: 34px;
  font-weight: 950;
  letter-spacing: -0.02em;
  line-height: 1.08;
  margin: 0;
  color: #0B0F19;
}
.hero-sub{
  margin-top: 8px;
  font-size: 13px;
  color: #334155;
}
.badge{
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(15,23,42,0.12);
  background: rgba(255,255,255,0.65);
  color: #0B0F19;
  font-size: 12px;
  font-weight: 700;
}

/* Cards */
.card{
  background: #FFFFFF;
  border: 1px solid rgba(15,23,42,0.12);
  border-radius: 18px;
  padding: 16px 16px 14px 16px;
  box-shadow: 0 10px 24px rgba(2,6,23,0.08);
  margin-bottom: 14px;
}
.card-title{
  font-size: 18px;
  font-weight: 900;
  margin: 0;
  color: #0B0F19;
}
.card-sub{
  margin-top: 6px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #334155;
}

/* KPI cards */
.kpi-grid{
  display:grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin: 10px 0 14px 0;
}
.kpi{
  background: #FFFFFF;
  border: 1px solid rgba(15,23,42,0.12);
  border-radius: 16px;
  padding: 14px 14px;
  box-shadow: 0 8px 20px rgba(2,6,23,0.06);
}
.kpi-k{ font-size: 12px; font-weight: 850; color: #334155; }
.kpi-v{ font-size: 26px; font-weight: 950; color: #0B0F19; margin-top: 6px; }
.kpi-note{
  display:inline-block;
  margin-top: 8px;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid rgba(15,23,42,0.12);
  color: #334155;
  font-size: 11px;
  background: rgba(248,250,255,0.8);
}

/* Make tables look clean */
[data-testid="stDataFrame"]{
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(15,23,42,0.12);
}

/* Tabs spacing */
.stTabs [data-baseweb="tab-list"]{
  gap: 8px;
}
</style>
""",
    unsafe_allow_html=True
)

# =========================
# UI helper
# =========================
def show_logo(path: Path, width: int):
    if path.exists():
        st.image(str(path), width=width)
    else:
        st.warning(f"Logo tidak ditemukan: {path.name} (cek root repo).")

def card_open(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="card">
          <div class="card-title">{title}</div>
          <div class="card-sub">{subtitle}</div>
        """,
        unsafe_allow_html=True
    )

def card_close():
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# DATA helpers (core tetap)
# =========================
def pick_file_optional(*names: str) -> Path | None:
    for n in names:
        p = DATA / n
        if p.exists():
            return p
    return None

@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def coalesce_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None

def normalize_sentiment(x) -> str:
    if pd.isna(x): return ""
    s = str(x).strip().lower()
    if s in {"positive", "positif", "pos"}: return "positif"
    if s in {"negative", "negatif", "neg"}: return "negatif"
    if s in {"neutral", "netral", "neu"}: return "netral"
    return s

@st.cache_data(show_spinner=False)
def load_dataset_final(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def detect_dataset_schema(df: pd.DataFrame) -> dict:
    sent_col  = coalesce_col(df, ["sentimen", "sentiment", "label_sentimen", "label"])
    topic_col = coalesce_col(df, ["topic_id", "topic", "topik", "dominant_topic", "dom_topic"])
    rating_col= coalesce_col(df, ["rating", "rate", "score", "bintang", "stars"])
    text_col  = coalesce_col(df, ["text", "ulasan", "review", "komentar", "steming_data"])
    return {"sent_col": sent_col, "topic_col": topic_col, "rating_col": rating_col, "text_col": text_col}

def standardize_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict, str | None]:
    schema = detect_dataset_schema(df)
    miss = [k for k, v in schema.items() if v is None]
    if miss:
        return df, schema, f"Kolom wajib tidak ditemukan: {', '.join(miss)}"

    tmp = df.copy()
    tmp[schema["sent_col"]] = tmp[schema["sent_col"]].apply(normalize_sentiment)
    tmp[schema["rating_col"]] = pd.to_numeric(tmp[schema["rating_col"]], errors="coerce")
    tmp[schema["topic_col"]]  = pd.to_numeric(tmp[schema["topic_col"]], errors="coerce")
    tmp = tmp.dropna(subset=[schema["rating_col"], schema["topic_col"]])

    df_std = pd.DataFrame({
        "sentimen": tmp[schema["sent_col"]].astype(str).str.lower().str.strip(),
        "topic_id": tmp[schema["topic_col"]].astype(int),
        "rating": tmp[schema["rating_col"]].astype(float),
        "text": tmp[schema["text_col"]].astype(str),
    })
    return df_std, schema, None

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

    topic_summary = (tmp.groupby("topic_id")
                     .agg(frequency=("topic_id", "size"),
                          mean_rating=("rating", "mean"),
                          median_rating=("rating", "median"))
                     .reset_index())

    topic_summary = topic_summary[topic_summary["frequency"] >= min_support].copy()
    if topic_summary.empty:
        return None, None, None, f"Tidak ada topik dengan support >= {min_support}."

    freq_thr = float(topic_summary["frequency"].median())
    rate_thr = float(topic_summary["mean_rating"].median())

    def assign_priority(row):
        high_freq = row["frequency"] >= freq_thr
        low_rate  = row["mean_rating"] <= rate_thr
        if high_freq and low_rate:
            return "P1 (Prioritas Tinggi)"
        if high_freq or low_rate:
            return "P2 (Prioritas Sedang)"
        return "P3 (Prioritas Rendah)"

    topic_summary["priority"] = topic_summary.apply(assign_priority, axis=1)
    return topic_summary.sort_values(["priority", "frequency"], ascending=[True, False]), tmp, (freq_thr, rate_thr), None

def pick_exemplars(df_sent: pd.DataFrame, topic_id: int, n: int = 5):
    sub = df_sent[df_sent["topic_id"] == topic_id].copy()
    if sub.empty:
        return sub
    sub = sub.drop_duplicates(subset=["text"])
    sub["len"] = sub["text"].astype(str).str.len()
    sub = sub.sort_values(["len", "rating"], ascending=[False, True]).head(n)
    return sub[["topic_id", "rating", "text"]]

# =========================
# LOAD CORE FILES (core tidak berubah)
# =========================
p_dataset_final = DATA / "dataset_final.csv"
if not p_dataset_final.exists():
    st.error("dataset_final.csv tidak ditemukan di folder data/.")
    st.stop()

df_raw = load_dataset_final(p_dataset_final)
df_std, schema, err = standardize_dataset(df_raw)
if err:
    st.error(f"dataset_final.csv invalid: {err}")
    st.stop()

# optional topic summary from notebook
p_top_neg = pick_file_optional("ringkasan_topik_negatif.csv")
p_top_pos = pick_file_optional("ringkasan_topik_positif.csv")
top_neg = load_csv(p_top_neg) if p_top_neg else None
top_pos = load_csv(p_top_pos) if p_top_pos else None

# optional mapping
p_topic_map = pick_file_optional("topic_label_map.csv")
topic_map = load_topic_label_map(p_topic_map) if p_topic_map else pd.DataFrame()

# =========================
# COMPUTE OVERVIEW (core same, just computed)
# =========================
dist_rating = df_std.groupby("rating").size().reset_index(name="jumlah_ulasan").sort_values("rating")
dist_sent = df_std.groupby("sentimen").size().reset_index(name="jumlah_ulasan").sort_values("jumlah_ulasan", ascending=False)

total_data = int(len(df_std))
avg_rating = float(df_std["rating"].mean()) if total_data else 0.0
pos_pct = 100.0 * float((df_std["sentimen"] == "positif").mean()) if total_data else 0.0
neg_pct = 100.0 * float((df_std["sentimen"] == "negatif").mean()) if total_data else 0.0

# =========================
# HERO HEADER (LOGO BESAR)
# =========================
st.markdown('<div class="hero">', unsafe_allow_html=True)

c1, c2, c3 = st.columns([1.35, 4.3, 1.35], vertical_alignment="center")
with c1:
    show_logo(LOGO_UPN_PATH, width=170)  # BESAR
with c2:
    st.markdown('<div class="hero-title">Dashboard Analitik Media Sosial Berbasis Rating Aplikasi SIGA</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-sub">'
        '<span class="badge">UPN</span> &nbsp;'
        '<span class="badge">BKKBN Jawa Timur</span> &nbsp;'
        '<span class="badge">Streamlit Deployment</span> &nbsp;'
        '<br/>Konversi: Analitik Media Sosial • People Analytics • Deployment Aplikasi'
        '</div>',
        unsafe_allow_html=True
    )
with c3:
    show_logo(LOGO_BKKBN_PATH, width=170)  # BESAR

st.markdown("</div>", unsafe_allow_html=True)

# KPI row
st.markdown(
    f"""
    <div class="kpi-grid">
      <div class="kpi"><div class="kpi-k">Total Ulasan</div><div class="kpi-v">{total_data:,}</div><div class="kpi-note">dataset_final.csv</div></div>
      <div class="kpi"><div class="kpi-k">Rata-rata Rating</div><div class="kpi-v">{avg_rating:.2f}</div><div class="kpi-note">computed</div></div>
      <div class="kpi"><div class="kpi-k">% Positif</div><div class="kpi-v">{pos_pct:.2f}%</div><div class="kpi-note">computed</div></div>
      <div class="kpi"><div class="kpi-k">% Negatif</div><div class="kpi-v">{neg_pct:.2f}%</div><div class="kpi-note">computed</div></div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# SIDEBAR (UX: global filter)
# =========================
with st.sidebar:
    st.markdown("## ⚙️ Kontrol Dashboard")
    st.caption("Filter global untuk tampilan data.")
    rating_filter = st.multiselect("Filter Rating (opsional)", sorted(df_std["rating"].unique().tolist()))
    sent_filter = st.multiselect("Filter Sentimen (opsional)", sorted(df_std["sentimen"].unique().tolist()))

df_view = df_std.copy()
if rating_filter:
    df_view = df_view[df_view["rating"].isin(rating_filter)]
if sent_filter:
    df_view = df_view[df_view["sentimen"].isin(sent_filter)]

# recompute overview for filtered view
dist_rating_f = df_view.groupby("rating").size().reset_index(name="jumlah_ulasan").sort_values("rating")
dist_sent_f = df_view.groupby("sentimen").size().reset_index(name="jumlah_ulasan").sort_values("jumlah_ulasan", ascending=False)

# =========================
# TABS (core same)
# =========================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🧩 Topic Modeling", "🧑‍💼 People Analytics", "🚀 Deployment Analytics"])

# ---------- OVERVIEW ----------
with tab1:
    card_open("Distribusi Rating", "Cerah, ringkas, mudah dibaca (berdasarkan filter sidebar jika dipakai).")
    fig = px.bar(dist_rating_f, x="rating", y="jumlah_ulasan", template=PX_TEMPLATE)
    fig.update_layout(height=360, xaxis_title="Rating", yaxis_title="Jumlah Ulasan")
    st.plotly_chart(fig, use_container_width=True)
    card_close()

    card_open("Distribusi Sentimen", "Komposisi sentimen (berdasarkan filter sidebar jika dipakai).")
    fig2 = px.pie(dist_sent_f, names="sentimen", values="jumlah_ulasan", template=PX_TEMPLATE)
    fig2.update_layout(height=360)
    st.plotly_chart(fig2, use_container_width=True)
    card_close()

    card_open("Preview Data (opsional)", "Untuk meyakinkan dosen data yang dipakai adalah dataset_final terbaru.")
    st.dataframe(df_view.head(30), use_container_width=True)
    card_close()

# ---------- TOPIC MODELING ----------
with tab2:
    card_open("Topik NEGATIF (Ringkasan LDA)", "Menampilkan hasil LDA dari notebook (file ringkasan).")
    if top_neg is None:
        st.warning("ringkasan_topik_negatif.csv belum ada di folder data/. Export dari notebook dulu.")
    else:
        st.dataframe(top_neg, use_container_width=True)
    card_close()

    card_open("Topik POSITIF (Ringkasan LDA)", "Menampilkan hasil LDA dari notebook (file ringkasan).")
    if top_pos is None:
        st.warning("ringkasan_topik_positif.csv belum ada di folder data/. Export dari notebook dulu.")
    else:
        st.dataframe(top_pos, use_container_width=True)
    card_close()

# ---------- PEOPLE ANALYTICS ----------
with tab3:
    card_open("People Analytics: Prioritas Masalah", "Frequency × Impact (rating) + bukti exemplars untuk rekomendasi aksi.")

    left, right = st.columns([1.2, 1.0])
    with left:
        sent_choice = st.selectbox("Sentimen untuk analisis prioritas", ["negatif", "positif"], index=0)
    with right:
        min_support = st.slider("Minimum support (ulasan/topik)", 5, 200, 20, step=5)

    topic_summary, df_sent, thr, e = compute_topic_metrics(df_view, sent_choice, min_support=min_support)
    if e:
        st.error(e)
        card_close()
    else:
        # merge label/action jika ada
        if not topic_map.empty:
            mp = topic_map[topic_map["sentimen"] == sent_choice][["topic_id", "label", "action"]].copy()
            topic_summary = topic_summary.merge(mp, on="topic_id", how="left")

        st.dataframe(topic_summary, use_container_width=True)

        freq_thr, rate_thr = thr
        fig = px.scatter(
            topic_summary,
            x="frequency",
            y="mean_rating",
            color="priority",
            hover_data=["topic_id", "median_rating"],
            template=PX_TEMPLATE
        )
        fig.add_vline(x=freq_thr, line_dash="dash")
        fig.add_hline(y=rate_thr, line_dash="dash")
        fig.update_layout(height=420, xaxis_title="Frequency", yaxis_title="Mean Rating")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Evidensi (Exemplars per Topik)")
        topic_options = topic_summary["topic_id"].astype(int).tolist()
        pick_topic = st.selectbox("Pilih topic_id", topic_options, index=0)
        ex_df = pick_exemplars(df_sent, int(pick_topic), n=5)
        st.dataframe(ex_df, use_container_width=True)

    card_close()

# ---------- DEPLOYMENT ANALYTICS ----------
with tab4:
    card_open("Deployment Analytics (Dynamic)", "Upload/Filter → output berubah → export untuk laporan & presentasi.")

    uploaded = st.file_uploader("Upload CSV (opsional). Jika kosong, pakai dataset_final.csv", type=["csv"])
    if uploaded is not None:
        raw = pd.read_csv(uploaded)
        df_live, _, e2 = standardize_dataset(raw)
        if e2:
            st.error(f"CSV upload invalid: {e2}")
            card_close()
        else:
            st.success("✅ Dataset upload dipakai.")
    else:
        df_live = df_view
        st.info("ℹ️ Menggunakan dataset_final.csv (dengan filter sidebar jika dipakai).")

    if "df_live" in locals() and df_live is not None:
        left, right = st.columns([1.2, 1.0])
        with left:
            sent_choice = st.selectbox("Sentimen (Deployment)", ["negatif", "positif", "netral"], index=0)
        with right:
            min_support = st.slider("Minimum support (Deployment)", 5, 200, 20, step=5)

        topic_summary, df_sent, thr, e3 = compute_topic_metrics(df_live, sent_choice, min_support=min_support)
        if e3:
            st.error(e3)
            card_close()
        else:
            if not topic_map.empty:
                mp = topic_map[topic_map["sentimen"] == sent_choice][["topic_id", "label", "action"]].copy()
                topic_summary = topic_summary.merge(mp, on="topic_id", how="left")

            st.dataframe(topic_summary, use_container_width=True)

            topic_options = topic_summary["topic_id"].astype(int).tolist()
            pick_topic = st.selectbox("Pilih topic_id (Deployment)", topic_options, index=0)
            ex_df = pick_exemplars(df_sent, int(pick_topic), n=5)
            st.dataframe(ex_df, use_container_width=True)

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

st.caption("© Dashboard cerah + font hitam + logo besar. Core analitik tidak berubah, hanya UI/UX diperbaiki.")
