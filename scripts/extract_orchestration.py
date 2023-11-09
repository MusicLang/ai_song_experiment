import glob
import os
from musiclang import Score
import shutil

midi_files = glob.glob('data/midi_files/**/*.mid', recursive=True)
output_path = 'data/extracted_orchestrations'
if not os.path.exists(output_path):
    os.makedirs(output_path)


beginnings = [('start', [0, 4]), ('mid', [8, 12]), ('end', [-4, None])]

for midi_file in midi_files:
    for name, (start, end) in beginnings:
        try:
            score = Score.from_midi(midi_file, chord_range=(start, end), fast_chord_inference=False, quantization=8)
            tempo = score.config['tempo']
            time_signature = score.config['time_signature']
            if time_signature[0] != 4 and time_signature[1] != 4:
                print('Not 4/4, continuing')
                continue

            assert score.duration == 4 * (end - start), f"Wrong duration {score.duration} for {midi_file}"
            filepath = midi_file.replace('midi_files', f'extracted_orchestrations/{name}')
            # Create dir if not exists (recursively)
            if not os.path.exists(os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath))
            score.to_midi(filepath, tempo=tempo, time_signature=time_signature, one_track_per_instrument=False)
            score.to_file(filepath.replace('.mid', '.msl'))
        except Exception as e:
            print(e)
            continue