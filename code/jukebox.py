"""
Author: Florian GARDIN
"""

import os
from musiclang import Score
from musiclang.transform.library import create_counterpoint_on_score
import numpy as np

def get_instruments_from_pitch(score, high=False):
    pitch_statistics = score.get_pitch_statistics()
    # Get top 50%
    pitch_median = np.median([s[2] for ins, s in pitch_statistics.items()])
    if high:
        kept_instruments = [ins for ins, s in pitch_statistics.items() if s[2] > pitch_median]
    else:
        kept_instruments = [ins for ins, s in pitch_statistics.items() if s[2] < pitch_median]
    return score[kept_instruments]

def manipulate(score1, score2, score_chords, reorchestrate=False):
    """
    Create a musical projection of score1 and score2 on score_chords
    score1 is used as an orchestration (Filter the bass and the most dense instrument)
    score2 is used as a melody (Filter the high range instruments)
    :param score1: Score
    :param score2: Score
    :param score_chords: Score
    :return:
    """
    # Project score1
    score = score1.project_on_score(score_chords, voice_leading=False, keep_score=False)
    densities = score.extract_densities()
    # Remove drums from densities
    densities = {k: v for k, v in densities.items() if 'drums' not in k}
    max_density_instrument = max(densities, key=densities.get).split('__')[0]
    # Also get lowest instrument (bass)
    pitch_statistics = score.get_pitch_statistics()
    lowest_instrument = min(pitch_statistics, key=lambda x: pitch_statistics[x][2]).split('__')[0]
    all_drums = list(set([ins for ins in score.instruments if ins.startswith('drums')]))
    drums = None
    if len(all_drums):
        drums = score[all_drums]

    score = score.get_instrument_names([max_density_instrument, lowest_instrument])
    fixed_parts = score.instruments

    # Project score2
    score2 = score2.create_instruments_suffix(offset=100)

    # Remove drums
    score2 = score2.remove_drums()
    # Keep only highest end of score
    pitch_statistics = score2.get_pitch_statistics()
    # Get top 50%
    pitch_median = np.median([s[2] for ins, s in pitch_statistics.items()])
    kept_instruments = [ins for ins, s in pitch_statistics.items() if s[2] > pitch_median]
    score2 = score2[kept_instruments]

    score = score2.project_on_score(score, voice_leading=False, keep_score=True)

    # score2_other = score2.create_instruments_suffix(offset=200) & -2
    # print(score2_other.instruments)
    # score = score2_other.project_on_score(score, voice_leading=False, keep_score=True)

    score = create_counterpoint_on_score(score, fixed_parts=fixed_parts)

    if drums is not None:
        score = drums.project_on_score(score, voice_leading=False, keep_score=True)

    return score

def mix_songs(path1, path2, path_chords, chord_range=(0, 16)):
    # Load three scores
    score1 = Score.from_midi(path1, chord_range=chord_range, quantization=8, fast_chord_inference=True)
    score2 = Score.from_midi(path2, chord_range=chord_range, quantization=8, fast_chord_inference=True)
    score_chords = Score.from_midi(path_chords, chord_range=chord_range, quantization=8, fast_chord_inference=True)

    ts1 = score1.config['time_signature']
    ts2 = score2.config['time_signature']
    ts_chords = score_chords.config['time_signature']

    assert ts1 == ts2 == ts_chords, f"Time signatures must all be the same, score1: {ts1}, score2: {ts2}, chords: {ts_chords}"

    # Project score1
    score = manipulate(score1, score2, score_chords)
    return score

