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

DATA = Path("data")
ASSETS = Path("assets")

# =========================
# LOGO PATHS (KAMU TARUH FILE DI assets/)
# =========================
LOGO_UPN_PATH = ASSETS / "logo_upn.png"
LOGO_BKKBN_PATH = ASSETS / "logo_bkkbn_jatim.png"

def show_logo(path: Path, width: int):
    if path.exists():
        st.image(str(path), width=width)
    else:
        st.warning(f"Logo belum ditemukan: {path}. Taruh file logo di folder assets/")

# =========================
# FILE HELPERS
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

# =========================
# DATASET HELPERS
# =========================
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
# BRIGHT UI THEME + BLACK FONT
# =========================
st.markdown(
    """
<style>
:root{
  --bg1:#F8FAFF;
  --bg2:#EEF2FF;
  --card:#FFFFFF;
  --text:#0B0F19;      /* hitam */
  --muted:#334155;     /* abu gelap */
  --stroke:rgba(15,23,42,0.12);
  --shadow:0 14px 32px rgba(2,6,23,0.10);
  --radius:18px;
  --radius-sm:14px;
}
html, body, [class*="css"]{
  color: var(--text) !important;
}
.block-container{
  max-width: 1200px;
  padding-top: 1.0rem;
}
.main{
  background: linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%);
}
.big-header{
  background: linear-gradient(135deg, rgba(59,130,246,0.18), rgba(99,102,241,0.18));
  border: 1px solid var(--stroke);
  border-radius: var(--radius);
  padding: 18px 18px;
  box-shadow: var(--shadow);
  margin-bottom: 14px;
}
.title{
  font-size: 34px;
  font-weight: 950;
  letter-spacing:-0.02em;
  color: var(--text);
  margin: 0;
}
.subtitle{
  margin-top: 6px;
  font-size: 13px;
  color: var(--muted);
}
.card{
  background: var(--card);
  border: 1px solid var(--stroke);
  border-radius: var(--radius);
  padding: 16px 16px 14px 16px;
  box-shadow: 0 10px 24px rgba(2,6,23,0.08);
  margin-bottom: 14px;
}
.card-title{ font-size: 18px; font-weight: 900; color: var(--text); }
.card-sub{ margin-top: 4px; margin-bottom: 12px; color: var(--muted); font-size: 12px; }
.kpi-grid{
  display:grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin: 10px 0 14px 0;
}
.kpi{
  background: var(--card);
  border: 1px solid var(--stroke);
  border-radius: var(--radius-sm);
  padding: 14px 14px;
  box-shadow: 0 8px 20px rgba(2,6,23,0.06);
}
.kpi .k{ color: var(--muted); font-size: 12px; font-weight: 800; }
.kpi .v{ font-size: 26px; font-weight: 950; color: var(--text); margin-top: 6px; }
.pill{
  display:inline-block;
  margin-top: 8px;
  padding: 3px 8px;
  border-radius: 999px;
  border: 1px solid var(--stroke);
  color: var(--muted);
  font-size: 11px;
}
</style>
""",
    unsafe_allow_html=True
)

# =========================
# LOAD TODAY DATA
# =========================
p_dataset_final = pick_file_optional("dataset_final.csv", "dataset_final (1).csv")
if p_dataset_final is None:
    st.error("dataset_final.csv tidak ditemukan di folder data/.")
    st.stop()

df_raw = load_dataset_final(p_dataset_final)
df_std, schema, err = standardize_dataset(df_raw)
if err:
    st.error(f"dataset_final.csv invalid: {err}")
    st.stop()

# Optional mapping
p_topic_map = pick_file_optional("topic_label_map.csv", "topic_label_map (1).csv")
topic_map = load_topic_label_map(p_topic_map) if p_topic_map else pd.DataFrame()

# Optional topic summary files (from notebook)
p_top_neg = pick_file_optional("ringkasan_topik_negatif.csv")
p_top_pos = pick_file_optional("ringkasan_topik_positif.csv")
top_neg = load_csv(p_top_neg) if p_top_neg else None
top_pos = load_csv(p_top_pos) if p_top_pos else None

# =========================
# OVERVIEW METRICS
# =========================
dist_rating = df_std.groupby("rating").size().reset_index(name="jumlah_ulasan").sort_values("rating")
dist_sent = df_std.groupby("sentimen").size().reset_index(name="jumlah_ulasan").sort_values("jumlah_ulasan", ascending=False)

total_data = int(len(df_std))
avg_rating = float(df_std["rating"].mean()) if len(df_std) else 0.0
pos_pct = 100.0 * float((df_std["sentimen"] == "positif").mean()) if len(df_std) else 0.0
neg_pct = 100.0 * float((df_std["sentimen"] == "negatif").mean()) if len(df_std) else 0.0

# =========================
# PLOTLY TEMPLATE (BRIGHT)
# =========================
PX_TEMPLATE = "plotly_white"

# =========================
# APP HEADER WITH BIG LOGOS
# =========================
st.markdown('<div class="big-header">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1.2, 4.5, 1.2], vertical_alignment="center")

with c1:
    show_logo(LOGO_UPN_PATH, width=140)          # BESAR
with c2:
    st.markdown('<div class="title">Dashboard Analitik Media Sosial Berbasis Rating Aplikasi SIGA</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Konversi: Analitik Media Sosial • People Analytics • Deployment Aplikasi (Streamlit)</div>', unsafe_allow_html=True)
with c3:
    show_logo(LOGO_BKKBN_PATH, width=140)        # BESAR

st.markdown("</div>", unsafe_allow_html=True)

# KPI
st.markdown(
    f"""
    <div class="kpi-grid">
      <div class="kpi"><div class="k">Total Ulasan</div><div class="v">{total_data:,}</div><div class="pill">dataset_final.csv</div></div>
      <div class="kpi"><div class="k">Rata-rata Rating</div><div class="v">{avg_rating:.2f}</div><div class="pill">computed</div></div>
      <div class="kpi"><div class="k">% Positif</div><div class="v">{pos_pct:.2f}%</div><div class="pill">computed</div></div>
      <div class="kpi"><div class="k">% Negatif</div><div class="v">{neg_pct:.2f}%</div><div class="pill">computed</div></div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🧩 Topic Modeling", "🧑‍💼 People Analytics", "🚀 Deployment Analytics"])

# ---------- OVERVIEW ----------
with tab1:
    card_open("Distribusi Rating", "Dihitung dari dataset_final.csv (terbaru)")
    fig = px.bar(dist_rating, x="rating", y="jumlah_ulasan", template=PX_TEMPLATE)
    fig.update_layout(height=360, xaxis_title="Rating", yaxis_title="Jumlah Ulasan")
    st.plotly_chart(fig, use_container_width=True)
    card_close()

    card_open("Distribusi Sentimen", "Dihitung dari dataset_final.csv (terbaru)")
    fig2 = px.pie(dist_sent, names="sentimen", values="jumlah_ulasan", template=PX_TEMPLATE)
    fig2.update_layout(height=360)
    st.plotly_chart(fig2, use_container_width=True)
    card_close()

# ---------- TOPIC MODELING ----------
with tab2:
    card_open("Topik NEGATIF (Ringkasan)", "Hasil LDA dari notebook (export CSV)")
    if top_neg is None:
        st.warning("ringkasan_topik_negatif.csv belum ada di folder data/.")
    else:
        st.dataframe(top_neg, use_container_width=True)
    card_close()

    card_open("Topik POSITIF (Ringkasan)", "Hasil LDA dari notebook (export CSV)")
    if top_pos is None:
        st.warning("ringkasan_topik_positif.csv belum ada di folder data/.")
    else:
        st.dataframe(top_pos, use_container_width=True)
    card_close()

# ---------- PEOPLE ANALYTICS ----------
with tab3:
    card_open("People Analytics (Prioritas Masalah)", "Dihitung ulang dari dataset_final.csv + mapping action")

    sent_choice = st.selectbox("Sentimen", ["negatif", "positif"], index=0)
    min_support = st.slider("Minimum support (ulasan/topik)", 5, 200, 20, step=5)

    topic_summary, df_sent, thr, e = compute_topic_metrics(df_std, sent_choice, min_support=min_support)
    if e:
        st.error(e)
        card_close()
    else:
        if not topic_map.empty:
            mp = topic_map[topic_map["sentimen"] == sent_choice][["topic_id", "label", "action"]].copy()
            topic_summary = topic_summary.merge(mp, on="topic_id", how="left")

        st.dataframe(topic_summary, use_container_width=True)

        freq_thr, rate_thr = thr
        fig = px.scatter(topic_summary, x="frequency", y="mean_rating", color="priority",
                         hover_data=["topic_id", "median_rating"], template=PX_TEMPLATE)
        fig.add_vline(x=freq_thr, line_dash="dash")
        fig.add_hline(y=rate_thr, line_dash="dash")
        fig.update_layout(height=420, xaxis_title="Frequency", yaxis_title="Mean Rating")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Exemplars (contoh ulasan per topik)**")
        topic_options = topic_summary["topic_id"].astype(int).tolist()
        pick_topic = st.selectbox("Pilih topic_id", topic_options, index=0)
        ex_df = pick_exemplars(df_sent, int(pick_topic), n=5)
        st.dataframe(ex_df, use_container_width=True)

    card_close()

# ---------- DEPLOYMENT ANALYTICS ----------
with tab4:
    card_open("Deployment Analytics (Dynamic)", "Upload/Filter → output berubah → export laporan")

    uploaded = st.file_uploader("Upload CSV (opsional). Jika kosong, pakai dataset_final.csv", type=["csv"])
    if uploaded is not None:
        raw = pd.read_csv(uploaded)
        df_live, _, e = standardize_dataset(raw)
        if e:
            st.error(f"CSV upload invalid: {e}")
            card_close()
        else:
            st.success("✅ Dataset upload dipakai.")
    else:
        df_live = df_std
        st.info("ℹ️ Menggunakan dataset_final.csv.")

    if 'df_live' in locals():
        sent_choice = st.selectbox("Sentimen (Deployment)", ["negatif", "positif", "netral"], index=0)
        min_support = st.slider("Minimum support (Deployment)", 5, 200, 20, step=5)

        topic_summary, df_sent, thr, e = compute_topic_metrics(df_live, sent_choice, min_support=min_support)
        if e:
            st.error(e)
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

st.caption("© Dashboard cerah + font hitam. Logo besar di header (assets/).")
