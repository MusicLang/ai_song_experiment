from musicpy import *
import glob
import os
from musiclang import Score

midi_files = glob.glob('data/midi_files/**/*.mid', recursive=True)
output_path = 'data/extracted_melodies'
if not os.path.exists(output_path):
    os.makedirs(output_path)

def get_note_density(score, ins):

    nb_chords = len(score.chords)
    silences = 0
    for chord in score.chords:
        notes = chord.score[ins].notes
        if len(notes) == 1 and notes[0].is_silence:
            silences += 1
    return (nb_chords - silences) / nb_chords
def extract_sub_melodies(score):
    # Keep only instruments with __0
    instruments = score.instruments

    # Delete instruments that are not monophonic
    to_delete = set()
    to_delete_name = set()
    for ins in instruments:
        name = ins.split('__')[0]
        print(name, ins)
        if not '__0' in ins:
            to_delete.add(ins)
            to_delete_name.add(name)

    kept_instruments = [ins for ins in instruments if ins.split('__')[0] not in to_delete_name]
    score = score[list(kept_instruments)]
    print(kept_instruments)
    # Split melody for each instrument
    instrument_dict = {}
    for ins in kept_instruments:
        score_instrument = score[ins]
        # Kept the ones with enough note density
        if get_note_density(score_instrument, ins) > 0.5:
            instrument_dict[ins.split('__')[0]] = score_instrument

    return instrument_dict

for midi_file in midi_files:
    try:
        a, bpm, start_time = read(midi_file).merge()
        example_melody = a.split_melody(mode='chord')
        filepath = midi_file.replace('midi_files', 'extracted_melodies')
        filepath_msl = filepath.replace('.mid', '.msl')
        # Create dir if not exists
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

        write(example_melody, bpm, name=filepath)
        # Load with musiclang
        score = Score.from_midi(filepath)
        score = score.remove_drums()

        instrument_dict = extract_sub_melodies(score)

        # Save each instrument into files
        for instrument_name, instrument_score in instrument_dict.items():
            filepath_msl = filepath.replace('.mid', f'__{instrument_name}.msl')
            instrument_score.to_file(filepath_msl)
    except Exception as e:
        print(e)
        continue