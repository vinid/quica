#!/usr/bin/env python

"""Tests for `quica` package."""

import pytest


from quica import quica
from quica.measures.irr import *
from quica.dataset.dataset import IRRDataset

@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')

def test_complete_agreement():
    coder_1 = [0, 1, 0, 1, 0, 1]
    coder_2 = [0, 1, 0, 1, 0, 1]
    coder_3 = [0, 1, 0, 1, 0, 0]

    agreeing_coders = [coder_1, coder_2]
    agreeing_dataset = IRRDataset(agreeing_coders)

    disagreeing_coders = [coder_1, coder_3]
    disagreeing_dataset = IRRDataset(disagreeing_coders)

    kri = Krippendorff()
    cohen = CohensK()

    assert kri.compute_irr(agreeing_dataset) == 1
    assert cohen.compute_irr(agreeing_dataset) == 1
    assert cohen.compute_irr(disagreeing_dataset) < 1
    assert cohen.compute_irr(disagreeing_dataset) < 1

