import os
from musiclang import Score
from musiclang.library import *
import numpy as np
import glob
import json
import shutil
from code.jukebox import manipulate, mix_songs
from code.ml import create_best_variations
import transformers

SEED = 100
np.random.seed(SEED)
# Configure same seed for huggingface
transformers.set_seed(SEED)

LOAD_FROM = 'midi'
#LOAD_FROM = 'msl'
DATA_DIR = 'data/experiment'
FILES_DIR = 'data/midi_files'

## CHANGE HERE TO SELECT MIDI_FILES
path_orchestration = "submission_files/Final_Fantasy_7/prelude.mid"  # Get the bass drums and the most dense instrument
path_melody = "submission_files/Rayman/rayman-bandland.mid"  # Get instruments in the high range (above median of mean pitch)
path_chords = "submission_files/Silent_Hill/SilentHillTheme.mid"  # Get only the chords of the song

base_dir = DATA_DIR

if not os.path.exists(base_dir):
    os.makedirs(base_dir)

# 1. Create a pattern by mixing three songs together
pattern = mix_songs(path_orchestration, path_melody, path_chords, chord_range=(0, 8))

# 2. Create variations of the pattern to extend the music
variations = create_best_variations(pattern, nb_variations=16, nb_kept=8, temperature=0.5, chord_duration=None, retry=2)

# Concatenate variations
score = pattern + sum(variations, None)
pattern.to_midi(os.path.join(base_dir, 'pattern.mid'), one_track_per_instrument=False)
score.to_midi(os.path.join(base_dir, 'output.mid'), one_track_per_instrument=False)

# Project on chord score
score_chords = Score.from_midi(path_chords, quantization=8, fast_chord_inference=True)
score_final = score.project_with_voice_leading_on_chord_score(score_chords, fixed_bass=True)

score_final.to_midi(os.path.join(base_dir, 'output_final.mid'), one_track_per_instrument=False)



# Save all variations as well
for idx, variation in enumerate(variations):
    variation.to_midi(os.path.join(base_dir, f'variation_{idx}.mid'), one_track_per_instrument=False)

# Copy original midi files to data directory
shutil.copy(path_orchestration, os.path.join(base_dir, 'orchestra.mid'))
shutil.copy(path_melody, os.path.join(base_dir, 'melody.mid'))
shutil.copy(path_chords, os.path.join(base_dir, 'chords.mid'))
data = {'orchestra': path_orchestration, 'melody': path_melody, 'chords': path_chords}
with open(os.path.join(base_dir, 'metadata.json'), 'w') as f:
    json.dump(data, f, indent=4)


