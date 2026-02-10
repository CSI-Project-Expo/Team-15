from datetime import datetime, timedelta
from importlib import import_module
from pathlib import Path
import sys
import os

# Ensure project root is on sys.path so we can import backend modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    crud = import_module('backend.crud')
    dbmod = import_module('backend.database')
    main = import_module('backend.main')
    SessionLocal = dbmod.SessionLocal
    db = SessionLocal()
    cameras = crud.get_all_cameras(db)
    incidents = crud.get_all_incidents(db, limit=1000)
    cameras_list = list(cameras)
    incidents_list = list(incidents)
    day_ago = datetime.utcnow() - timedelta(days=1)
    recent_count = sum(1 for incident in incidents_list if getattr(incident, 'timestamp', datetime.min) > day_ago)
    print('OK', len(cameras_list), len(incidents_list), recent_count)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    try:
        db.close()
    except:
        pass
