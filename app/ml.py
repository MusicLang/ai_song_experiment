"""
Author: Florian GARDIN
"""

from musiclang import ScoreFormatter
from musiclang.library import *
from musiclang import Score
from musiclang.write.out.constants import *
import tempfile
from tqdm import tqdm
from .proximity import get_nearest_scores

def predict_score_orchestra(score, n_chords=None, temperature=0.5, chord_duration=None, retry=0):
    """
    Predict the continuation of a score with the same instruments as the input score.
    There is an engineering hack because MusicLang model is better at outputing piano music.
    :param score: musiclang.Score
    :param n_chords: int
    :param temperature: float
    :param chord_duration:
    :param retry:
    :return:
    """
    with tempfile.NamedTemporaryFile(suffix='.mid', delete=True) as file:
        score.to_midi(file.name)
        score = Score.from_midi(file.name)

    instruments = score.instruments
    instrument_replace_dict = {}
    instrument_idx = {}
    idx = -1
    for instrument in instruments:
        name, part = instrument.split('__')
        if instrument not in instrument_idx:
            idx += 1
            instrument_replace_dict[instrument] = f'piano__{idx}'

    # Replace instruments in score
    score_instrument = score.replace_instruments(**instrument_replace_dict)
    score_instrument = score_instrument.remove_silenced_instruments()
    inv_instrument_replace_dict = {val: key for key, val in instrument_replace_dict.items()}
    # Predict score

    # For each chord make a chord with the same duration
    if chord_duration is None:
        chord_duration = score_instrument.chords[0].duration

    predicted_score = score_instrument.copy()
    if n_chords is None:
        n_chords = len(score.chords)

    for idx in range(n_chords):
        while retry > 0:
            try:
                predicted_score = predicted_score.predict_score(n_chords=1, temperature=temperature, normalize_midi=False)
                break
            except Exception as e:
                print('error')
                if retry == 0:
                    raise e
                retry -= 1
                continue

        # Select only instruments from instrument_idx
        existing_instruments = score_instrument.instruments
        predicted_score = predicted_score[existing_instruments]
        #predicted_score = predicted_score[1:]

        # Reproject instruments, if not existing drop
        predicted_score = predicted_score.arrange_chords_duration(chord_duration)
        predicted_score = predicted_score.remove_silenced_instruments()

    predicted_score = predicted_score.replace_instruments(**inv_instrument_replace_dict)

    return predicted_score


def create_variations(pattern, nb_variations=4, temperature=0.5, chord_duration=None, retry=2):
    # Predict following
    scores = []
    nb_chords = len(pattern.chords)
    for i in tqdm(range(nb_variations)):
        predicted_score = predict_score_orchestra(pattern, n_chords=nb_chords,
                                                  temperature=temperature, chord_duration=chord_duration, retry=retry)
        scores.append(predicted_score[nb_chords:])
    return scores

def create_best_variations(pattern, nb_variations=4, nb_kept=2, temperature=0.5, chord_duration=None, retry=2):
    pattern = pattern.remove_silenced_instruments()
    scores = create_variations(pattern, nb_variations=nb_variations, temperature=temperature, chord_duration=chord_duration, retry=retry)
    return get_nearest_scores(pattern, scores, nb=nb_kept)
