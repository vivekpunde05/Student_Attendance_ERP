#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Initialize database tables
python -c "from database import create_tables, create_default_admin; create_tables(); create_default_admin()"
