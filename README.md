# 🎬 CineMetrics — IMDb Film Analytics Dashboard

> An interactive, cinematic-themed analytics dashboard built with **Streamlit** and **Plotly**, exploring patterns across top-rated films in cinema history.

---

## Overview

CineMetrics is a data analytics dashboard that visualizes key trends from the **IMDb Top 1000 Movies & TV Shows** dataset. It allows users to interactively filter and explore films by release year, genre, rating, and box office earnings — surfacing insights about what makes a film critically and commercially significant.

Built as a solo mini-project for **CIS 220 — Business Analytics** at **West Visayas State University (WVSU)**, 2026.

---

## 📊 Dashboard Features

### Key Performance Indicators (KPIs)

| KPI | Description |
|---|---|
| **Total Films** | Count of films matching current filters |
| **Avg IMDb Rating** | Mean audience rating across filtered films |
| **Avg Runtime** | Average film length in minutes |
| **Top Genre** | Most represented genre by film count |
| **Combined Gross** | Total box office revenue of filtered films |

### Charts & Visualizations

| Chart | Type | Insight |
|---|---|---|
| Film Count by Genre | **Treemap** | Relative genre representation |
| Rating Distribution | **Violin Plot** | Score spread per top genre |
| Votes vs. Rating | **Bubble Scatter** | Popularity vs. quality vs. revenue |
| Genre × Decade | **Heatmap** | How genre ratings shifted across time |
| Top Directors | **Horizontal Bar** | Highest avg-rated directors (≥2 films) |
| Runtime vs. Rating | **Scatter + Trendline** | Does length correlate with quality? |
| Rating by Decade | **Dual-Axis Line + Bar** | Historical rating trends + film volume |
| Box Office by Genre | **Funnel Chart** | Which genres earn the most |
| Critics vs. Audience | **OLS Scatter** | Metacritic score vs. IMDb rating |

### Key Insight Panel

A dynamically generated callout box that surfaces data-driven findings from the current filter state — including genre rating gaps, directorial dominance, and the box office vs. critical acclaim paradox.

### Interactive Sidebar Filters

- **Release Year** — range slider (1931 to 2023)
- **Minimum IMDb Rating** — threshold slider (5.0 to 9.5)
- **Genre** — multi-select filter
- **Box Office Toggle** — show only films with known gross earnings

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `Streamlit` | Web app framework |
| `Pandas` | Data loading and cleaning |
| `NumPy` | Numerical operations and trendlines |
| `Plotly Express` | Treemap, scatter, funnel, OLS charts |
| `Plotly Graph Objects` | Violin, heatmap, bar, dual-axis charts |
| `SciPy / Statsmodels` | OLS regression for trendlines |

---

## 🎨 Design Decisions

- **Color palette:** Deep black background (`#0D0D0D`) with gold accents (`#E8C87A`) — inspired by film grain and theater aesthetics
- **Typography:** `Playfair Display` (serif) for headers, `Inter` for body — balancing editorial elegance with readability
- **Layout:** Wide mode with responsive columns; KPI cards use custom HTML/CSS for full design control
- **Responsiveness:** All charts re-render dynamically based on sidebar filter state via `@st.cache_data`

---

## 📋 Dataset

| Field | Detail |
|---|---|
| **Source** | IMDb (Internet Movie Database) |
| **Reference** | [Kaggle — IMDb Top 1000 Movies & TV Shows](https://www.kaggle.com/datasets/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows) |
| **License** | CC0 1.0 Universal — Public Domain |
| **Films** | 113 curated entries, 1931–2023 |
| **Fields** | Title, Year, Certificate, Runtime, Genre, IMDb Rating, Metacritic Score, Director, Stars, Votes, Gross |

---

**Lil Benedict Herrera**
BS Information Systems — 
West Visayas State University · Iloilo City, Philippines
CIS 220 — Business Analytics · 2026
