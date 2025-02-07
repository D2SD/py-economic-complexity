"""Cross-space module
"""

import numpy as np
import pandas as pd


def cross_proximity(rcas_a, rcas_b):
    """Calculates the Cross-proximity index between two matrices of RCA.

    Catalan et al. (2020) introduced the cross-proximity index in order
    to measure the minimum probability that a country presents comparative
    advantages in a patent in a given area, given it has comparative
    advantages in an area of ​​knowledge, or vice versa, where values ​​that
    are more close to unity indicate a stronger relationship between the
    patent area and the knowledge area.

    Note the characteristic in both RCA matrices can't be the location.

    Args:
        rcas_a (pd.DataFrame) -- A matrix of pivotted data for RCA, obtained
            from the RCA function, for a main characteristic to evaluate.
        rcas_b (pd.DataFrame) -- The pivot table obtained from the RCA
            function, for a secondary characteristic to evaluate.

    Returns:
        (pd.DataFrame) -- A matrix with the proximity between the two types
            of evaluated elements that can be used in the calculation of the
            cross-relatedness.
    """
    # Trims RCA values to [0,1]
    rcas_a[rcas_a >= 1] = 1
    rcas_a[rcas_a < 1] = 0
    rcas_b[rcas_b >= 1] = 1
    rcas_b[rcas_b < 1] = 0

    # Calculates numerator of array
    numerator = rcas_a.T.dot(rcas_b)

    # Calculates kp0 for rcas_a and rcas_b
    kp0_a = rcas_a.sum(axis=0)
    kp0_a = kp0_a.values.reshape((1, len(kp0_a)))

    kp0_b = rcas_b.sum(axis=0)
    kp0_b = kp0_b.values.reshape((1, len(kp0_b)))

    # Calculates two possible cross proximity values and replace posibles NaN values
    a = numerator.divide(kp0_b).fillna(0)
    b = numerator.divide(kp0_a.T).fillna(0)

    # Compares the two previous arrays, and keeps minimum value of each cell
    x_proximity = pd.DataFrame(
        [np.minimum(x, y) for x, y in zip(a.values, b.values)],
        index=a.index,
        columns=a.columns
    )
    return x_proximity


def cross_relatedness(rcas: pd.DataFrame, x_proximity: pd.DataFrame):
    """Calculates the Cross-relatedness.

    Catalan et al. (2020) incorporated the concept of cross-relatedness
    in order to quantify the relationship between scientific fields in the
    development of new technologies in a country. The density crossing
    takes values ​​between zero and one, mathematically it corresponds to
    the average cross proximity of a technology and the scientific knowledge
    of a country during the period of time.

    Note it's important to be consistent with the name of the variables
    when calculating cross-proximity and cross-relatedness.
    To display the outputted values, the series must be transformed into
    a dataframe in tidy format as shown below:

        x_relatedness = cross_relatedness(rcas, cross_proximity)
        x_relatedness.unstack().reset_index(name="cross_relatedness")

    Args:
        rcas (pd.DataFrame) -- A pivotted table obtained from the RCA
            function, for the main characteristic to evaluate.
        x_proximity {} -- The cross-proximity matrix obtained between the
            `rcas` matrix in the first parameter, and another RCA matrix.

    Returns:
        (pd.DataFrame) -- A matrix with the probability that a location
            generates comparative advantages in the characteristic to be
            evaluated considering its proximity with the other evaluated
            characteristic.
    """
    rcas = rcas.copy()
    rcas[rcas >= 1] = 1
    rcas[rcas < 1] = 0

    numerator = rcas.dot(x_proximity)

    rcas_ones = rcas * 0
    rcas_ones = rcas + 1

    denominator = rcas_ones.dot(x_proximity)

    x_relatedness = numerator / denominator
    return x_relatedness
