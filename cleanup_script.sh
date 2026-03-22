#!/bin/bash

# Script to clean up and verify the foundation of the FastAPI + React project
# This script performs the following:
# - Handles migration folders: backs up and removes backend/migrations, ensures alembic is in backend/alembic
# - Updates alembic/env.py to use SQLModel metadata
# - Creates missing .env.example files
# - Creates minimal Dockerfiles
# - Checks and suggests fixes for database.py and config.py
# - Ensures proper __init__.py files

set -e  # Exit on any error

PROJECT_ROOT="$(pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_ADMIN_DIR="$PROJECT_ROOT/frontend-admin"
FRONTEND_STORE_DIR="$PROJECT_ROOT/frontend-store"

echo "=== Project Foundation Cleanup Script ==="
echo "Project root: $PROJECT_ROOT"
echo ""

# Function to ask for confirmation
confirm() {
    read -p "$1 (y/N): " response
    case "$response" in
        [yY][eE][sS]|[yY])
            true
            ;;
        *)
            false
            ;;
    esac
}

# 1. Handle migration folders
echo "1. Handling migration folders..."
if [ -d "$BACKEND_DIR/migrations" ]; then
    echo "Found backend/migrations folder."
    if [ -d "$BACKEND_DIR/migrations/versions" ] && [ "$(ls -A $BACKEND_DIR/migrations/versions)" ]; then
        echo "Migration versions found in migrations/versions. Backing up to alembic/versions..."
        mkdir -p "$BACKEND_DIR/alembic/versions"
        cp -r "$BACKEND_DIR/migrations/versions/"* "$BACKEND_DIR/alembic/versions/" 2>/dev/null || true
        echo "Backup completed."
    else
        echo "No migration files found in migrations/versions."
    fi

    if confirm "Remove backend/migrations folder?"; then
        rm -rf "$BACKEND_DIR/migrations"
        echo "Removed backend/migrations."
    else
        echo "Skipped removing backend/migrations."
    fi
else
    echo "backend/migrations does not exist."
fi

# Ensure alembic is initialized in backend/alembic
if [ ! -f "$BACKEND_DIR/alembic.ini" ]; then
    echo "alembic.ini not found. Initializing Alembic in backend/alembic..."
    cd "$BACKEND_DIR"
    alembic init alembic
    cd "$PROJECT_ROOT"
else
    echo "alembic.ini already exists."
fi

# Update alembic.ini to point to alembic
if grep -q "script_location = migrations" "$BACKEND_DIR/alembic.ini"; then
    echo "Updating alembic.ini script_location to alembic..."
    sed -i 's|script_location = migrations|script_location = alembic|' "$BACKEND_DIR/alembic.ini"
fi

# Update env.py to use SQLModel metadata
echo "2. Updating alembic/env.py..."
ENV_PY="$BACKEND_DIR/alembic/env.py"
if [ -f "$ENV_PY" ]; then
    # Add import for SQLModel metadata
    if ! grep -q "from sqlmodel import SQLModel" "$ENV_PY"; then
        sed -i '/import sqlalchemy as sa/a from sqlmodel import SQLModel' "$ENV_PY"
    fi
    # Update target_metadata
    sed -i 's/target_metadata = None/target_metadata = SQLModel.metadata/' "$ENV_PY"
    echo "Updated env.py to use SQLModel.metadata."
else
    echo "env.py not found in alembic folder."
fi

# 3. Create .env.example in backend
echo "3. Creating .env.example in backend..."
if [ ! -f "$BACKEND_DIR/.env.example" ]; then
    cat > "$BACKEND_DIR/.env.example" << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Other environment variables as needed
# SECRET_KEY=your-secret-key-here
EOF
    echo "Created backend/.env.example."
else
    echo "backend/.env.example already exists."
fi

# 4. Update frontend .env.example files
echo "4. Updating frontend .env.example files..."
for frontend_dir in "$FRONTEND_ADMIN_DIR" "$FRONTEND_STORE_DIR"; do
    env_example="$frontend_dir/.env.example"
    if [ -f "$env_example" ]; then
        if [ ! -s "$env_example" ]; then
            echo "VITE_API_URL=http://localhost:8000" > "$env_example"
            echo "Updated $env_example with VITE_API_URL."
        else
            echo "$env_example already has content."
        fi
    else
        echo "VITE_API_URL=http://localhost:8000" > "$env_example"
        echo "Created $env_example."
    fi
done

# 5. Create minimal Dockerfiles
echo "5. Creating minimal Dockerfiles..."
# Backend Dockerfile
if [ ! -s "$BACKEND_DIR/Dockerfile" ]; then
    cat > "$BACKEND_DIR/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
    echo "Created backend/Dockerfile."
else
    echo "backend/Dockerfile already has content."
fi

# Frontend Dockerfiles
for frontend_dir in "$FRONTEND_ADMIN_DIR" "$FRONTEND_STORE_DIR"; do
    dockerfile="$frontend_dir/Dockerfile"
    if [ ! -s "$dockerfile" ]; then
        cat > "$dockerfile" << 'EOF'
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

CMD ["npm", "run", "preview"]
EOF
        echo "Created $dockerfile."
    else
        echo "$dockerfile already has content."
    fi
done

# 6. Check and suggest fixes for database.py and config.py
echo "6. Checking database.py and config.py..."
DB_PY="$BACKEND_DIR/database.py"
if [ -f "$DB_PY" ]; then
    if ! grep -q "SQLModel.metadata" "$DB_PY"; then
        echo "Suggestion: Add 'from sqlmodel import SQLModel' and ensure models are imported to initialize metadata for migrations."
    fi
    echo "database.py exists. Review for error handling and connection pooling."
else
    echo "database.py not found!"
fi

CONFIG_PY="$BACKEND_DIR/config.py"
if [ ! -s "$CONFIG_PY" ]; then
    echo "config.py is empty. Creating basic Pydantic settings..."
    cat > "$CONFIG_PY" << 'EOF'
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()
EOF
    echo "Created basic config.py with Pydantic BaseSettings."
else
    echo "config.py has content."
fi

# 7. Ensure __init__.py files
echo "7. Ensuring __init__.py files..."
for dir in "$BACKEND_DIR" "$BACKEND_DIR/models" "$BACKEND_DIR/routers"; do
    init_file="$dir/__init__.py"
    if [ ! -f "$init_file" ]; then
        touch "$init_file"
        echo "Created $init_file."
    else
        echo "$init_file exists."
    fi
done

echo ""
echo "=== Script completed ==="
echo "Summary of changes:"
echo "- Handled migration folders (backed up and removed migrations/ if confirmed)"
echo "- Updated alembic configuration"
echo "- Created/updated .env.example files"
echo "- Created minimal Dockerfiles"
echo "- Checked and fixed config.py"
echo "- Ensured __init__.py files exist"
echo ""
echo "Further manual steps:"
echo "- Review and update models/__init__.py to import all model classes"
echo "- Implement main.py with FastAPI app"
echo "- Update database.py to import models for metadata"
echo "- Test Alembic: cd backend && alembic revision --autogenerate -m 'initial'"
echo "- Implement auth.py, dependencies.py"
echo "- Set up docker-compose.yml for services"