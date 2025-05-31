import shutil
from datetime import datetime

now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
shutil.copyfile("base.db", f"backups/base_backup_{now}.db")
print("Sauvegarde faite.")
