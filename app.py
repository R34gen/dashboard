import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

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
# FILE HELPERS
# =========================
DATA = Path("data")

def pick_file(*names: str) -> Path:
    for n in names:
        p = DATA / n
        if p.exists():
            return p
    st.error("File tidak ditemukan di folder data/. Pastikan file ada.")
    st.write("Dicari:", list(names))
    st.stop()

def pick_file_optional(*names: str) -> Path | None:
    """Cari file di folder data/ tanpa menghentikan app kalau tidak ada."""
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
# LOAD FILES (fitur lama tetap)
# =========================
p_rating    = pick_file("distribusi_rating.csv")
p_sentiment = pick_file("distribusi_sentimen.csv")

p_top_neg    = pick_file("ringkasan_topik_negatif.csv")
p_top_neg_f  = pick_file("hasil_topic_negatif_full.csv")
p_top_pos    = pick_file("ringkasan_topik_positif.csv")
p_top_pos_f  = pick_file("hasil_topic_positif_full.csv")

p_people_sum = pick_file("people_analytics_summary.csv", "people_analytics_summary (1).csv")
p_keluhan4   = pick_file("rating_4keatas_tapi_keluhan.csv", "rating_4keatas_tapi_keluhan (1).csv")
p_rating2    = pick_file("rating_2kebawah_semua_ulasan.csv")

# Deployment analytics (opsional)
p_dataset_final = pick_file_optional("dataset_final.csv", "dataset_final (1).csv")
dataset_final_raw = load_dataset_final(p_dataset_final) if p_dataset_final else pd.DataFrame()
dataset_final, dataset_schema, dataset_err = (pd.DataFrame(), {}, None)
if not dataset_final_raw.empty:
    dataset_final, dataset_schema, dataset_err = standardize_dataset(dataset_final_raw)

# Topic label map (opsional)
p_topic_map = pick_file_optional("topic_label_map.csv", "topic_label_map (1).csv")
topic_map = load_topic_label_map(p_topic_map) if p_topic_map else pd.DataFrame()

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
# STYLING
# =========================
PX_TEMPLATE = "plotly_white"

st.markdown(
    """
<style>
.card {background:#ffffff;border:1px solid #eee;border-radius:14px;padding:18px;margin-bottom:14px;box-shadow:0 2px 10px rgba(0,0,0,0.03);}
.card-title {font-weight:700;font-size:18px;margin-bottom:4px;}
.card-sub {color:#666;font-size:13px;margin-top:-2px;margin-bottom:10px;}
hr {border:0;border-top:1px solid #eee;margin:18px 0;}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# AUTH UI
# =========================
def login_page():
    st.title("🔐 Login (Demo)")
    st.write("Masukkan username & password untuk masuk dashboard.")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if USERS.get(u) == p:
            st.session_state.login = True
            st.success("Login berhasil!")
            st.rerun()  # ✅ FIX: ganti experimental_rerun
        else:
            st.error("Username / password salah.")

# =========================
# DASHBOARD
# =========================
def dashboard():
    st.title("📊 Dashboard Analitik Medsos & People Analytics")

    # status dataset_final (opsional)
    if p_dataset_final is None:
        st.caption("ℹ️ dataset_final.csv belum ada (opsional). Fitur lama tetap berjalan.")
    elif dataset_err:
        st.warning(f"dataset_final.csv terdeteksi, tapi tidak valid: {dataset_err}")
    else:
        st.caption("✅ dataset_final.csv terdeteksi & skema kolom berhasil distandarkan (siap untuk deployment analytics).")

    # status topic map (opsional)
    if p_topic_map is None:
        st.caption("ℹ️ topic_label_map.csv belum ada (opsional).")
    else:
        if topic_map.empty:
            st.warning("topic_label_map.csv ada tapi kosong / tidak valid. Pastikan kolom: sentimen, topic_id, label, action.")
        else:
            st.caption("✅ topic_label_map.csv terdeteksi (siap untuk label & rekomendasi aksi).")

    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🧩 Topic Modeling", "🧑‍💼 People Analytics"])

    # ---------- OVERVIEW ----------
    with tab1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Distribusi Rating</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-sub'>Ringkasan jumlah ulasan per rating</div>", unsafe_allow_html=True)

        r_col = safe_col(rating_df, "rating", "Rating", "rate", "bintang")
        c_col = safe_col(rating_df, "count", "jumlah", "freq")

        if r_col and c_col:
            fig = px.bar(rating_df, x=r_col, y=c_col, template=PX_TEMPLATE)
            fig.update_layout(height=350, xaxis_title="Rating", yaxis_title="Jumlah")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Kolom distribusi rating tidak sesuai format (rating/count).")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Distribusi Sentimen</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-sub'>Ringkasan jumlah ulasan per sentimen</div>", unsafe_allow_html=True)

        s_col = safe_col(sent_df, "sentimen", "sentiment", "label")
        c2_col = safe_col(sent_df, "count", "jumlah", "freq")

        if s_col and c2_col:
            fig2 = px.pie(sent_df, names=s_col, values=c2_col, template=PX_TEMPLATE)
            fig2.update_layout(height=350)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Kolom distribusi sentimen tidak sesuai format (sentimen/count).")

        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- TOPIC MODELING ----------
    with tab2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Ringkasan Topik NEGATIF</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-sub'>Top words tiap topik (NEGATIF)</div>", unsafe_allow_html=True)
        st.dataframe(top_neg, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Ringkasan Topik POSITIF</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-sub'>Top words tiap topik (POSITIF)</div>", unsafe_allow_html=True)
        st.dataframe(top_pos, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Data Topic Full (NEG & POS)</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-sub'>Jika ingin analisis lanjutan di aplikasi</div>", unsafe_allow_html=True)

        st.write("NEG Full:")
        st.dataframe(top_neg_full.head(50), use_container_width=True)
        st.write("POS Full:")
        st.dataframe(top_pos_full.head(50), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------- PEOPLE ANALYTICS ----------
    with tab3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Matriks Prioritas Masalah</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-sub'>Frequency × Impact (rating) untuk prioritas perbaikan</div>", unsafe_allow_html=True)
        st.dataframe(people_sum, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if not topic_map.empty:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-title'>Mapping Label Topik & Rekomendasi Aksi</div>", unsafe_allow_html=True)
            st.markdown("<div class='card-sub'>Interpretasi analis (bukan output model).</div>", unsafe_allow_html=True)
            st.dataframe(topic_map, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Evidence: Rating ≥ 4 tapi ada keluhan</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-sub'>Membuktikan ulasan rating tinggi bisa tetap mengandung keluhan</div>", unsafe_allow_html=True)
        st.dataframe(keluhan4_df.head(50), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Evidence: Rating ≤ 2 (Negatif)</div>", unsafe_allow_html=True)
        st.markdown("<div class='card-sub'>Kumpulan ulasan rating rendah untuk analisis keluhan dominan</div>", unsafe_allow_html=True)
        st.dataframe(rating2_df.head(50), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.caption("© Dashboard untuk Konversi: Analitik Media Sosial & People Analytics (dan siap untuk Deployment Analytics).")


# =========================
# MAIN
# =========================
if not st.session_state.login:
    login_page()
else:
    dashboard()
