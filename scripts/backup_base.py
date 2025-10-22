import shutil
from datetime import datetime
from pathlib import Path

now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
BASE_DIR = Path(__file__).resolve().parents[1]
source = BASE_DIR / "data" / "base.db"
destination = BASE_DIR / "data" / "backups" / f"base_backup_{now}.db"
shutil.copyfile(source, destination)
print("Sauvegarde faite.")
