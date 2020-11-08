from abc import ABC, abstractmethod
import krippendorff
from quica.dataset.dataset import IRRDataset
from sklearn.metrics import cohen_kappa_score
from nltk import agreement
from itertools import combinations
from quica.internal.measures import *
from sklearn.metrics import accuracy_score
import numpy as np

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

class CohensK(IRRMeasure):
    def __init__(self):
        super().__init__()

    def compute_irr(self, dataset: IRRDataset):

        if dataset.coders > 2:
            raise Exception("Cohen's K supported only for two coders")

        return cohen_kappa_score(dataset.get_coder(0), dataset.get_coder(1))


class FleissK(IRRMeasure):
    """
    taking strong inspiration from: https://learnaitech.com/how-to-compute-inter-rater-reliablity-metrics-cohens-kappa-fleisss-kappa-cronbach-alpha-kripndorff-alpha-scotts-pi-inter-class-correlation-in-python/
    """
    def __init__(self):
        super().__init__()

    def compute_irr(self, dataset: IRRDataset):

        formatted_codes = []

        for i in range(0, dataset.coders):
            coder_data = dataset.get_coder(i)
            data_formatted = [[i, n, coder_data[n]] for n in range(len(coder_data))]
            formatted_codes.extend(data_formatted)

        ratingtask = agreement.AnnotationTask(data=formatted_codes)

        return ratingtask.multi_kappa()

class ScottsPI(IRRMeasure):
    """
    taking strong inspiration from: https://learnaitech.com/how-to-compute-inter-rater-reliablity-metrics-cohens-kappa-fleisss-kappa-cronbach-alpha-kripndorff-alpha-scotts-pi-inter-class-correlation-in-python/
    """
    def __init__(self):
        super().__init__()

    def compute_irr(self, dataset: IRRDataset):

        formatted_codes = []

        for i in range(0, dataset.coders):
            coder_data = dataset.get_coder(i)
            data_formatted = [[i, n, coder_data[n]] for n in range(len(coder_data))]
            formatted_codes.extend(data_formatted)

        ratingtask = agreement.AnnotationTask(data=formatted_codes)

        return ratingtask.pi()

class RawAgreement(IRRMeasure):

    def __init__(self):
        super().__init__()

    def compute_irr(self, dataset: IRRDataset):

        comb = combinations(dataset.data, 2)

        return np.mean([accuracy_score(a,b) for a,b in comb])

class MaceIRR(IRRMeasure):

    def __init__(self):
        super().__init__()

    def compute_irr(self, dataset):

        dataframe = pd.DataFrame(data=dataset.data).applymap(lambda x : str(x))

        algo = Mace(
            inputfile=dataframe,
            priors={},
            alpha=ALPHA,
            beta=BETA,
            em=EM,
            controls=[],
            iterations=ITERATIONS,
            restarts=RESTARTS,
            threshold=THRESHOLD,
            smoothing=0,
        )
        algo.fit()
        return np.mean(algo.competence[:, 1])




