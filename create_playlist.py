import os
import shutil
import glob

DATA_DIR = 'data/experiment'
PLAYLIST_DIR = 'data/experiment/playlist'
os.makedirs(PLAYLIST_DIR, exist_ok=True)

dirs = [d for d in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, d)) and not d.startswith('playlist')]
for dir in dirs:
    try:
        shutil.copy(os.path.join(DATA_DIR, dir, 'output.mid'), os.path.join(PLAYLIST_DIR, f'{dir}.mid'))
    except:
        pass