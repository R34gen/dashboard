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
USERS = {"mahasiswa": "upnvjt"}
if "login" not in st.session_state:
    st.session_state.login = False

# =========================
# FILES + HELPERS
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

def as_lower(s):
    return str(s).strip().lower()

# =========================
# LOAD FILES (sesuai revisi kamu)
# =========================
p_rating     = pick_file("distribusi_rating.csv")
p_sentiment  = pick_file("distribusi_sentimen.csv", "distribusi_sentimen (1).csv")

p_top_neg    = pick_file("ringkasan_topik_negatif.csv")
p_top_neg_f  = pick_file("hasil_topic_negatif_full.csv")

p_top_pos    = pick_file("ringkasan_topik_positif.csv")
p_top_pos_f  = pick_file("hasil_topic_positif_full.csv")

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
# UI THEME (FIX: background soft, font tetap gelap)
# =========================
st.markdown("""
<style>
:root{
  --bg:#F5F7FB;
  --surface:#FFFFFF;
  --border:rgba(15,23,42,0.10);
  --shadow:0 10px 30px rgba(15,23,42,0.06);

  --text:#0F172A;
  --muted:#334155;
  --subtle:#64748B;

  --brand:#1E3A8A;   /* navy */
  --brand2:#2563EB;  /* blue */
  --soft:rgba(37,99,235,0.08);

  --pos:#16A34A;     /* green */
  --neg:#DC2626;     /* red */
  --neu:#94A3B8;     /* gray */
}

[data-testid="stAppViewContainer"]{ background:var(--bg); }
html, body, [class*="css"]{ color:var(--text) !important; font-family:Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial; }

.card{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:22px;
  padding:18px;
  box-shadow:var(--shadow);
  margin-bottom:14px;
}
.center{ text-align:center; }
.card-title{ font-size:18px; font-weight:900; color:var(--text) !important; margin:0 0 6px 0; }
.card-sub{ font-size:13px; color:var(--subtle) !important; margin:0; }

.badges{ display:flex; justify-content:center; flex-wrap:wrap; gap:8px; margin-top:10px; }
.badge{
  font-size:12px; font-weight:800;
  padding:7px 12px; border-radius:999px;
  background:var(--soft);
  border:1px solid rgba(30,58,138,0.18);
  color:var(--brand) !important;
}

.kpi-grid{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin-bottom:12px; }
.kpi{
  border-radius:18px; padding:16px;
  background:linear-gradient(135deg, rgba(30,58,138,.98), rgba(37,99,235,.92));
  border:1px solid rgba(15,23,42,0.10);
  position:relative; overflow:hidden;
}
.kpi:before{
  content:""; position:absolute; right:-60px; top:-60px;
  width:150px; height:150px; border-radius:999px;
  background:rgba(255,255,255,0.14);
}
.kpi .title{ font-size:13px; font-weight:900; color:rgba(255,255,255,0.92) !important; }
.kpi .value{ font-size:26px; font-weight:950; color:#fff !important; margin-top:4px; }
.kpi .pill{
  display:inline-block; margin-top:8px;
  font-size:12px; font-weight:800;
  padding:4px 9px; border-radius:999px;
  background:rgba(255,255,255,0.14);
  color:rgba(255,255,255,0.92) !important;
}

.insight{
  background:#FFFFFF;
  border:1px solid rgba(15,23,42,0.10);
  border-left:5px solid var(--brand);
  border-radius:18px;
  padding:14px 14px;
}
.insight ul{ margin: 0.4rem 0 0 1.1rem; color:var(--muted) !important; }
.insight b{ color:var(--text) !important; }

.stButton>button{
  border-radius:14px !important;
  background:var(--brand) !important;
  color:#fff !important;
  border:1px solid rgba(15,23,42,0.10) !important;
  padding:10px 14px !important;
}
.stButton>button:hover{ background:#162E6E !important; }

@media (max-width:768px){
  .block-container{ padding:.8rem .8rem; }
  .kpi-grid{ grid-template-columns:1fr; }
}
</style>
""", unsafe_allow_html=True)

# =========================
# PLOTLY STYLE (consistent & proper)
# =========================
PX_TEMPLATE = "simple_white"
AXIS = dict(showgrid=True, gridcolor="rgba(15,23,42,0.08)", zeroline=False)

# =========================
# KPI COMPUTATION (from your CSV)
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
# DATA-DRIVEN INSIGHTS (NO ASSUMPTION)
# =========================
def rating_extremes_insight():
    """Return: (top_rating, top_count, share_extremes, count_r1, count_r5) if possible."""
    if not (col_r_rate and col_r_count):
        return None
    tmp = rating_df[[col_r_rate, col_r_count]].copy()
    tmp[col_r_rate] = pd.to_numeric(tmp[col_r_rate], errors="coerce")
    tmp[col_r_count] = pd.to_numeric(tmp[col_r_count], errors="coerce").fillna(0)

    top_row = tmp.sort_values(col_r_count, ascending=False).head(1)
    top_rating = int(top_row[col_r_rate].iloc[0]) if not top_row.empty else None
    top_count = int(top_row[col_r_count].iloc[0]) if not top_row.empty else None

    # share extremes (1 and 5) if those exist
    r1 = tmp[tmp[col_r_rate] == 1][col_r_count].sum()
    r5 = tmp[tmp[col_r_rate] == 5][col_r_count].sum()
    share_ext = float((r1 + r5) / max(tmp[col_r_count].sum(), 1) * 100)

    return top_rating, top_count, share_ext, int(r1), int(r5)

def top_topics_insight(df, label_hint):
    """Return top-3 topics with counts from ringkasan_topik_*.csv."""
    topic_col = safe_col(df, "topic_label", "topik", "topic")
    cnt_col   = safe_col(df, "jumlah_ulasan", "jumlah", "count", "freq")
    if not (topic_col and cnt_col):
        return []
    tmp = df[[topic_col, cnt_col]].copy()
    tmp[cnt_col] = pd.to_numeric(tmp[cnt_col], errors="coerce").fillna(0)
    tmp = tmp.sort_values(cnt_col, ascending=False).head(3)
    return [(str(r[topic_col]), int(r[cnt_col])) for _, r in tmp.iterrows()]

rating_ins = rating_extremes_insight()
top3_pos = top_topics_insight(top_pos, "positif")
top3_neg = top_topics_insight(top_neg, "negatif")

n_keluhan4 = int(len(keluhan4_df))
n_rating2  = int(len(rating2_df))

# =========================
# UI COMPONENTS
# =========================
def header_center(title: str, subtitle: str):
    st.markdown("<div class='card center'>", unsafe_allow_html=True)
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
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    u = st.text_input("Username", placeholder="contoh: mahasiswa")
    p = st.text_input("Password", type="password", placeholder="contoh: upnvjt")
    if st.button("Login", use_container_width=True):
        if USERS.get(u) == p:
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Username atau password salah.")
    st.caption("Login demo. Untuk produksi gunakan Streamlit Secrets.")
    st.markdown("</div>", unsafe_allow_html=True)

def insight_block(title, bullets):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='card-title'>{title}</div>", unsafe_allow_html=True)
    st.markdown("<div class='insight'>", unsafe_allow_html=True)
    st.markdown("<ul>", unsafe_allow_html=True)
    for b in bullets:
        st.markdown(f"<li>{b}</li>", unsafe_allow_html=True)
    st.markdown("</ul></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def dashboard():
    header_center("People Analytics Dashboard", "Overview • Topic Modeling • People Analytics Evidence")

    # KPI cards
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
            <div class="pill">weighted average</div>
          </div>
          <div class="kpi">
            <div class="title">Sentimen Negatif</div>
            <div class="value">{pct_negatif:.1f}%</div>
            <div class="pill">Pos {pct_positif:.1f}% • Net {pct_netral:.1f}%</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🧩 Topic Modeling", "🧑‍💼 People Analytics"])

    # =========================
    # OVERVIEW TAB (VISUAL PROPER + INSIGHTS)
    # =========================
    with tab1:
        # Visual card
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Distribusi Rating & Sentimen</div>", unsafe_allow_html=True)
        st.markdown("<p class='card-sub'>Visual dibuat konsisten (template putih) agar mudah dibaca.</p>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        # Rating (horizontal bar)
        with c1:
            if col_r_rate and col_r_count:
                tmp = rating_df.copy()
                tmp[col_r_rate] = pd.to_numeric(tmp[col_r_rate], errors="coerce")
                tmp[col_r_count] = pd.to_numeric(tmp[col_r_count], errors="coerce").fillna(0)

                fig = px.bar(
                    tmp.sort_values(col_r_rate),
                    x=col_r_count, y=col_r_rate,
                    orientation="h",
                    text=col_r_count,
                    template=PX_TEMPLATE,
                    color_discrete_sequence=["#1E3A8A"]
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10),
                                  xaxis_title="Jumlah Ulasan", yaxis_title="Rating")
                fig.update_xaxes(**AXIS); fig.update_yaxes(**AXIS)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Kolom rating/jumlah_ulasan tidak ditemukan pada distribusi_rating.csv")

        # Sentimen (donut with meaning colors)
        with c2:
            if col_s_name:
                val_col = col_s_count if col_s_count else col_s_pct
                fig = px.pie(
                    sent_df,
                    names=col_s_name,
                    values=val_col,
                    hole=0.60,
                    template=PX_TEMPLATE,
                    color=col_s_name,
                    color_discrete_map={
                        "positif": "#16A34A",
                        "netral": "#94A3B8",
                        "negatif": "#DC2626",
                        "Positif": "#16A34A",
                        "Netral": "#94A3B8",
                        "Negatif": "#DC2626",
                    }
                )
                fig.update_layout(
                    height=380,
                    margin=dict(l=10, r=10, t=40, b=10),
                    annotations=[dict(
                        text=f"{pct_negatif:.1f}%<br>Negatif",
                        x=0.5, y=0.5,
                        showarrow=False,
                        font=dict(size=18, color="#0F172A")
                    )]
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Kolom sentimen tidak ditemukan pada distribusi_sentimen.csv")

        st.markdown("</div>", unsafe_allow_html=True)

        # Data-driven insights (NO assumption)
        bullets = []
        if rating_ins:
            top_rating, top_count, share_ext, r1, r5 = rating_ins
            bullets.append(f"<b>Rating paling banyak</b> adalah <b>{top_rating}</b> dengan <b>{top_count:,}</b> ulasan (sumber: distribusi_rating.csv).")
            bullets.append(f"Total ulasan pada rating <b>1</b> = <b>{r1:,}</b> dan rating <b>5</b> = <b>{r5:,}</b>; gabungan rating ekstrem (1 & 5) = <b>{share_ext:.1f}%</b> dari total (sumber: distribusi_rating.csv).")
        bullets.append(f"Proporsi sentimen: <b>negatif {pct_negatif:.1f}%</b>, positif {pct_positif:.1f}%, netral {pct_netral:.1f}% (sumber: distribusi_sentimen.csv).")
        insight_block("Key Findings (berdasarkan angka)", bullets)

    # =========================
    # TOPIC MODELING TAB (TOP-N + INSIGHT TOP TOPICS)
    # =========================
    with tab2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>Ringkasan Topik</div>", unsafe_allow_html=True)
        st.markdown("<p class='card-sub'>Topik ditampilkan dari ringkasan, dan detailnya bisa dibuka dari file full.</p>", unsafe_allow_html=True)

        pos_topic = safe_col(top_pos, "topic_label", "topik", "topic")
        pos_cnt   = safe_col(top_pos, "jumlah_ulasan", "jumlah", "count", "freq")
        neg_topic = safe_col(top_neg, "topic_label", "topik", "topic")
        neg_cnt   = safe_col(top_neg, "jumlah_ulasan", "jumlah", "count", "freq")

        topn = st.slider("Top-N topik", 5, 20, 10)

        c1, c2 = st.columns(2)
        with c1:
            if pos_topic and pos_cnt:
                tmp = top_pos.copy()
                tmp[pos_cnt] = pd.to_numeric(tmp[pos_cnt], errors="coerce").fillna(0)
                fig = px.bar(
                    tmp.head(topn).sort_values(pos_cnt),
                    x=pos_cnt, y=pos_topic,
                    orientation="h",
                    template=PX_TEMPLATE,
                    color_discrete_sequence=["#2563EB"]
                )
                fig.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10),
                                  xaxis_title="Jumlah kemunculan", yaxis_title="")
                fig.update_xaxes(**AXIS); fig.update_yaxes(**AXIS)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Kolom topik/jumlah tidak ditemukan pada ringkasan_topik_positif.csv")

            with st.expander("Detail: hasil_topic_positif_full.csv"):
                st.dataframe(top_pos_full, use_container_width=True)

        with c2:
            if neg_topic and neg_cnt:
                tmp = top_neg.copy()
                tmp[neg_cnt] = pd.to_numeric(tmp[neg_cnt], errors="coerce").fillna(0)
                fig = px.bar(
                    tmp.head(topn).sort_values(neg_cnt),
                    x=neg_cnt, y=neg_topic,
                    orientation="h",
                    template=PX_TEMPLATE,
                    color_discrete_sequence=["#DC2626"]
                )
                fig.update_layout(height=420, margin=dict(l=10, r=10, t=40, b=10),
                                  xaxis_title="Jumlah kemunculan", yaxis_title="")
                fig.update_xaxes(**AXIS); fig.update_yaxes(**AXIS)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Kolom topik/jumlah tidak ditemukan pada ringkasan_topik_negatif.csv")

            with st.expander("Detail: hasil_topic_negatif_full.csv"):
                st.dataframe(top_neg_full, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Topic insights strictly from top-3
        bullets = []
        if top3_pos:
            bullets.append("Top 3 topik positif (ringkasan): " + ", ".join([f"<b>{t}</b> ({c:,})" for t, c in top3_pos]) + ".")
        if top3_neg:
            bullets.append("Top 3 topik negatif (ringkasan): " + ", ".join([f"<b>{t}</b> ({c:,})" for t, c in top3_neg]) + ".")
        if not bullets:
            bullets.append("Tidak bisa membuat ringkasan topik karena nama kolom ringkasan tidak terdeteksi.")
        insight_block("Insight Topic Modeling (berdasarkan ringkasan topik)", bullets)

    # =========================
    # PEOPLE ANALYTICS TAB (EVIDENCE COUNTS + SUMMARY TABLE)
    # =========================
    with tab3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>People Analytics Summary</div>", unsafe_allow_html=True)
        st.markdown("<p class='card-sub'>Ringkasan dari people_analytics_summary.csv + evidence ulasan ekstrem.</p>", unsafe_allow_html=True)

        st.dataframe(people_sum, use_container_width=True)

        st.markdown("<hr style='border:none; border-top:1px solid rgba(15,23,42,0.10); margin:14px 0;'/>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Rating ≥ 4 tapi keluhan**")
            st.caption(f"Jumlah baris evidence: {n_keluhan4:,} (sumber: rating_4keatas_tapi_keluhan.csv)")
            st.dataframe(keluhan4_df.head(30), use_container_width=True)

        with c2:
            st.markdown("**Rating ≤ 2 (semua ulasan)**")
            st.caption(f"Jumlah baris evidence: {n_rating2:,} (sumber: rating_2kebawah_semua_ulasan.csv)")
            st.dataframe(rating2_df.head(30), use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Evidence insight (purely counts + presence)
        bullets = [
            f"Terdapat <b>{n_keluhan4:,}</b> baris evidence untuk kategori <b>rating ≥ 4 namun mengandung keluhan</b> (rating_4keatas_tapi_keluhan.csv).",
            f"Terdapat <b>{n_rating2:,}</b> baris evidence untuk kategori <b>rating ≤ 2</b> (rating_2kebawah_semua_ulasan.csv).",
            "Ini menunjukkan bahwa dataset menyediakan contoh teks untuk dua kondisi ekstrem (positif-tinggi tapi keluhan, dan negatif-rendah)."
        ]
        insight_block("Insight People Analytics (berdasarkan evidence)", bullets)

    st.caption(f"© {datetime.now().year} • People Analytics • Data aktual (CSV) • UI/UX final")

# =========================
# ROUTER
# =========================
if not st.session_state.login:
    login_page()
else:
    dashboard()
