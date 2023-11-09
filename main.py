import os
from musiclang import Score
from musiclang.library import *
import numpy as np
import glob
import json
import shutil

from code.jukebox import manipulate, mix_songs

LOAD_FROM = 'midi'
#LOAD_FROM = 'msl'
DATA_DIR = 'data/experiment'
FILES_DIR = 'data/midi_files'
RANDOM = True
SEED = 235
ONE_SHOT = False
N_ITER = 100
base_dir = DATA_DIR

files = glob.glob(os.path.join(FILES_DIR, '**/*.mid'))

for i in range(N_ITER):
    try:
        if not ONE_SHOT:
            SEED = np.random.randint(50000)
            np.random.seed(SEED)

        # Make dir SEED
        base_dir = os.path.join(DATA_DIR, str(SEED))

        if RANDOM:
            np.random.seed(SEED)
            path1, path2, path_chords = np.random.choice(files, 3, replace=False)
        else:
            # Load two pieces and one chord progression
            path1 = "submission_files/Final_Fantasy_7/prelude.mid"
            path2 = "submission_files/Rayman/rayman-bandland.mid"
            path_chords = "submission_files/Silent_Hill/SilentHillTheme.mid"

        score = mix_songs(path1, path2, path_chords, chord_range=(0, 16))

        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        score.to_midi(os.path.join(base_dir, 'output.mid'), one_track_per_instrument=False)
        # Copy original midi files to data directory
        shutil.copy(path1, os.path.join(base_dir, 'orchestra.mid'))
        shutil.copy(path2, os.path.join(base_dir, 'melody.mid'))
        shutil.copy(path_chords, os.path.join(base_dir, 'chords.mid'))
        data = {'orchestra': path1, 'melody': path2, 'chords': path_chords, 'seed': SEED}
        with open(os.path.join(base_dir, 'metadata.json'), 'w') as f:
            json.dump(data, f, indent=4)

        if ONE_SHOT:
            break

    except Exception as e:
        print(e)
        continue


