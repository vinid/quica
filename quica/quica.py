"""Main module."""
import pandas as pd
from quica.dataset.dataset import IRRDataset
from quica.measures.irr import *

class Quica:

    def __init__(self):
        pass

    def save_to_csv(self, dataset: IRRDataset):
        pass

    def get_latex(self, dataset: IRRDataset):
        pass

    def get_results(self, dataset: IRRDataset):
        measures = [Krippendorff(), FleissK(), ScottsPI()]
        names = ["krippendorf", "fleiss", "scotts"]

        if dataset.coders == 2:
            measures.append(CohensK())
            names.append("cohen")

        results = []
        for measure in measures:
            results.append(measure.compute_irr(dataset))

        data = pd.DataFrame({"names": names, "score": results})
        data.index = data["names"]
        del data["names"]
        return data



