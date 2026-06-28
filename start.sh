#!/bin/bash
set -e
alembic upgrade head
python -c "
from app.seed import seed_default_users
seed_default_users()
print('Seed complete')
"
exec gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
