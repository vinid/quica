#!/usr/bin/env python

"""Tests for `quica` package."""

from quica.measures.irr import *
from quica.dataset.dataset import IRRDataset
from quica.quica import Quica
import pandas as pd
from pandas._testing import assert_frame_equal

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
    fliess = FleissK()
    scotts = ScottsPI()

    assert kri.compute_irr(agreeing_dataset) == 1
    assert cohen.compute_irr(agreeing_dataset) == 1
    assert cohen.compute_irr(disagreeing_dataset) < 1
    assert cohen.compute_irr(disagreeing_dataset) < 1
    assert fliess.compute_irr(disagreeing_dataset) < 1
    assert fliess.compute_irr(agreeing_dataset) == 1
    assert scotts.compute_irr(agreeing_dataset) == 1
    assert scotts.compute_irr(disagreeing_dataset) < 1

def test_quica_complete():


    coder_1 = [0, 1, 0, 1, 0, 1]
    coder_3 = [0, 1, 0, 1, 0, 0]

    dataframe = pd.DataFrame({"coder1" : coder_1,
                  "coder3" : coder_3})

    disagreeing_coders = [coder_1, coder_3]
    disagreeing_dataset = IRRDataset(disagreeing_coders)

    quica = Quica(disagreeing_dataset)
    first_set = (quica.get_results())

    quica = Quica(dataframe=dataframe)
    second_set = (quica.get_results())
    assert first_set.equals(second_set)
