from musiclang.library import *
from musiclang import ScoreFormatter, VoiceLeading, Score
import argparse
import random
import glob
import json
import os
import shutil
from musiclang import Silence, Note
from musiclang.library import *

def main(melody_file, chords_file, orchestration_file, output_path):
    print('Loading orchestra ...')
    score_orchestra = Score.from_file(orchestration_file)
    print('Loading melody ...')
    score_melody = Score.from_file(melody_file)
    #score_melody = (I % I.M)(string_ensemble_1__0=s0 + s1 + s2 + s4) + (I % I.M)(string_ensemble_1__0=s2.h + s4 + s2.e + s1.e)
    score_melody = score_melody.ff
    print('Loading chords ...')
    text = open(chords_file, 'r').read()
    print('Projecting orchestration ...')
    orchestra = score_orchestra.project_on_one_chord().to_orchestra(pattern=True, drop_drums=False)
    chords = ScoreFormatter(text).parse().to_custom_chords(max_iter=0, max_iter_rules=0).to_chords(duration=True)
    score = Score.from_orchestration(orchestra, chords, chord_rhythm=True, use_pattern=True)

    print('Projecting melody on orchestration and removing conflicting parts ...')
    score_melody = score_melody.replace_instruments(**{score_melody.instruments[0]: 'string_ensemble_1__0'})
    score_melody = score_melody.create_instruments_suffix(offset=100)
    # Get the instrument with the most comparable pitch range
    melody_pitch_statistics = score_melody.get_pitch_statistics()
    min_pitch, max_pitch, mean_pitch, std_pitch = melody_pitch_statistics[score_melody.instruments[0]]
    instrument = score.get_pitch_most_comparable_instrument(mean_pitch)
    instrument_name = instrument.split('__')[0]
    deleted_score = score.get_instrument_names([instrument_name])
    maximum_density_instrument = deleted_score.get_maximum_density_instrument(exclude_instruments=None).instruments[0]
    deleted_score_max_density_rhythms = [chord.score.get(maximum_density_instrument,  Note("s", 0, 0, chord.duration).to_melody()) for chord in deleted_score.chords]
    # Project melody on this rhythm
    score_melody = score_melody.repeat_until_duration(deleted_score.duration)
    #score_melody = score_melody.project_on_rhythm_chord_per_chord(deleted_score_max_density_rhythms)

    #score = score.delete_instrument_names([instrument_name])
    print('Optimizing melody projection')
    orchestra_melody = score_melody[0:4].project_on_one_chord().to_orchestra(pattern=True, drop_drums=False)
    score_melody = Score.from_orchestration(orchestra_melody, chords, chord_rhythm=True, use_pattern=True)
    print('Now projecting melody on score ...')
    score = score_melody.project_on_score(score, voice_leading=False, keep_score=True)
    print('Finished projecting, now saving midi')
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    score_orchestra.to_midi(os.path.join(output_path, 'orchestra.mid'), one_track_per_instrument=False)
    score.to_midi(os.path.join(output_path, 'output.mid'), one_track_per_instrument=False, tempo=score_orchestra.config['tempo'])
    # Copy original chords, orchestra and melody to output_path

    shutil.copy(chords_file, os.path.join(output_path, 'chords.rntxt'))

    shutil.copy(melody_file, os.path.join(output_path, 'melody.msl'))
    # Save midi file of melody
    score_melody.to_midi(os.path.join(output_path, 'melody.mid'), one_track_per_instrument=False)


if __name__ == '__main__':

    base_chords = 'data/extracted_chords'
    base_melodies = 'data/extracted_melodies'
    base_orchestrations = 'data/extracted_orchestrations/mid'
    base_output = 'data/output'
    base_playlist = 'data/output/playlist'
    # Select one chord, one melody and one orchestration at random
    chords_files = glob.glob(f'{base_chords}/**/*.rntxt', recursive=True)
    melody_files = glob.glob(f'{base_melodies}/**/*.msl', recursive=True)
    orchestration_files = glob.glob(f'{base_orchestrations}/**/*.msl', recursive=True)
    n_gen = 10

    max_idx = 0
    for i in range(n_gen):

        try:
            chords_file = random.choice(chords_files)
            melody_file = random.choice(melody_files)
            orchestration_file = random.choice(orchestration_files)
            # Create a dict with selected path without base path
            dictionary = {"chords": chords_file.replace(base_chords, ""), "melody": melody_file.replace(base_melodies, ""), "orchestration": orchestration_file.replace(base_orchestrations, "")}
            existing_output = [int(l) for l in os.listdir(base_output) if l.isdigit()]
            if len(existing_output) == 0:
                output_path = os.path.join(base_output, '0')
            else:
                max_idx = max(existing_output) + 1
                output_path = os.path.join(base_output, str(max_idx))

            # Create output path directory if not exist

            if not os.path.exists(base_playlist):
                os.makedirs(base_playlist)

            output_playlist_path = os.path.join(base_playlist, f'{max_idx}.mid')
            main(melody_file, chords_file, orchestration_file, output_path)
            shutil.copy(os.path.join(output_path, 'output.mid'), output_playlist_path)
            with open(os.path.join(output_path, 'metadata.json'), 'w') as f:
                json.dump(dictionary, f)
        except Exception as e:
            print(e)
            pass