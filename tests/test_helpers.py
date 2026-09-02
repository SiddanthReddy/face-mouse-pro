"""
Unit tests for helper calculations, EAR, MAR, and One-Euro Filter.
"""

import pytest

from src.utils.helpers import ExponentialFilter, OneEuroFilter2D, calculate_ear, calculate_mar, euclidean_distance


def test_euclidean_distance():
    p1 = (0.0, 0.0)
    p2 = (3.0, 4.0)
    assert euclidean_distance(p1, p2) == pytest.approx(5.0)

    p3d_1 = (1.0, 2.0, 3.0)
    p3d_2 = (4.0, 6.0, 3.0)
    assert euclidean_distance(p3d_1, p3d_2) == pytest.approx(5.0)


def test_calculate_ear():
    # Canonical open eye coordinates
    # P1 (outer), P2 (top-outer), P3 (top-inner), P4 (inner), P5 (bot-inner), P6 (bot-outer)
    open_eye = [
        (0.0, 0.0),  # P1
        (0.2, 0.15),  # P2
        (0.4, 0.15),  # P3
        (0.6, 0.0),  # P4
        (0.4, -0.15),  # P5
        (0.2, -0.15),  # P6
    ]
    ear_open = calculate_ear(open_eye)
    assert ear_open > 0.25

    # Closed eye coordinates (vertical heights near zero)
    closed_eye = [(0.0, 0.0), (0.2, 0.01), (0.4, 0.01), (0.6, 0.0), (0.4, -0.01), (0.2, -0.01)]
    ear_closed = calculate_ear(closed_eye)
    assert ear_closed < 0.10
    assert ear_closed < ear_open


def test_calculate_mar():
    # Open mouth (large vertical aperture)
    open_mouth = [
        (0.0, 0.0),  # P1
        (0.3, 0.25),  # P2
        (0.5, 0.25),  # P3
        (0.8, 0.0),  # P4
        (0.5, -0.25),  # P5
        (0.3, -0.25),  # P6
    ]
    mar_open = calculate_mar(open_mouth)
    assert mar_open > 0.40

    # Closed mouth
    closed_mouth = [(0.0, 0.0), (0.3, 0.02), (0.5, 0.02), (0.8, 0.0), (0.5, -0.02), (0.3, -0.02)]
    mar_closed = calculate_mar(closed_mouth)
    assert mar_closed < 0.20


def test_exponential_filter():
    f = ExponentialFilter(alpha=0.5)
    assert f.update((10.0, 10.0)) == (10.0, 10.0)
    # Next step: 0.5 * 20 + 0.5 * 10 = 15.0
    res = f.update((20.0, 20.0))
    assert res[0] == pytest.approx(15.0)
    assert res[1] == pytest.approx(15.0)


def test_one_euro_filter_2d():
    f = OneEuroFilter2D(min_cutoff=1.0, beta=0.01)
    t0 = 100.0
    p0 = f.filter((100.0, 200.0), timestamp=t0)
    assert p0 == pytest.approx((100.0, 200.0))

    # Next timestamp step
    t1 = 100.033
    p1 = f.filter((105.0, 205.0), timestamp=t1)
    assert p1[0] > 100.0 and p1[0] < 105.0
