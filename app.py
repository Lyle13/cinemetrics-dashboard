import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  PAGE CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CineMetrics | Film Analytics",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL CSS — cinematic dark theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Google Font ── */
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');

  /* ── Base ── */
  html, body, [class*="css"] {
      background-color: #0D0D0D;
      color: #E8E8E8;
      font-family: 'Inter', sans-serif;
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
      background: linear-gradient(180deg, #141414 0%, #0D0D0D 100%);
      border-right: 1px solid #2A2A2A;
  }
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] .stMarkdown p {
      color: #AAAAAA !important;
      font-size: 0.8rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
  }

  /* ── KPI card ── */
  .kpi-card {
      background: linear-gradient(135deg, #1A1A1A 0%, #141414 100%);
      border: 1px solid #2A2A2A;
      border-radius: 12px;
      padding: 20px 24px;
      text-align: center;
  }
  .kpi-label {
      font-family: 'Inter', sans-serif;
      font-size: 0.7rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: #888888;
      margin-bottom: 6px;
  }
  .kpi-value {
      font-family: 'Playfair Display', serif;
      font-size: 2rem;
      font-weight: 700;
      color: #E8C87A;
      line-height: 1;
  }
  .kpi-sub {
      font-size: 0.72rem;
      color: #666666;
      margin-top: 6px;
  }

  /* ── Section header ── */
  .section-header {
      font-family: 'Playfair Display', serif;
      font-size: 1.1rem;
      font-weight: 600;
      color: #E8C87A;
      border-left: 3px solid #E8C87A;
      padding-left: 10px;
      margin: 24px 0 14px 0;
  }

  /* ── Insight box ── */
  .insight-box {
      background: linear-gradient(135deg, #1C160A 0%, #16120A 100%);
      border: 1px solid #E8C87A44;
      border-left: 4px solid #E8C87A;
      border-radius: 10px;
      padding: 20px 24px;
      margin: 20px 0;
  }
  .insight-title {
      font-family: 'Playfair Display', serif;
      font-size: 1rem;
      color: #E8C87A;
      margin-bottom: 8px;
      letter-spacing: 0.04em;
  }
  .insight-text {
      font-size: 0.88rem;
      color: #BBBBBB;
      line-height: 1.7;
  }
  .insight-text strong { color: #E8C87A; }

  /* ── Attribution ── */
  .attribution {
      font-size: 0.7rem;
      color: #555555;
      text-align: center;
      border-top: 1px solid #1E1E1E;
      padding-top: 16px;
      margin-top: 40px;
      letter-spacing: 0.05em;
  }
  .attribution a { color: #E8C87A88; text-decoration: none; }
  .attribution a:hover { color: #E8C87A; }

  /* ── Divider ── */
  hr { border-color: #1E1E1E; }

  /* ── Metric overrides ── */
  [data-testid="stMetric"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATA LOADING & CLEANING
# ─────────────────────────────────────────────
@st.cache_data
def load_and_clean():
    df = pd.read_csv("imdb_top_1000.csv", encoding="utf-8")

    # ── Strip whitespace ──
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].astype(str).str.strip()

    # ── Released_Year ──
    df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce")
    df = df[df["Released_Year"].between(1920, 2025)]

    # ── Runtime → numeric (minutes) ──
    df["Runtime_min"] = (
        df["Runtime"].str.replace(" min", "", regex=False)
        .str.replace(",", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )

    # ── Gross → numeric ──
    df["Gross_USD"] = (
        df["Gross"].str.replace(",", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )

    # ── Rating & score ──
    df["IMDB_Rating"] = pd.to_numeric(df["IMDB_Rating"], errors="coerce")
    df["Meta_score"] = pd.to_numeric(df["Meta_score"], errors="coerce")
    df["No_of_Votes"] = (
        df["No_of_Votes"].str.replace(",", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )

    # ── Primary genre (first listed) ──
    df["Primary_Genre"] = df["Genre"].str.split(",").str[0].str.strip()

    # ── Decade ──
    df["Decade"] = (df["Released_Year"] // 10 * 10).astype("Int64").astype(str) + "s"

    # ── Drop rows missing core metrics ──
    df = df.dropna(subset=["IMDB_Rating", "Released_Year", "Primary_Genre"])

    # ── Remove duplicates ──
    df = df.drop_duplicates(subset=["Series_Title", "Released_Year"])

    return df.reset_index(drop=True)


df_full = load_and_clean()

# ─────────────────────────────────────────────
#  SIDEBAR — FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 style='font-family:Playfair Display,serif;color:#E8C87A;font-size:1.3rem;"
        "margin-bottom:4px;'>🎬 CineMetrics</h2>"
        "<p style='color:#666;font-size:0.72rem;margin-top:0;letter-spacing:0.08em;'>FILM ANALYTICS DASHBOARD</p>"
        "<hr style='border-color:#2A2A2A;margin:12px 0 20px 0;'>",
        unsafe_allow_html=True,
    )

    st.markdown("**RELEASE YEAR**")
    year_min, year_max = int(df_full["Released_Year"].min()), int(df_full["Released_Year"].max())
    year_range = st.slider(
        "Year range", year_min, year_max, (1950, year_max), label_visibility="collapsed"
    )

    st.markdown("**MIN IMDB RATING**")
    min_rating = st.slider("Min rating", 5.0, 9.5, 7.0, 0.1, label_visibility="collapsed")

    st.markdown("**GENRE**")
    all_genres = sorted(df_full["Primary_Genre"].unique())
    selected_genres = st.multiselect(
        "Genres", all_genres, default=all_genres, label_visibility="collapsed"
    )

    st.markdown("**GROSS EARNINGS FILTER**")
    show_with_gross_only = st.toggle("Only films with known box office", value=False)

    st.markdown("<hr style='border-color:#2A2A2A;margin:20px 0;'>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#444;font-size:0.65rem;text-align:center;'>Lil Benedict Herrera<br>"
        "CIS 220 — Business Analytics<br>WVSU, 2026</p>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
#  APPLY FILTERS
# ─────────────────────────────────────────────
df = df_full.copy()
df = df[df["Released_Year"].between(*year_range)]
df = df[df["IMDB_Rating"] >= min_rating]
if selected_genres:
    df = df[df["Primary_Genre"].isin(selected_genres)]
if show_with_gross_only:
    df = df[df["Gross_USD"].notna()]

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown(
    "<h1 style='font-family:Playfair Display,serif;font-size:2.6rem;font-weight:700;"
    "color:#E8C87A;margin-bottom:0;letter-spacing:0.03em;'>🎬 CineMetrics</h1>"
    "<p style='color:#666;font-size:0.8rem;letter-spacing:0.14em;margin-top:4px;'>IMDB FILM ANALYTICS · TOP-RATED CINEMA ·</p>",
    unsafe_allow_html=True,
)
st.markdown("<hr style='border-color:#1E1E1E;margin:12px 0 24px 0;'>", unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️ No films match the current filters. Try widening your selection.")
    st.stop()

# ─────────────────────────────────────────────
#  KPI ROW
# ─────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

total_films   = len(df)
avg_rating    = df["IMDB_Rating"].mean()
avg_runtime   = df["Runtime_min"].dropna().mean()
top_genre     = df["Primary_Genre"].value_counts().idxmax()
top_director  = df["Director"].value_counts().idxmax()
total_gross   = df["Gross_USD"].sum()

def kpi(label, value, sub=""):
    return f"""<div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>"""

with k1:
    st.markdown(kpi("Total Films", f"{total_films:,}", f"{year_range[0]}–{year_range[1]}"), unsafe_allow_html=True)
with k2:
    st.markdown(kpi("Avg IMDb Rating", f"{avg_rating:.2f}", "out of 10.0"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi("Avg Runtime", f"{avg_runtime:.0f} min", "per film"), unsafe_allow_html=True)
with k4:
    st.markdown(kpi("Top Genre", top_genre, "by film count"), unsafe_allow_html=True)
with k5:
    gross_str = f"${total_gross/1e9:.1f}B" if total_gross >= 1e9 else f"${total_gross/1e6:.0f}M" if total_gross >= 1e6 else "N/A"
    st.markdown(kpi("Combined Gross", gross_str, "known box office"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY THEME DEFAULTS
# ─────────────────────────────────────────────
GOLD   = "#E8C87A"
BG     = "#0D0D0D"
CARD   = "#141414"
GRID   = "#1E1E1E"
TEXT   = "#AAAAAA"
ACCENT = "#CF6679"

LAYOUT_BASE = dict(
    paper_bgcolor=CARD,
    plot_bgcolor=CARD,
    font_color=TEXT,
    font_family="Inter",
    title_font_family="Playfair Display",
    title_font_color=GOLD,
    margin=dict(t=50, b=40, l=40, r=20),
)


# ─────────────────────────────────────────────
#  ROW 1 — Treemap + Violin
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Genre Landscape</div>', unsafe_allow_html=True)
c1, c2 = st.columns([1.2, 1])

with c1:
    genre_counts = df["Primary_Genre"].value_counts().reset_index()
    genre_counts.columns = ["Genre", "Count"]

    fig_tree = px.treemap(
        genre_counts,
        path=["Genre"],
        values="Count",
        color="Count",
        color_continuous_scale=[[0, "#1A1A1A"], [0.5, "#7A5A1A"], [1, GOLD]],
        title="Film Count by Genre",
    )
    fig_tree.update_layout(**LAYOUT_BASE, coloraxis_showscale=False)
    fig_tree.update_traces(
        textfont_size=13,
        marker_line_color=BG,
        marker_line_width=2,
    )
    st.plotly_chart(fig_tree, use_container_width=True, config={"displayModeBar": False})

with c2:
    top5_genres = df["Primary_Genre"].value_counts().head(6).index.tolist()
    df_v = df[df["Primary_Genre"].isin(top5_genres)]

    fig_violin = go.Figure()
    colors_violin = [
        (GOLD,    "rgba(232,200,122,0.25)"),
        (ACCENT,  "rgba(207,102,121,0.25)"),
        ("#5C9E82","rgba(92,158,130,0.25)"),
        ("#7A8FC2","rgba(122,143,194,0.25)"),
        ("#C28F7A","rgba(194,143,122,0.25)"),
        ("#9A7AC2","rgba(154,122,194,0.25)"),
    ]

    for i, genre in enumerate(top5_genres):
        g_df = df_v[df_v["Primary_Genre"] == genre]["IMDB_Rating"]
        line_c, fill_c = colors_violin[i % len(colors_violin)]
        fig_violin.add_trace(go.Violin(
            y=g_df,
            name=genre,
            line_color=line_c,
            fillcolor=fill_c,
            box_visible=True,
            meanline_visible=True,
            points=False,
        ))

    fig_violin.update_layout(
        **LAYOUT_BASE,
        title="IMDb Rating Distribution (Top Genres)",
        yaxis_title="IMDb Rating",
        showlegend=False,
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        xaxis=dict(gridcolor=GRID),
    )
    st.plotly_chart(fig_violin, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────
#  KEY INSIGHT BOX
# ─────────────────────────────────────────────
median_drama = df[df["Primary_Genre"] == "Drama"]["IMDB_Rating"].median() if "Drama" in df["Primary_Genre"].values else None
median_action = df[df["Primary_Genre"] == "Action"]["IMDB_Rating"].median() if "Action" in df["Primary_Genre"].values else None

top_dir_count = df["Director"].value_counts().iloc[0]
top_dir_name  = df["Director"].value_counts().index[0]

highest_gross_row = df.dropna(subset=["Gross_USD"]).sort_values("Gross_USD", ascending=False).iloc[0] if not df.dropna(subset=["Gross_USD"]).empty else None
highest_gross_title = highest_gross_row["Series_Title"] if highest_gross_row is not None else "N/A"
highest_gross_val   = f"${highest_gross_row['Gross_USD']/1e6:.0f}M" if highest_gross_row is not None else "N/A"

nolan_df = df[df["Director"].str.contains("Nolan", na=False)]
nolan_avg = nolan_df["IMDB_Rating"].mean() if not nolan_df.empty else None

insight_parts = []
if median_drama and median_action:
    diff = round(median_drama - median_action, 2)
    insight_parts.append(
        f"<strong>Drama outrates Action by {diff} points</strong> (median IMDb) — suggesting critics and "
        f"audiences consistently reward narrative depth over spectacle in top-tier cinema."
    )
if nolan_avg:
    insight_parts.append(
        f"<strong>Christopher Nolan</strong> commands an average IMDb rating of "
        f"<strong>{nolan_avg:.2f}</strong> across {len(nolan_df)} films in this dataset — "
        f"the highest directorial floor of any prolific filmmaker here."
    )
if highest_gross_row is not None:
    insight_parts.append(
        f"<strong>{highest_gross_title}</strong> is the highest-grossing film at "
        f"<strong>{highest_gross_val}</strong>, yet it sits at a rating of "
        f"<strong>{highest_gross_row['IMDB_Rating']}</strong> — illustrating that box office dominance "
        f"and critical acclaim are not always the same story."
    )

insight_html = "<br><br>".join(insight_parts) if insight_parts else (
    "Across top-rated cinema, <strong>narrative depth consistently correlates with higher audience scores</strong>. "
    "Films with longer runtimes and complex themes tend to age better in ratings."
)

st.markdown(f"""
<div class="insight-box">
  <div class="insight-title">🔍 Key Insight</div>
  <div class="insight-text">{insight_html}</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ROW 2 — Bubble Scatter + Heatmap
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Ratings · Votes · Revenue</div>', unsafe_allow_html=True)
c3, c4 = st.columns([1.3, 1])

with c3:
    df_bubble = df.dropna(subset=["No_of_Votes", "Gross_USD"]).copy()

    if not df_bubble.empty:
        fig_bubble = px.scatter(
            df_bubble,
            x="No_of_Votes",
            y="IMDB_Rating",
            size="Gross_USD",
            color="Primary_Genre",
            hover_name="Series_Title",
            hover_data={"Released_Year": True, "Director": True,
                        "No_of_Votes": ":,", "Gross_USD": ":,.0f"},
            size_max=40,
            title="Votes vs. Rating (bubble = gross revenue)",
            color_discrete_sequence=px.colors.qualitative.Antique,
        )
        fig_bubble.update_layout(
            **LAYOUT_BASE,
            xaxis=dict(title="Number of Votes", gridcolor=GRID, type="log"),
            yaxis=dict(title="IMDb Rating", gridcolor=GRID),
            legend=dict(
                bgcolor="#0D0D0D",
                bordercolor="#2A2A2A",
                font_size=10,
                title_text="Genre",
            ),
        )
        st.plotly_chart(fig_bubble, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Enable box office filter off to see bubble chart.")

with c4:
    top_hm_genres = df["Primary_Genre"].value_counts().head(7).index.tolist()
    df_hm = df[df["Primary_Genre"].isin(top_hm_genres)]

    pivot = (
        df_hm.groupby(["Decade", "Primary_Genre"])["IMDB_Rating"]
        .mean()
        .round(2)
        .reset_index()
        .pivot(index="Primary_Genre", columns="Decade", values="IMDB_Rating")
    )

    if not pivot.empty:
        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[
                [0.0, "#1A1A1A"],
                [0.4, "#4A3010"],
                [0.7, "#9A7030"],
                [1.0, GOLD],
            ],
            text=np.where(pd.isna(pivot.values), "", pivot.values.round(1).astype(str)),
            texttemplate="%{text}",
            textfont={"size": 10, "color": "white"},
            hovertemplate="<b>%{y}</b><br>Decade: %{x}<br>Avg Rating: %{z:.2f}<extra></extra>",
            showscale=True,
            colorbar=dict(
                title="Avg Rating",
                tickfont=dict(color=TEXT),
                title_font=dict(color=TEXT),
                bgcolor=CARD,
            ),
        ))
        fig_heat.update_layout(
            **LAYOUT_BASE,
            title="Avg IMDb Rating by Genre × Decade",
            xaxis=dict(title="Decade", gridcolor=GRID, side="bottom"),
            yaxis=dict(title="", gridcolor=GRID),
        )
        st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────
#  ROW 3 — Top Directors + Runtime vs Rating
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Director Spotlight & Runtime Analysis</div>', unsafe_allow_html=True)
c5, c6 = st.columns(2)

with c5:
    top_dirs = (
        df.groupby("Director")
        .agg(Film_Count=("Series_Title", "count"), Avg_Rating=("IMDB_Rating", "mean"))
        .query("Film_Count >= 2")
        .sort_values("Avg_Rating", ascending=False)
        .head(10)
        .reset_index()
    )

    if not top_dirs.empty:
        top_dirs["Label"] = top_dirs["Director"].apply(lambda x: x.split(" ")[-1])

        fig_dir = go.Figure(go.Bar(
            x=top_dirs["Avg_Rating"],
            y=top_dirs["Label"],
            orientation="h",
            marker=dict(
                color=top_dirs["Avg_Rating"],
                colorscale=[[0, "#2A2A2A"], [0.5, "#CF6679"], [1, "#E8C87A"]],  # Ensure valid color strings
                opacity=0.75,
                line=dict(width=0),
            ),
            text=top_dirs["Avg_Rating"].apply(lambda x: f"{x:.2f}"),
            textposition="outside",
            textfont=dict(color=GOLD, size=11),
            customdata=top_dirs[["Director", "Film_Count"]].values,
            hovertemplate="<b>%{customdata[0]}</b><br>Avg Rating: %{x:.2f}<br>Films: %{customdata[1]}<extra></extra>",
        ))
        fig_dir.update_layout(
            **LAYOUT_BASE,
            title="Top Directors by Avg Rating (≥2 films)",
            xaxis=dict(range=[7, top_dirs["Avg_Rating"].max() + 0.4],
                       gridcolor=GRID, title="Avg IMDb Rating"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            height=370,
        )
        st.plotly_chart(fig_dir, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Not enough multi-film directors in current filter.")

with c6:
    df_rt = df.dropna(subset=["Runtime_min"]).copy()

    fig_rt = go.Figure()
    fig_rt.add_trace(go.Scatter(
        x=df_rt["Runtime_min"],
        y=df_rt["IMDB_Rating"],
        mode="markers",
        marker=dict(
            color=df_rt["IMDB_Rating"],
            colorscale=[[0, "#2A2A2A"], [0.5, "#CF6679"], [1, "#E8C87A"]],  # Ensure valid color strings
            size=8,
            opacity=0.75,
            line=dict(width=0),
        ),
        text=df_rt["Series_Title"],
        hovertemplate="<b>%{text}</b><br>Runtime: %{x} min<br>Rating: %{y:.1f}<extra></extra>",
        showlegend=False,
    ))

    # Trend line
    if len(df_rt) > 4:
        z = np.polyfit(df_rt["Runtime_min"].fillna(0), df_rt["IMDB_Rating"].fillna(0), 1)
        p = np.poly1d(z)
        x_line = np.linspace(df_rt["Runtime_min"].min(), df_rt["Runtime_min"].max(), 100)
        fig_rt.add_trace(go.Scatter(
            x=x_line, y=p(x_line),
            mode="lines",
            line=dict(color="rgba(232, 200, 122, 0.53)", width=2, dash="dot"),
            name="Trend",
            showlegend=False,
        ))

    fig_rt.update_layout(
        **LAYOUT_BASE,
        title="Runtime vs. IMDb Rating (with trend)",
        xaxis=dict(title="Runtime (minutes)", gridcolor=GRID),
        yaxis=dict(title="IMDb Rating", gridcolor=GRID),
        height=370,
    )
    st.plotly_chart(fig_rt, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────
#  ROW 4 — Decade Trend Line + Genre Funnel
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">Temporal Trends & Genre Breakdown</div>', unsafe_allow_html=True)
c7, c8 = st.columns([1.3, 1])

with c7:
    decade_trend = (
        df.groupby("Decade")
        .agg(Avg_Rating=("IMDB_Rating", "mean"),
             Film_Count=("Series_Title", "count"))
        .reset_index()
        .sort_values("Decade")
    )

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

    fig_trend.add_trace(
        go.Scatter(
            x=decade_trend["Decade"],
            y=decade_trend["Avg_Rating"],
            mode="lines+markers",
            name="Avg Rating",
            line=dict(color=GOLD, width=3),
            marker=dict(size=9, color=GOLD, line=dict(color=BG, width=2)),
        ),
        secondary_y=False,
    )
    fig_trend.add_trace(
        go.Bar(
            x=decade_trend["Decade"],
            y=decade_trend["Film_Count"],
            name="Film Count",
            marker_color="rgba(207, 102, 121, 0.33)",  # Replace ACCENT + "55" with valid rgba color
            hovertemplate="Decade: %{x}<br>Films: %{y}<extra></extra>",
        ),
        secondary_y=True,
    )

    fig_trend.update_layout(
        **LAYOUT_BASE,
        title="Average Rating & Film Count by Decade",
        legend=dict(bgcolor="#0D0D0D", bordercolor="#2A2A2A", font_size=10),
        xaxis=dict(gridcolor=GRID),
    )
    fig_trend.update_yaxes(title_text="Avg IMDb Rating", secondary_y=False,
                           gridcolor=GRID, range=[7, 9.5])
    fig_trend.update_yaxes(title_text="Film Count", secondary_y=True, gridcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})

with c8:
    genre_gross = (
        df.dropna(subset=["Gross_USD"])
        .groupby("Primary_Genre")["Gross_USD"]
        .sum()
        .sort_values(ascending=True)
        .tail(8)
        .reset_index()
    )

    if not genre_gross.empty:
        fig_funnel = go.Figure(go.Funnel(
            y=genre_gross["Primary_Genre"],
            x=genre_gross["Gross_USD"] / 1e6,
            textposition="inside",
            textinfo="label+value",
            texttemplate="%{label}<br>$%{value:.0f}M",
            marker=dict(
                color=[
                    "rgba(232,200,122,0.90)", "rgba(232,200,122,0.78)",
                    "rgba(232,200,122,0.65)", "rgba(232,200,122,0.55)",
                    "rgba(232,200,122,0.45)", "rgba(232,200,122,0.35)",
                    "rgba(232,200,122,0.25)", "rgba(232,200,122,0.18)",
                ],
                line=dict(color=BG, width=1),
            ),
            connector=dict(line=dict(color=GRID, width=1)),
            hovertemplate="<b>%{y}</b><br>Total Gross: $%{x:.0f}M<extra></extra>",
        ))
        fig_funnel.update_layout(
            **LAYOUT_BASE,
            title="Total Box Office by Genre (Top 8)",
            showlegend=False,
        )
        st.plotly_chart(fig_funnel, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No gross data available for funnel. Toggle off box office filter.")


# ─────────────────────────────────────────────
#  ROW 5 — IMDb vs Metacritic Correlation
# ─────────────────────────────────────────────
df_meta = df.dropna(subset=["Meta_score"]).copy()

if len(df_meta) > 5:
    st.markdown('<div class="section-header">Audience vs. Critics</div>', unsafe_allow_html=True)

    fig_corr = px.scatter(
        df_meta,
        x="Meta_score",
        y="IMDB_Rating",
        color="Primary_Genre",
        hover_name="Series_Title",
        hover_data={"Released_Year": True, "Director": True},
        trendline="ols",
        trendline_color_override=GOLD,
        title="Metacritic Score vs. IMDb Rating (Critics vs. Audience)",
        color_discrete_sequence=px.colors.qualitative.Antique,
    )
    fig_corr.update_layout(
        **LAYOUT_BASE,
        xaxis=dict(title="Metacritic Score (Critics)", gridcolor=GRID),
        yaxis=dict(title="IMDb Rating (Audience)", gridcolor=GRID),
        legend=dict(bgcolor="#0D0D0D", bordercolor="#2A2A2A", font_size=10),
    )
    st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────
#  FILMOGRAPHY TABLE
# ─────────────────────────────────────────────
with st.expander("📋  Browse Films in Current Filter"):
    cols_show = ["Series_Title", "Released_Year", "Primary_Genre", "Director",
                 "IMDB_Rating", "Meta_score", "Runtime_min", "Gross_USD"]
    df_show = df[cols_show].copy()
    df_show.columns = ["Title", "Year", "Genre", "Director",
                       "IMDb", "Metacritic", "Runtime (min)", "Gross (USD)"]
    df_show = df_show.sort_values("IMDb", ascending=False).reset_index(drop=True)
    df_show["Gross (USD)"] = df_show["Gross (USD)"].apply(
        lambda x: f"${x:,.0f}" if pd.notna(x) else "—"
    )

    st.dataframe(
        df_show,
        use_container_width=True,
        hide_index=True,
        column_config={
            "IMDb": st.column_config.ProgressColumn("IMDb", min_value=0, max_value=10, format="%.1f"),
        },
    )


# ─────────────────────────────────────────────
#  ATTRIBUTION FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="attribution">
  <strong>Data Source:</strong> IMDb Top 1000 Movies & TV Shows Dataset &nbsp;·&nbsp;
  Originally compiled by Harshit Shankhdhar &nbsp;·&nbsp;
  Available on <a href="https://www.kaggle.com/datasets/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows" target="_blank">Kaggle</a>
  under the <strong>CC0 1.0 Universal (Public Domain)</strong> license.
  <br><br>
  Dashboard built with <strong>Streamlit</strong> + <strong>Plotly</strong> &nbsp;·&nbsp;
  CIS 220 — Business Analytics &nbsp;·&nbsp;
  West Visayas State University &nbsp;·&nbsp;
  <strong>Lil Benedict Herrera</strong> &nbsp;·&nbsp; 2026
</div>
""", unsafe_allow_html=True)
