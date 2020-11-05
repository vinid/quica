from abc import ABC, abstractmethod
import krippendorff
from quica.dataset.dataset import IRRDataset
from sklearn.metrics import cohen_kappa_score

class IRRMeasure(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def compute_irr(self, dataset):
        pass


class Krippendorff(IRRMeasure):
    def __init__(self):
        super().__init__()

    def compute_irr(self, dataset: IRRDataset):
        return krippendorff.alpha(dataset.data)

class CohensK:
    def __init__(self):
        super().__init__()

    def compute_irr(self, dataset: IRRDataset):

        if dataset.coders > 2:
            raise Exception("Cohen's K supported only for two coders")

        return cohen_kappa_score(dataset.get_coder(0), dataset.get_coder(1))
