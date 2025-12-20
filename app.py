import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from datetime import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="People Analytics Dashboard", page_icon="📊", layout="wide")

# =========================
# AUTH (DEMO)
# =========================
USERS = {"mahasiswa": "upnvjt"}  # ubah kalau mau
if "login" not in st.session_state:
    st.session_state.login = False

# =========================
# PATHS
# =========================
DATA = Path("data")

# =========================
# FILE HELPERS
# =========================
def pick_file(*names: str) -> Path:
    for n in names:
        p = DATA / n
        if p.exists():
            return p
    st.error("File tidak ditemukan di folder data/. Pastikan file ada.")
    st.write("Dicari:", list(names))
    st.stop()

def pick_file_optional(*names: str) -> Path | None:
    for n in names:
        p = DATA / n
        if p.exists():
            return p
    return None

@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def safe_col(df: pd.DataFrame, *names: str):
    for n in names:
        if n in df.columns:
            return n
    return None

# =========================
# UI HELPERS (RESTORE UI)
# =========================
def header_center(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="header">
          <div class="header-title">{title}</div>
          <div class="header-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

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
# CSS (RESTORE ORIGINAL STYLE)
# =========================
st.markdown(
    """
<style>
:root{
  --bg:#F5F7FB;
  --surface:#FFFFFF;
  --ink:#0F172A;
  --muted:#64748B;
  --stroke:rgba(15,23,42,0.10);
  --shadow:0 10px 30px rgba(2,6,23,0.08);
  --radius:18px;
  --radius-sm:14px;
  --brand:#2563EB;
  --good:#16A34A;
  --warn:#F59E0B;
  --bad:#DC2626;
  --mono:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  --font:Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}
html, body, [class*="css"]{ font-family: var(--font); }
.block-container{ padding-top: 1.2rem; padding-bottom: 2.0rem; max-width: 1200px; }
.header{
  background: linear-gradient(135deg, rgba(37,99,235,0.10), rgba(99,102,241,0.10));
  border:1px solid var(--stroke);
  border-radius: var(--radius);
  padding: 18px 20px;
  box-shadow: var(--shadow);
  margin-bottom: 14px;
}
.header-title{ font-size: 34px; font-weight: 900; letter-spacing:-0.02em; color: var(--ink); }
.header-sub{ margin-top: 4px; color: var(--muted); font-size: 13px; }

.kpi-grid{
  display:grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin: 10px 0 14px 0;
}
.kpi{
  background: var(--surface);
  border: 1px solid var(--stroke);
  border-radius: var(--radius-sm);
  padding: 14px 14px;
  box-shadow: 0 8px 20px rgba(2,6,23,0.06);
}
.kpi .title{ color: var(--muted); font-size: 12px; font-weight: 700; }
.kpi .value{ font-size:26px; font-weight:950; color: var(--ink); margin-top: 6px; }
.kpi .pill{
  display:inline-block;
  margin-top: 8px;
  padding: 3px 8px;
  border-radius: 999px;
  border:1px solid var(--stroke);
  color: var(--muted);
  font-size: 11px;
  font-family: var(--mono);
}

.card{
  background: var(--surface);
  border: 1px solid var(--stroke);
  border-radius: var(--radius);
  padding: 16px 16px 14px 16px;
  box-shadow: var(--shadow);
  margin-bottom: 14px;
}
.card-title{ font-size: 18px; font-weight: 900; color: var(--ink); }
.card-sub{ margin-top: 4px; margin-bottom: 12px; color: var(--muted); font-size: 12px; }

.small-note{ color: var(--muted); font-size: 12px; }
hr.soft{ border:0; border-top:1px solid rgba(15,23,42,0.08); margin: 12px 0; }
</style>
""",
    unsafe_allow_html=True
)

# =========================
# PLOTLY STYLE (RESTORE ORIGINAL)
# =========================
PX_TEMPLATE = "simple_white"
AXIS = dict(showgrid=True, gridcolor="rgba(15,23,42,0.08)", zeroline=False)

# =========================
# ROBUST DISTRIBUTION COLUMN PICKER (NEW, supaya tidak warning)
# =========================
def pick_x_y_columns_for_distribution(df: pd.DataFrame, kind: str):
    """
    kind: 'rating' atau 'sentiment'
    Return: (x_col, y_col, err)
    """
    cols = list(df.columns)

    # kandidat Y (jumlah)
    y_candidates = ["jumlah_ulasan", "jumlah", "count", "freq", "frequency", "total", "n", "cnt"]
    y_col = None
    for c in y_candidates:
        if c in cols:
            y_col = c
            break

    # fallback: kolom numerik paling "kuat"
    if y_col is None:
        numeric_cols = []
        for c in cols:
            s = pd.to_numeric(df[c], errors="coerce")
            if s.notna().sum() >= max(3, int(0.6 * len(df))):
                numeric_cols.append((c, float(s.fillna(0).sum())))
        if numeric_cols:
            y_col = sorted(numeric_cols, key=lambda x: x[1], reverse=True)[0][0]

    # kandidat X
    if kind == "rating":
        x_candidates = ["rating", "Rating", "score", "rate", "bintang", "stars", "nilai"]
    else:
        x_candidates = ["sentimen", "sentiment", "label", "kategori", "class", "kelas"]

    x_col = None
    for c in x_candidates:
        if c in cols:
            x_col = c
            break

    # fallback: cari kolom non-numerik
    if x_col is None:
        for c in cols:
            s = pd.to_numeric(df[c], errors="coerce")
            if s.notna().sum() < int(0.4 * len(df)):
                x_col = c
                break

    if x_col is None or y_col is None:
        return None, None, f"Format kolom tidak terdeteksi. Kolom tersedia: {cols}"

    return x_col, y_col, None

# =========================
# DEPLOYMENT ANALYTICS HELPERS (NEW)
# =========================
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
    tmp[schema["topic_col"]] = pd.to_numeric(tmp[schema["topic_col"]], errors="coerce")
    tmp = tmp.dropna(subset=[schema["rating_col"], schema["topic_col"]])

    df_std = pd.DataFrame({
        "sentimen": tmp[schema["sent_col"]].astype(str).str.lower().str.strip(),
        "topic_id": tmp[schema["topic_col"]].astype(int),
        "rating": tmp[schema["rating_col"]].astype(float),
        "text": tmp[schema["text_col"]].astype(str),
    })
    return df_std, schema, None

# =========================
# TOPIC LABEL MAP (NEW)
# =========================
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

# =========================
# LOAD FILES (TETAP SEPERTI APP AWAL KAMU)
# =========================
# Overview
p_rating     = pick_file("distribusi_rating.csv")
p_sentiment  = pick_file("distribusi_sentimen.csv", "distribusi_sentimen (1).csv")

# Topic modeling
p_top_neg    = pick_file("ringkasan_topik_negatif.csv")
p_top_neg_f  = pick_file("hasil_topic_negatif_full.csv")
p_top_pos    = pick_file("ringkasan_topik_positif.csv")
p_top_pos_f  = pick_file("hasil_topic_positif_full.csv")

# People analytics
p_people_sum = pick_file("people_analytics_summary.csv", "people_analytics_summary (1).csv")
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

# dataset_final (opsional, tidak ganggu fitur lama)
p_dataset_final = pick_file_optional("dataset_final.csv", "dataset_final (1).csv")
dataset_final_raw = load_dataset_final(p_dataset_final) if p_dataset_final else pd.DataFrame()
dataset_final, dataset_schema, dataset_err = (pd.DataFrame(), {}, None)
if not dataset_final_raw.empty:
    dataset_final, dataset_schema, dataset_err = standardize_dataset(dataset_final_raw)

# topic_label_map (opsional, tidak ganggu fitur lama)
p_topic_map = pick_file_optional("topic_label_map.csv", "topic_label_map (1).csv")
topic_map = load_topic_label_map(p_topic_map) if p_topic_map else pd.DataFrame()

# =========================
# KPI (lebih robust, pakai picker juga)
# =========================
# Rating KPI
x_r, y_r, err_r = pick_x_y_columns_for_distribution(rating_df, "rating")
total_data = int(pd.to_numeric(rating_df[y_r], errors="coerce").fillna(0).sum()) if (y_r and y_r in rating_df.columns) else int(len(rating_df))

avg_rating = np.nan
if x_r and y_r and x_r in rating_df.columns and y_r in rating_df.columns:
    tmp = rating_df[[x_r, y_r]].copy()
    tmp[x_r] = pd.to_numeric(tmp[x_r], errors="coerce")
    tmp[y_r] = pd.to_numeric(tmp[y_r], errors="coerce").fillna(0)
    if tmp[x_r].notna().any() and tmp[y_r].sum() > 0:
        avg_rating = float((tmp[x_r] * tmp[y_r]).sum() / tmp[y_r].sum())

# Sentiment KPI (optional)
x_s, y_s, err_s = pick_x_y_columns_for_distribution(sent_df, "sentiment")
pos_pct = np.nan
neg_pct = np.nan
if x_s and y_s and x_s in sent_df.columns and y_s in sent_df.columns:
    t = sent_df[[x_s, y_s]].copy()
    t[y_s] = pd.to_numeric(t[y_s], errors="coerce").fillna(0)
    total = float(t[y_s].sum()) if float(t[y_s].sum()) > 0 else 0.0
    if total > 0:
        # normalisasi label
        t["_lab"] = t[x_s].astype(str).str.lower().str.strip().apply(normalize_sentiment)
        pos = float(t.loc[t["_lab"] == "positif", y_s].sum())
        neg = float(t.loc[t["_lab"] == "negatif", y_s].sum())
        pos_pct = 100.0 * pos / total
        neg_pct = 100.0 * neg / total

# =========================
# AUTH UI
# =========================
def login_page():
    header_center("People Analytics Dashboard", "Silakan login untuk mengakses dashboard.")
    card_open("Login", "Demo login sederhana")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login", use_container_width=True):
        if USERS.get(u) == p:
            st.session_state.login = True
            st.success("Login berhasil!")
            st.rerun()  # FIX: Streamlit terbaru
        else:
            st.error("Username / password salah.")
    card_close()

# =========================
# DASHBOARD
# =========================
def dashboard():
    header_center("Dashboard Analitik Medsos & People Analytics", "Overview • Topic Modeling • People Analytics Evidence")

    # status file opsional
    if p_dataset_final is None:
        st.markdown("<div class='small-note'>ℹ️ dataset_final.csv belum ada (opsional). Fitur lama tetap berjalan.</div>", unsafe_allow_html=True)
    elif dataset_err:
        st.warning(f"dataset_final.csv terdeteksi, tapi tidak valid: {dataset_err}")
    else:
        st.markdown("<div class='small-note'>✅ dataset_final.csv terdeteksi & skema kolom berhasil distandarkan (siap untuk deployment analytics).</div>", unsafe_allow_html=True)

    if p_topic_map is None:
        st.markdown("<div class='small-note'>ℹ️ topic_label_map.csv belum ada (opsional).</div>", unsafe_allow_html=True)
    else:
        if topic_map.empty:
            st.warning("topic_label_map.csv ada tapi kosong / tidak valid. Pastikan kolom: sentimen, topic_id, label, action.")
        else:
            st.markdown("<div class='small-note'>✅ topic_label_map.csv terdeteksi (siap untuk label & rekomendasi aksi).</div>", unsafe_allow_html=True)

    # KPI GRID (restore UI)
    st.markdown(
        f"""
        <div class="kpi-grid">
          <div class="kpi">
            <div class="title">Total Ulasan</div>
            <div class="value">{total_data:,}</div>
            <div class="pill">distribusi_rating.csv</div>
          </div>
          <div class="kpi">
            <div class="title">Rata-rata Rating</div>
            <div class="value">{avg_rating:.2f}</div>
            <div class="pill">weighted avg</div>
          </div>
          <div class="kpi">
            <div class="title">% Positif</div>
            <div class="value">{(pos_pct if not np.isnan(pos_pct) else 0):.2f}%</div>
            <div class="pill">distribusi_sentimen.csv</div>
          </div>
          <div class="kpi">
            <div class="title">% Negatif</div>
            <div class="value">{(neg_pct if not np.isnan(neg_pct) else 0):.2f}%</div>
            <div class="pill">distribusi_sentimen.csv</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🧩 Topic Modeling", "🧑‍💼 People Analytics"])

    # ---------- OVERVIEW ----------
    with tab1:
        card_open("Distribusi Rating", "Ringkasan jumlah ulasan per rating")
        if err_r:
            st.warning(err_r)
        else:
            fig = px.bar(rating_df, x=x_r, y=y_r, template=PX_TEMPLATE)
            fig.update_layout(height=360, xaxis_title=str(x_r), yaxis_title=str(y_r))
            fig.update_xaxes(**AXIS)
            fig.update_yaxes(**AXIS)
            st.plotly_chart(fig, use_container_width=True)
        card_close()

        card_open("Distribusi Sentimen", "Ringkasan jumlah ulasan per sentimen")
        if err_s:
            st.warning(err_s)
        else:
            fig2 = px.pie(sent_df, names=x_s, values=y_s, template=PX_TEMPLATE)
            fig2.update_layout(height=360)
            st.plotly_chart(fig2, use_container_width=True)
        card_close()

    # ---------- TOPIC MODELING ----------
    with tab2:
        card_open("Ringkasan Topik NEGATIF", "Top words tiap topik (NEGATIF)")
        st.dataframe(top_neg, use_container_width=True)
        card_close()

        card_open("Ringkasan Topik POSITIF", "Top words tiap topik (POSITIF)")
        st.dataframe(top_pos, use_container_width=True)
        card_close()

        card_open("Data Topic Full (NEG & POS)", "Preview (head) untuk analisis lanjutan")
        st.write("NEG Full:")
        st.dataframe(top_neg_full.head(50), use_container_width=True)
        st.write("POS Full:")
        st.dataframe(top_pos_full.head(50), use_container_width=True)
        card_close()

    # ---------- PEOPLE ANALYTICS ----------
    with tab3:
        card_open("Matriks Prioritas Masalah", "Frequency × Impact (rating) untuk prioritas perbaikan")
        st.dataframe(people_sum, use_container_width=True)
        card_close()

        if not topic_map.empty:
            card_open("Mapping Label Topik & Rekomendasi Aksi", "Interpretasi analis (bukan output model)")
            st.dataframe(topic_map, use_container_width=True)
            card_close()

        card_open("Evidence: Rating ≥ 4 tapi ada keluhan", "Membuktikan rating tinggi bisa tetap mengandung keluhan")
        st.dataframe(keluhan4_df.head(50), use_container_width=True)
        card_close()

        card_open("Evidence: Rating ≤ 2 (Negatif)", "Kumpulan ulasan rating rendah untuk analisis keluhan dominan")
        st.dataframe(rating2_df.head(50), use_container_width=True)
        card_close()

    st.caption("© Dashboard untuk Konversi: Analitik Media Sosial & People Analytics (UI restored, siap lanjut Deployment Analytics).")

# =========================
# MAIN
# =========================
if not st.session_state.login:
    login_page()
else:
    dashboard()
