# Copilot Instructions for lynkscan-backend

## Project Overview

- **Purpose:** Scan open source software (OSS) for license and vulnerability information.
- **Main Components:**
  - `src/lynkscan/scanners/`: Scanners for GitHub, PyPI, and NPM repositories. Each scanner fetches metadata and vulnerabilities for packages.
  - `src/lynkscan/db/`: Database models, repositories, and a manager for SQLModel-based persistence.
  - `src/lynkscan/llm/`: License detection using LLMs (LangChain + Ollama).
  - `src/lynkscan/utils/`: Utility functions (logging, formatting, git versioning).

## Architecture & Data Flow

- **Scanning:**
  - Each scanner (e.g., `python.py`, `npm.py`, `github.py`) fetches metadata and vulnerabilities from external APIs (PyPI, OSV, GitHub).
  - Example: `PythonPackage` fetches release info and vulnerabilities, storing results in memory or files.
- **Database:**
  - Uses SQLModel (see `db/models/software.py`, `db/manager.py`, `db/repos/software.py`).
  - `DatabaseManager` provides session and repository access.
  - Models follow the schema in the following instructions. (see mermaid ER diagram).
- **LLM Integration:**
  - `llm/license_detector.py` uses LangChain and Ollama to classify license text files.

## Developer Workflows

- **Python Version:** 3.13+
- **Install dependencies:**
  ```sh
  pip install -e .
  ```
- **Database setup:**
  - Use `DatabaseManager.create_db_and_tables()` to initialize tables.
- **Linting/Formatting:**
  - Uses `ruff` and `pyrefly` (see `pyproject.toml`).
- **Testing:**
  - No explicit test runner found; add tests under `tests/` if needed.

## Project Conventions

- **Models:** Use SQLModel for all DB tables. ERD if schema changes.
- **Repositories:** All DB access via repository classes (e.g., `SoftwareRepository`).
- **Scanners:** Each ecosystem has its own scanner class. Fetches metadata and vulnerabilities, writes results to JSON files.
- **LLM:** License detection is abstracted in `LicenseDetector` (configurable model and base_url).
- **Config:** Most config is hardcoded; update classes directly for changes.

## Git Commit Messages

- Use the conventional commit format, the commit message should be structured as follows:

  '''
  <type>[optional scope]: <description>

  [optional body]

  [optional footer(s)]
  '''

- The first line is the commit title and should be concise (max 50 characters).
- The third line is optional and can provide additional context or details about the change.
- The type in the first line must be one of the following:
  - build: Changes that affect the build system or external dependencies
  - ci: Changes to our CI configuration files and scripts
  - docs: Documentation only changes
  - feat: A new feature
  - fix: A bug fix
  - perf: A code change that improves performance
  - refactor: A code change that neither fixes a bug nor adds a feature
  - style: Changes that do not affect the meaning of the code
  - test: Adding missing tests or correcting existing tests

## Integration Points

- **External APIs:**
  - GitHub REST API, PyPI JSON API, OSV vulnerability database.
  - LLM via Ollama HTTP API.
- **Database:**
  - SQLite by default, configurable via `DatabaseManager`.

## Key Files/Directories

- `src/lynkscan/scanners/` — Scanners for each package ecosystem
- `src/lynkscan/db/` — DB models, repositories, and manager
- `src/lynkscan/llm/license_detector.py` — LLM-based license detection
- `GEMINI.md` — ER diagram and schema reference
- `pyproject.toml` — Tooling and dependency config

---

## Database schema

```mermaid
erDiagram

  SOFTWARE {
    int id PK
    string name
    string identifier
    string latest_version
    int category_id FK
    int license FK
    string official_site_url
    string repo_url
  }

  LICENSE {
    int id PK
    string name UK
    string type_id FK
  }

  LICENSE_TYPE {
    int id PK
    string type UK
  }

  SOFTWARE_CATEGORY {
    int id PK
    string name UK
  }

  SOFTWARE_VULNERABILITY {
    int id PK
    int software_id FK
    string software_version
    string cve FK
  }

  SOFTWARE_GITHUB_EVALUATION {
    int id PK
    string identifier FK
    int stars
    bool has_sponsors
    bool is_authorized_developer
    str license_file_path
    datetime last_checked_time
  }

  VULNERABILITY {
    string cve PK
    float cvss
  }

  USAGE {
    int id
    string usage
  }

  SOFTWARE ||--o{ SOFTWARE_CATEGORY : belongs to
  SOFTWARE ||--o{ LICENSE : uses
  LICENSE ||--o{ LICENSE_TYPE : has_type
  VULNERABILITY ||--o{ affects
  SOFTWARE ||--o{ SOFTWARE_VULNERABILITY : is affected
  SOFTWARE ||--o| SOFTWARE_GITHUB_EVALUATION : has_evaluation
```
