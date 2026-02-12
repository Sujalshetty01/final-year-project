import os
import uvicorn

# Run backend from the `backend` package so imports like `from app.routes` work
os.chdir(os.path.join(os.path.dirname(__file__), '..', 'backend'))

uvicorn.run('app.main:app', host='127.0.0.1', port=int(os.environ.get('BACKEND_PORT','8001')), log_level='warning')
