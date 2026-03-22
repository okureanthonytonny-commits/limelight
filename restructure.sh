# Create new backend files (if not already present)
touch backend/__init__.py
touch backend/config.py
touch backend/auth.py
touch backend/dependencies.py
touch backend/Dockerfile

# Create __init__.py in models and routers (if missing)
touch backend/models/__init__.py
touch backend/routers/__init__.py

# Create alembic directory (if you want to keep migrations)
mkdir -p backend/alembic/versions
touch backend/alembic/README

# Create root-level files
touch .env.example
touch docker-compose.yml
touch .gitignore

# Create types/ folders in frontends
mkdir -p frontend-store/src/types
mkdir -p frontend-admin/src/types

# Create Dockerfiles for frontends
touch frontend-store/Dockerfile
touch frontend-admin/Dockerfile

# Create .env.example files in frontends
touch frontend-store/.env.example
touch frontend-admin/.env.example
