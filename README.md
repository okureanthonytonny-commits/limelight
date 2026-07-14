# limelight/README.md

## One-line description
A single-vendor marketplace prototype (React frontends + FastAPI backend) — the first, exploratory iteration of a marketplace concept, rebuilt as `limelight_v2` after hitting scalability issues.

## Tech stack
- **Frontend**: React (two separate apps: customer + admin)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL

## Architecture summary
```
limelight/
├── backend/          # FastAPI service (early-stage, buggy)
├── frontend-admin/   # React admin dashboard
└── frontend-store/   # React customer storefront
```
An early prototype built to test the marketplace concept end-to-end. The backend and frontends are separated, but the codebase became unstable as scope grew without incremental testing — the core issues that `limelight_v2` was built to fix.

## Setup / run
This repo is **not recommended for production use** — it's preserved as a learning artifact. For a working version, see [`limelight_v2`](https://github.com/okureanthonytonny-commits/limelight_v2) or [`poultry-marketplace`](https://github.com/okureanthonytonny-commits/poultry-marketplace).

## What's implemented vs in-progress
- **Implemented**: Basic project structure, React frontends scaffolding, FastAPI backend skeleton.
- **In-progress / broken**: Most API endpoints are unstable; the project was abandoned due to compounding errors.

> **Note**: This is an **earlier iteration** superseded by [`poultry-marketplace`](https://github.com/okureanthonytonny-commits/poultry-marketplace), which contains the final, production-ready version of this marketplace concept.
