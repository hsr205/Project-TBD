# NBA Immaculate Grid Solver

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-16+-336791?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Playwright-Async-2EAD33?style=for-the-badge&logo=playwright&logoColor=white" />
  <img src="https://img.shields.io/badge/Poetry-Package%20Manager-60A5FA?style=for-the-badge&logo=poetry&logoColor=white" />
  <img src="https://img.shields.io/badge/UMAP-ML%20Visualization-FF6B35?style=for-the-badge" />
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [ML & Visualization](#ml--visualization)
- [Immaculate Grid Category Mappings](#immaculate-grid-category-mappings)
- [Testing](#testing)
- [Dependencies](#dependencies)
- [Author](#author)

---

## Overview

**NBA Immaculate Grid Solver** is an end-to-end Python application that autonomously solves the daily [NBA Immaculate Grid](https://www.sports-reference.com/immaculate-grid/basketball/mens/) puzzle. The system navigates the Sports Reference website using a headless browser, interprets each cell's category constraints, queries a locally maintained PostgreSQL database of historical NBA statistics, selects a valid player answer for every cell, and submits the completed grid — all without human input.

Beyond the solver, the project includes a machine learning layer that generates player similarity embeddings from career statistics and renders them as interactive 3D visualizations using UMAP dimensionality reduction and Plotly.

The data pipeline scrapes [Basketball Reference](https://www.basketball-reference.com/) for comprehensive historical player and franchise statistics and loads them into a normalized relational database that powers both the grid solver and the ML models.

---

## Features

- **Automated Grid Solving** — Navigates the Immaculate Grid interface, reads all row/column category headers (team logos, stat thresholds, awards, etc.), builds SQL queries, and submits valid player answers.
- **Full Data Pipeline** — Asynchronous Playwright-based web scraper populates a PostgreSQL database with:
  - Player biographical data (debut year, position, height, weight, college, birth country, draft round)
  - Per-game regular season statistics (31 columns per season)
  - Advanced regular season statistics (PER, TS%, WS/48, VORP, BPM, and more — 29 columns per season)
  - Playoff series statistics (37 columns per series)
  - NBA franchise data
- **Player Similarity Engine** — Builds player embedding vectors from career averages and computes cosine similarity matrices using NumPy and scikit-learn's `StandardScaler`.
- **Interactive 3D Visualizations** — Renders player clusters in 3D using UMAP (Uniform Manifold Approximation and Projection) and Plotly, with searchable dropdowns to highlight individual players.
- **Structured Logging** — Color-coded console logging across all modules using a custom ANSI formatter.
- **Connection Pooling** — PostgreSQL connections are managed via `psycopg2`'s `SimpleConnectionPool` (configurable min/max connections).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Entry Point                             │
│                      src/main/main.py                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────▼──────────────────┐
          │         ImmaculateGrid              │
          │   immaculate_grid/immaculate_grid.py│
          │  - Navigates grid UI via Playwright │
          │  - Reads category headers           │
          │  - Queries DB for valid answers     │
          │  - Submits player selections        │
          └────────┬───────────────┬────────────┘
                   │               │
    ┌──────────────▼───┐   ┌───────▼──────────────────┐
    │   WebScraper     │   │     DatabaseClient        │
    │  src/web_scraper │   │   src/database/           │
    │  - Playwright    │   │   - psycopg2 pool         │
    │  - BbRef scraping│   │   - CRUD operations       │
    │  - DataCleanser  │   │   - Immaculate Grid query │
    └──────────────────┘   └───────────────────────────┘
                                       │
                            ┌──────────▼──────────┐
                            │     PostgreSQL        │
                            │   basketball_db       │
                            │  - player             │
                            │  - franchise          │
                            │  - player_reg_stats   │
                            │  - player_adv_stats   │
                            │  - player_playoff_stats│
                            └─────────────────────┘

    ┌─────────────────────────────────────────────────┐
    │                  ML Layer                        │
    │  models/player_embedding.py                     │
    │  - Career averages → feature vectors            │
    │  - StandardScaler normalization                 │
    │  - Cosine similarity matrix (NxN)               │
    │                                                 │
    │  models/umap_rendering.py                       │
    │  - UMAP 3D dimensionality reduction             │
    │  - Interactive Plotly scatter plot              │
    │  - Advanced metrics 3D view (PER/WS48/VORP)    │
    └─────────────────────────────────────────────────┘
```

---

## Project Structure

```
Immaculate_Grid_NBA/
│
├── src/
│   ├── main/
│   │   └── main.py                     # Application entry point
│   ├── config/
│   │   └── config.py                   # Pydantic-Settings configuration (reads .env)
│   ├── database/
│   │   ├── database_client.py          # PostgreSQL client with connection pooling
│   │   └── data_loader.py              # Orchestrates scraping → DB ingestion
│   ├── web_scraper/
│   │   ├── web_scraper.py              # Async Playwright scraper (players, franchises, drafts)
│   │   └── data_cleanser.py            # Type-safe row sanitization (str/int/decimal)
│   ├── utils/
│   │   └── constants.py                # SQL queries, table mappings, category mappings, team abbreviations
│   └── logger/
│       ├── logger.py                   # Singleton root logger configuration
│       └── logger_color_formatter.py   # ANSI color-coded log formatter
│
├── immaculate_grid/
│   └── immaculate_grid.py              # Core solver: reads grid, builds queries, fills answers
│
├── models/
│   ├── player_embedding.py             # Player feature vectors + cosine similarity matrix
│   └── umap_rendering.py               # 3D UMAP and advanced metrics visualizations
│
├── test/                               # Test directory (pytest + pytest-asyncio)
│
├── .env                                # Environment variables (not committed)
├── pyproject.toml                      # Poetry project configuration and dependencies
└── poetry.lock                         # Locked dependency versions
```

---

## Database Schema

The application maintains five tables in a PostgreSQL database (`basketball_db`).

### `player`
Stores biographical data for every NBA player scraped from Basketball Reference.

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto-incremented player ID |
| `player_name` | VARCHAR(100) | Full player name |
| `year_debuted` | INTEGER | First NBA season year |
| `year_retired` | INTEGER | Last NBA season year |
| `position` | VARCHAR(5) | Primary position (PG, SG, SF, PF, C) |
| `height` | VARCHAR(5) | Height in feet-inches format (e.g. `6-11`) |
| `weight` | INTEGER | Weight in pounds |
| `birth_date` | VARCHAR(100) | Date of birth |
| `colleges` | VARCHAR(100) | College(s) attended |
| `hall_of_fame` | VARCHAR(1) | `'Y'` if inducted |
| `round_selected` | INTEGER | NBA Draft round (9999 = undrafted) |
| `birth_country` | VARCHAR(50) | Country of birth (US state → `'United States'`) |

### `franchise`
Stores historical franchise-level data for all 30 active NBA teams.

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL PK | Auto-incremented franchise ID |
| `franchise_name` | VARCHAR(100) | Full franchise name |
| `franchise_abbreviation` | VARCHAR(5) | Team abbreviation (e.g. `LAL`) |
| `league_name` | VARCHAR(20) | League (e.g. `NBA`) |
| `year_established` | VARCHAR(20) | Founding year |
| `num_years_in_operation` | INTEGER | Total years active |
| `num_games_played` | INTEGER | All-time games played |
| `num_games_won` | INTEGER | All-time wins |
| `num_games_lost` | INTEGER | All-time losses |
| `win_percentage` | NUMERIC(4,4) | All-time win percentage |
| `playoff_appearances` | INTEGER | Total playoff appearances |
| `division_title_wins` | INTEGER | Division titles |
| `conference_title_wins` | INTEGER | Conference titles |
| `championship_title_wins` | INTEGER | NBA Championships |
| `league_champion_years` | VARCHAR(200) | Championship years string |

### `player_regular_season_stats`
Per-game statistics for each player-season in the regular season.

Key columns: `player_id` (FK), `season`, `age`, `team`, `league`, `position`, `games_played`, `games_started`, `minutes_played_per_game`, `field_goals_made`, `field_goals_attempted`, `field_goal_percentage`, `three_pointers_made`, `three_point_percentage`, `two_pointers_made`, `free_throws_made`, `free_throw_percentage`, `offensive_rebounds`, `defensive_rebounds`, `rebound_avg`, `assist_avg`, `steal_avg`, `block_avg`, `turnover_avg`, `point_avg`, `awards`

### `player_regular_season_advanced_stats`
Advanced analytics per player-season: `PER`, `TS%`, `3PAr`, `FTr`, `ORB%`, `DRB%`, `TRB%`, `AST%`, `STL%`, `BLK%`, `TOV%`, `USG%`, `OWS`, `DWS`, `WS`, `WS/48`, `OBPM`, `DBPM`, `BPM`, `VORP`

### `player_playoff_series_stats`
Per-series playoff statistics including series result, opponent, round, and complete box score totals.

---

## Prerequisites

Before running the project, ensure you have the following installed:

- **Python 3.12+**
- **Poetry** — [Installation guide](https://python-poetry.org/docs/#installation)
- **PostgreSQL 14+** — A running instance with a database named `basketball_db` and a user with write permissions
- **Chromium** — Installed via Playwright (handled automatically after install)

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Immaculate_Grid_NBA
```

### 2. Install dependencies with Poetry

```bash
poetry install
```

### 3. Install Playwright browsers

```bash
poetry run playwright install chromium
```

### 4. Set up PostgreSQL

Create the database and user:

```sql
CREATE DATABASE basketball_db;
CREATE USER postgres WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE basketball_db TO postgres;
```

### 5. Configure environment variables

Copy the example below and create a `.env` file in the project root:

```bash
cp .env.example .env  # or create .env manually — see Configuration section
```

---

## Configuration

All configuration is managed via a `.env` file in the project root. The application uses **pydantic-settings** to load and validate these values at startup.

Create a `.env` file with the following variables:

```dotenv
# ─── Sports Reference URLs ──────────────────────────────────────────────────

# Base URL for Basketball Reference (used for player/franchise navigation)
BASE_URL=https://www.basketball-reference.com/?utm_source=SRhome_clickto_bbr

# Draft history page URL (used for scraping NBA draft pick rounds)
DRAFT_URL=https://www.basketball-reference.com/draft/

# Immaculate Grid base URL — a numeric index is appended per puzzle (e.g. grid-0, grid-1, ...)
IMMACULATE_GRID_URL=https://www.sports-reference.com/immaculate-grid/basketball/mens/grid-

# ─── Stats Table Key ────────────────────────────────────────────────────────
# Controls which statistics table the scraper targets on a player's BBRef page.
# Valid values:
#   reg-season-qsiB8VY      → Per-game regular season stats (table#per_game_stats)
#   reg-season-adv-uBMv04w  → Advanced regular season stats (table#advanced)
#   playoffs-vsy03Dw        → Playoff series stats (table#playoffs_series)
#   franchise-roBWT3o       → Franchise per-season stats
STATS_TABLE_KEY=reg-season-adv-uBMv04w

# ─── PostgreSQL ─────────────────────────────────────────────────────────────
DB_HOST=localhost
DB_PORT=<DB-PORT>
DB_NAME=<DB-NAME>
DB_USER=<DB-USER>
```

> **Note:** `DB_PASSWORD` is not read via pydantic-settings in the current implementation. The PostgreSQL connection relies on peer authentication or a `.pgpass` file. Ensure your local PostgreSQL instance is configured to allow the specified user to connect without a password, or extend `config.py` to include a `db_password` field.

---

## Running the Project

All commands should be run from the project root using `poetry run`.

### Solve the Immaculate Grid

Runs the solver against a specific puzzle index (defaults to index `0`):

```bash
poetry run python -m src.main.main
```

To solve a different puzzle, change the `index` range in `src/main/main.py`:

```python
# Solve puzzle index 42
for index in range(0, 43):
    ...
```

> The solver launches a **non-headless** Chromium browser window so you can observe the automation in real time. The grid URL is constructed as `IMMACULATE_GRID_URL + index` (e.g. `.../grid-0`).

---

### Data Pipeline — Populate the Database

The database must be seeded with NBA data before the solver can run. The following operations are available via `DatabaseClient` and `DataLoader`. These are intended to be called programmatically from a script or a temporary `__main__` block.

**Step 1 — Create all tables:**
```python
db_client = DatabaseClient(settings=settings)
db_client.create_player_table()
db_client.create_franchise_table()
db_client.create_player_regular_season_stats_table()
db_client.create_player_regular_season_advanced_stats_table()
```

**Step 2 — Insert all NBA players:**
```python
await db_client.insert_rows_into_player_table()
```

**Step 3 — Insert franchise data:**
```python
await db_client.insert_rows_into_franchise_table()
```

**Step 4 — Load stats for all players** (set `STATS_TABLE_KEY` in `.env` to the desired table before running):
```python
loader = DataLoader(settings=settings)
player_dict = db_client.get_result_dict_from_queried_table()
await loader.load_data_into_table(
    insert_query_str=Constants.Queries.INSERT_INTO_PLAYER_REGULAR_SEASON_STATS_TABLE_STR,
    entity_dict=player_dict
)
```

**Step 5 — Enrich player data (birth country + draft round):**
```python
await loader.update_player_birth_country_in_player_table(all_players_data_dict=player_dict)
await loader.update_draft_data_in_player_table()
```

> **Important:** The scraper interacts with Basketball Reference using a browser UI automation. Running the full pipeline across all historical players is a time-intensive process. The scraper includes `asyncio.sleep()` delays between requests to avoid rate limiting. Ads may interrupt the scraping session — a TODO comment in the code notes this as a known issue.

---

## ML & Visualization

### Player Similarity Embeddings

`models/player_embedding.py` builds a feature matrix from career-averaged statistics stored in the database, normalizes it with `StandardScaler`, and computes a cosine similarity matrix (NxN) across all eligible players (minimum 82 career games).

```python
from models.player_embedding import PlayerEmbedding
from src.config.config import Settings

settings = Settings()
embedding = PlayerEmbedding(settings=settings)
similarity_matrix = embedding.get_similarity_matrix()  # numpy ndarray (N, N)
```

### UMAP 3D Visualizations

`models/umap_rendering.py` provides two interactive 3D Plotly charts rendered in the browser.

**Option 1 — UMAP Dimensionality Reduction** (full stat vector → 3D):
```python
from models.umap_rendering import UMAPRendering

renderer = UMAPRendering(settings=settings)
renderer.display_umap_rending()
```

**Option 2 — Advanced Metrics 3D Plot** (PER × WS/48 × VORP axes):
```python
renderer.display_umap_rendering_for_advanced_stats()
```

Both visualizations include a searchable dropdown menu to locate and highlight any individual player in the 3D space.

---

## Immaculate Grid Category Mappings

The solver maps textual grid category labels to SQL `WHERE` clause conditions. The supported categories are:

| Grid Category | SQL Condition |
|---|---|
| `Block` | `p_reg.block_avg > {N}` |
| `Steal` | `p_reg.steal_avg > {N}` |
| `Points` | `p_reg.point_avg > {N}` |
| `Rebounds` | `p_reg.rebound_avg > {N}` |
| `Assists` | `p_reg.assist_avg > {N}` |
| `Points (career)` | `p_reg.total_career_points > {N}` |
| `Assists (career)` | `p_reg.total_career_assists > {N}` |
| `Rebounds (career)` | `p_reg.total_career_rebounds > {N}` |
| `All Star` | `p_reg.awards LIKE '%AS%'` |
| `Rookie of the Year` | `p_reg.awards LIKE '%ROY-1%'` |
| `MVP` | `p_reg.awards LIKE '%MVP-1%'` |
| `All-NBA` | `p_reg.awards LIKE '%NBA%'` |
| `Defensive Player of the Year` | `p_reg.awards LIKE '%DPOY-1%'` |
| `Hall of Fame` | `p.hall_of_fame = 'Y'` |
| `First Round Draft Pick` | `p.round_selected = 1` |
| `Undrafted` | `p.round_selected = 9999` |
| `League Champ` | Championship year overlap subquery |
| `Only One Team` | Single-team career subquery |
| `Born Outside US 50 States and DC` | `p.birth_country <> 'United States'` |

Team-based cells (e.g. `Los Angeles Lakers`) are resolved using the `TEAM_ABBREVIATION_DICT` and result in a SQL `team = 'LAL'` condition. When a cell requires two team constraints (a player who played for both teams), the solver automatically uses a `COUNT(DISTINCT team) = 2` subquery.

---

## Testing

The project uses **pytest** with **pytest-asyncio** for async test support and **pytest-cov** / **coverage** for code coverage reporting.

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=src --cov=immaculate_grid --cov=models --cov-report=term-missing

# Run a specific test file
poetry run pytest test/your_test_file.py -v
```

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `playwright` | ^1.61.0 | Async browser automation for scraping and grid interaction |
| `psycopg2-binary` | ^2.9.12 | PostgreSQL driver with connection pooling |
| `pydantic-settings` | ^2.14.2 | Environment variable loading and validation |
| `pydantic` | ^2.13.4 | Data validation |
| `pandas` | ^3.0.5 | DataFrame operations for ML feature preparation |
| `numpy` | ^2.5.1 | Array operations, similarity matrix computation |
| `scikit-learn` | ^1.9.0 | `StandardScaler`, `OneHotEncoder` for feature engineering |
| `umap-learn` | ^0.5.12 | Unsupervised dimensionality reduction to 3D |
| `plotly` | ^6.9.0 | Interactive 3D scatter plot visualization |
| `numba` | ^0.59.0 | JIT compilation (required by umap-learn) |
| `llvmlite` | ^0.42.0 | LLVM bindings (required by numba) |
| `tqdm` | — | Progress bars during long scraping operations |
| `pytest` | ^9.1.1 | Test framework |
| `pytest-asyncio` | ^1.4.0 | Async test support |
| `pytest-cov` | ^7.1.0 | Test coverage integration |
| `coverage` | — | Code coverage measurement |

---

## Author

**Henry Rothenberg** — [hsr205@aol.com](mailto:hsr205@aol.com)
