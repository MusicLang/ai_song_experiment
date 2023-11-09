import glob
import os
from musiclang import Score

midi_files = glob.glob('data/midi_files/**/*.mid', recursive=True)
output_path = 'data/extracted_chords_augmented'
if not os.path.exists(output_path):
    os.makedirs(output_path)

def build_formatted_chord_list(score, chord_list, tonality):
    time_signature = score.config['time_signature']
    formatted_score = [
        "Time Signature: " + f"{time_signature[0]}/{time_signature[1]}",
        "Tonality: " + f"{tonality}",
    ]
    for idx, chord in enumerate(chord_list):
        formatted_score.append(f"m{idx+1} {chord}")
    return "\n".join(formatted_score)


for midi_file in midi_files:
    try:
        score = Score.from_midi(midi_file, fast_chord_inference=False)
        chords = score.config['annotation']
        filepath = midi_file.replace('.mid', '.rntxt').replace('midi_files', 'extracted_chords_augmented')
        # Create dir if not exists
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        with open(filepath, 'w') as f:
            f.write(chords)
    except Exception as e:
        print(e)
        continue
