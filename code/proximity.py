"""
Author: Florian GARDIN
"""
import numpy as np


def get_proximity_score(reference, other):
    """
    Get the proximity between two scores using following features:
    - Number of instruments in common
    - Proximity of mean pitch range for each instrument
    - Proximity of std pitch range for each instrument
    - Same note density for each instrument
    :param reference: musiclang.Score
    :param other: musiclang.Score
    :return:
    """
    other = other.remove_silenced_instruments()

    reference = reference.remove_silenced_instruments()
    pitch_statistics = reference.get_pitch_statistics()
    densities = reference.extract_densities()
    instruments = reference.instruments

    # Get number of instruments in common
    instruments_common = set(instruments).intersection(other.instruments)
    n_instruments = len(instruments_common) / len(instruments)
    if len(instruments_common) == 0:
        return 0, -10, -10, -10

    # Get mean pitch range for each instrument
    pitch_statistics_other = other.get_pitch_statistics()
    mean_pitch_diff = np.mean([abs(pitch_statistics[ins][2] - pitch_statistics[ins][2]) for ins in instruments_common])

    # Get std pitch range for each instrument
    std_pitch_diff = np.mean([abs(pitch_statistics[ins][3] - pitch_statistics[ins][3]) for ins in instruments_common])

    # Get same note density for each instrument
    densities_other = other.extract_densities()
    density_diff = np.mean([abs(densities[ins] - densities_other[ins]) for ins in instruments_common])

    return -n_instruments, mean_pitch_diff, std_pitch_diff, density_diff


def get_nearest_scores(reference, scores, nb=2):
    """
    Sort scores by proximity to reference score
    :param reference: musiclang.Score
    :param scores: list of musiclang.Score
    :param nb: int: number of scores to return
    :return:
    """
    scores_proximity = []
    for score in scores:
        scores_proximity.append(get_proximity_score(reference, score))
    scores_proximity = np.array(scores_proximity)

    # Rank propositions by each kind of score
    order = scores_proximity.argsort(axis=0)
    ranks = order.argsort(axis=0)
    ranks[:, 0] *= 10
    # Penality for nb instruments in common
    # Get mean rank
    scores_proximity_rank = np.mean(ranks, axis=1)
    # return top nb scores
    indexes = np.argsort(scores_proximity_rank)[:nb]
    return [scores[idx] for idx in indexes]