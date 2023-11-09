from musiclang.library import *
from musiclang import ScoreFormatter, VoiceLeading, Score
import argparse

def main(melody_file, chords_file, orchestration_file, output_path):
    score_orchestra = Score.from_midi(orchestration_file)
    orchestra = score_orchestra.project_on_one_chord().to_orchestra(pattern=True, drop_drums=False)
    score_melody = Score.from_file(melody_file)
    text = open(chords_file, 'r').read()
    chords = ScoreFormatter(text).parse().to_custom_chords(max_iter=1000, max_iter_rules=1000).to_chords(duration=True)
    score = Score.from_orchestration(orchestra, chords, chord_rhythm=True, use_pattern=True)
    # score = VoiceLeading(fixed_bass='piano__0')(score)
    score = score_melody.project_on_score(score, voice_leading=False, keep_score=True)
    score.to_midi(output_path)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--chords', default='data/chords/bach_chorale.rntxt')
    parser.add_argument('--melody_file', default='data/melodies/batman.msl')
    parser.add_argument('--orchestration', default='data/orchestrations/crash_bandicoot.mid')
    parser.add_argument('--output_path', default="output.mid")

    args = parser.parse_args()
    chords_file = args.chords
    melody_file = args.melody
    orchestration_file = args.path_orchestration
    output_path = args.output_path



    main(melody_file, chords_file, orchestration_file, output_path)