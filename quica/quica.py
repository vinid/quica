"""Main module."""

from quica.dataset.dataset import IRRDataset
from quica.measures.irr import *
import pandas as pd

class Quica:

    def __init__(self, dataset: IRRDataset = None, dataframe: pd.DataFrame = None):

        if dataset is not None and dataframe is not None:
            raise Exception("No input option selected, add a dataset or a dataframe")

        if dataset is not None:
            self.dataset = dataset
        else:
            self.dataset = IRRDataset(dataframe.values.T)

    def save_to_csv(self, csv_path):
        df = self.get_results()
        df.to_csv(csv_path)

    def get_latex(self):
        df = self.get_results()
        return df.to_latex()

    def get_results(self):
        measures = [Krippendorff(), ScottsPI(), RawAgreement(), MaceIRR()]
        names = ["Krippendorff's Alpha", "Scotts' Kappa", "Raw Agreement", "MACE"]

        if self.dataset.coders == 2:
            measures.append(CohensK())
            names.append("Cohen's K")
        else:
            measures.append(FleissK())
            names.append("Fleiss'K")

        results = []
        for measure in measures:
            results.append(measure.compute_irr(self.dataset))

        data = pd.DataFrame({"measure": names, "score": results})
        data.index = data["measure"]
        del data["measure"]
        return data



