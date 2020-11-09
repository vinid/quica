"""
From Pietro Lesci and Dirk Hovy
"""

import sys
import time
import numpy as np
import pandas as pd
from typing import Dict, List
import scipy.special as ssp
from sklearn.metrics import accuracy_score

FILLER = '__XXX__'
MIN_ROWS = 2000
MIN_LABELS = 10
PRIORS_COL_NAME = 'PRIORS'
PRIORS_ANNOTATIONS_COL_NAME = 'Annotations'
CONTROLS_COL_NAME = 'CONTROLS'

# MACE configs
ALPHA = 0.5
BETA = 0.5
EM = False
ITERATIONS = 50
MAX_ITERATIONS = 1000
RESTARTS = 10
THRESHOLD = 1.0


class Mace(object):
    f"""
    Sets parameters and computes basic stats
    Parameters
    ----------
    inputfile : pandas.core.frame.DataFrame
        Name of the input file
    priors : Dict
        File name for prior likelihood of each label
    controls : List
        List of length inputfile.shape[0] with the true annotation
    alpha : float alpha > 0 defaults to {ALPHA}
        For VB, alpha parameter of the beta prior distribution
    beta : float beta > 0 defaults to {BETA}
        For VB, beta parameter of the beta prior distribution
    em : bool defalts to {EM}
        Flag to use EM training instead of VB
    iterations : int iterations > 0 defaults to {MAX_ITERATIONS / 10}
        Number of training iterations
    restarts : int restarts > 0 defaults to {RESTARTS}
        Number of random restarts
    threshold : float threshold > 0 defaults to {THRESHOLD}
        Percentage of instances (ordered by entropy) to keep
    smoothing : float smoothing > 0 defaults to 0.01/num_labels
        Smoothing parameter
    """

    def __init__(
        self,
        inputfile: pd.DataFrame,
        priors: Dict,
        controls: List,
        alpha: float,
        beta: float,
        em: bool,
        iterations: int,
        restarts: int,
        threshold: float,
        smoothing: float,
    ):

        # read inputs
        self.inputfile = inputfile
        self.unique_labels = np.unique(self.inputfile.values).tolist()
        # self.unique_labels.remove(FILLER)  # remove the empty label
        self.num_labels = len(self.unique_labels)
        self.num_instances, self.num_annotators = self.inputfile.values.shape

        self.priors = priors
        self.controls = controls
        self.alpha = alpha
        self.beta = beta
        self.em = em
        self.iterations = iterations
        self.restarts = restarts
        self.threshold = threshold
        self.smoothing = smoothing

        # set label to int dict
        self.label2int = {label: value for value, label in zip(
            range(self.num_labels), self.unique_labels)}
        self.label2int.update({FILLER: -1})


        # set int to label dict
        self.int2label = {value : label for label,
                                           value in self.label2int.items()}
        # translate input labels to indices
        self.labels = self.inputfile.replace(self.label2int).values.astype(int)

        # for each row, get the column indices with annotations
        self.active_annotations = [
            [i for i in range(len(row)) if row[i] > -1]
            for row in self.labels
        ]

        # initialize all parameters
        self.reset_params()

    def reset_params(self):
        """
        set all fractrional counts and priors to 0
        :return:
        """
        # initialize fractional counts
        self.gold_label_marginals = np.zeros(
            shape=(self.num_instances, self.num_labels)
        )


        self.label_preference_expected_counts = np.zeros(
            shape=(self.num_annotators, self.num_labels)
        )
        self.competence_expected_counts = np.zeros((self.num_annotators, 2))

        # initialize parameters
        self.competence = np.random.random((self.num_annotators, 2)) \
                          + self.smoothing
        self.competence = self.competence / \
                          self.competence.sum(axis=1).reshape(-1, 1)

        self.label_preference = np.random.random(
            (self.num_annotators, self.num_labels)
        ) + self.smoothing
        self.label_preference = self.label_preference / \
                                self.label_preference.sum(axis=1).reshape(-1, 1)

        # initialize priors
        self.competence_priors = np.ones(((self.num_annotators, 2)))
        self.competence_priors[:, 0] *= self.alpha
        self.competence_priors[:, 1] *= self.beta
        self.label_preference_priors = np.ones(
            (self.num_annotators, self.num_labels)) * 10.0

    def E_step(self):
        """
        EM and Variational Bayes Expectation step, collects
        fractional counts and computes likelihood.
        """
        # reset counts
        self.gold_label_marginals = np.zeros(
            shape=(self.num_instances, self.num_labels)
        )

        self.label_preference_expected_counts = np.zeros(
            shape=(self.num_annotators, self.num_labels)
        )

        self.competence_expected_counts = np.zeros((self.num_annotators, 2))

        # compute marginals
        self.log_marginal_likelihood = 0.0

        for d in range(self.num_instances):
            instance_marginal = 0.0

            # look only at non-empty lines
            if self.labels[d].sum() > -self.num_annotators:

                # 1. collect instance marginals
                # iterate over all labels
                for l in range(self.num_labels):

                    # TODO: CHECK THIS
                    if self.priors:
                        gold_label_marginal = self.priors[l]
                    else:
                        # uniform prior
                        gold_label_marginal = 1.0 / self.num_labels

                    # get only annotators who labeled
                    for a in self.active_annotations[d]:
                        annotation = self.labels[d][a]
                        spam_value = self.competence[a][1] \
                            if l == annotation else 0.0


                        gold_label_marginal *= self.competence[a][0] * \
                                               self.label_preference[a][annotation] + \
                                               spam_value

                    if (
                        not self.controls
                        or self.controls and self.controls[d] == l
                    ):
                        instance_marginal += gold_label_marginal
                        self.gold_label_marginals[d][l] = gold_label_marginal

                # 2. collect fractional counts, use the instance marginal in 1.
                self.log_marginal_likelihood += np.log(instance_marginal)

                for a in self.active_annotations[d]:
                    strategy_marginal = 0.0

                    annotation = self.labels[d][a]

                    if self.controls:
                        # if the annotator used the gold label
                        if annotation == self.controls[d]:
                            spam_value = self.competence[a][1] \
                                if self.controls[d] == annotation else 0.0
                            strategy_marginal += \
                                self.gold_label_marginals[d][l] / \
                                (self.competence[a][0] *
                                 self.label_preference[a][annotation] +
                                 spam_value)

                            strategy_marginal *= self.competence[a][0] * \
                                                 self.label_preference[a][annotation]

                            self.label_preference_expected_counts[a][annotation] += \
                                strategy_marginal / instance_marginal
                            self.competence_expected_counts[a][0] += \
                                strategy_marginal / instance_marginal
                            self.competence_expected_counts[a][1] += (
                                                                         self.gold_label_marginals[d][annotation] *
                                                                         self.competence[a][1] /
                                                                         (self.competence[a][0] *
                                                                          self.label_preference[a][annotation] +
                                                                          self.competence[a][1])) \
                                                                     / instance_marginal

                        # otherwise, update the observed strategy counts
                        # and the likelihood of competence
                        else:
                            self.label_preference_expected_counts[a][annotation] += 1.0
                            self.competence_expected_counts[a][0] += 1.0

                    # if controls is not defined
                    else:
                        for l in range(self.num_labels):
                            spam_value = \
                                self.competence[a][1] if l == annotation else 0.0
                            strategy_marginal += self.gold_label_marginals[d][l] / (
                                self.competence[a][0] * self.label_preference[a][annotation] + spam_value
                            )

                        strategy_marginal *= self.competence[a][0] * \
                                             self.label_preference[a][annotation]
                        self.label_preference_expected_counts[a][annotation] += strategy_marginal / \
                                                                                instance_marginal
                        self.competence_expected_counts[a][0] += strategy_marginal / \
                                                                 instance_marginal
                        self.competence_expected_counts[a][1] += (self.gold_label_marginals[d][annotation] *
                                                                  self.competence[a][1]
                                                                  / (self.competence[a][0] * self.label_preference[a][
                                annotation]
                                                                     + self.competence[a][1])
                                                                  ) / instance_marginal

    def M_step(self):
        """
        EM Maximization-step: normalize fractional counts
        :return:
        """
        self.competence_expected_counts = \
            self.competence_expected_counts + self.smoothing
        self.competence = self.competence_expected_counts / \
                          self.competence_expected_counts.sum(axis=1).reshape(-1, 1)

        self.label_preference_expected_counts = \
            self.label_preference_expected_counts + self.smoothing
        self.label_preference = self.label_preference_expected_counts / \
                                self.label_preference_expected_counts.sum(axis=1).reshape(-1, 1)

    def variational_M_step(self):
        """
        Variational Bayes Maximization-step: normalize
        fractional counts using digamma exponentiation
        """
        self.competence_expected_counts = \
            self.competence_expected_counts + self.competence_priors
        self.competence = \
            np.exp(ssp.digamma(self.competence_expected_counts)) / \
            np.exp(ssp.digamma(
                self.competence_expected_counts.sum(axis=1).reshape(-1, 1)
            ))

        self.label_preference_expected_counts = \
            self.label_preference_expected_counts + self.label_preference_priors
        self.label_preference = \
            np.exp(ssp.digamma(self.label_preference_expected_counts)) / \
            np.exp(ssp.digamma(
                self.label_preference_expected_counts.sum(axis=1).reshape(-1, 1)
            ))

    def fit(self):
        """
        fit selected model type on the data
        :return:
        """
        best_restart = 0
        best_log_marginal_likelihood = float('-inf')
        best_competence = self.competence.copy()
        best_label_preference = self.label_preference.copy()

        mode = 'vanilla' if self.em else 'variational Bayes'
        #if len(self.controls) > 0:
            #print("Running {} EM training with CONTROLS and the following settings:".format(
        #        mode), file=sys.stderr)
        #else:
            #print("Running {} EM training with the following settings:".format(
        #        mode), file=sys.stderr)
        #print("\t{} iterations".format(self.iterations), file=sys.stderr)
        #print("\t{} restarts".format(self.restarts), file=sys.stderr)
        #print("\tsmoothing = {}".format(self.smoothing), file=sys.stderr)
        #if not self.em:
            #print("\talpha = {}".format(self.alpha), file=sys.stderr)
            #print("\tbeta = {}".format(self.beta), file=sys.stderr)

        start = time.time()
        for restart in range(self.restarts):
            #print("=============", file=sys.stderr)
            #print("Restart {}".format(restart + 1), file=sys.stderr)
            #print("=============", file=sys.stderr)

            self.reset_params()
            self.E_step()
            #print("initial log marginal likelihood = {}".format(
                #self.log_marginal_likelihood), file=sys.stderr)

            for iter in range(self.iterations):
                if self.em:
                    self.M_step()
                else:
                    self.variational_M_step()

                self.E_step()

            #print("final log marginal likelihood = {}".format(
                #self.log_marginal_likelihood), file=sys.stderr)

            if self.log_marginal_likelihood > best_log_marginal_likelihood:
                best_restart = restart + 1
                best_log_marginal_likelihood = self.log_marginal_likelihood
                best_competence = self.competence.copy()
                best_label_preference = self.label_preference.copy()

        #print("\nTraining completed in {} sec".format(
        #    time.time() - start), file=sys.stderr)
        #print("Best model came from random restart number {} (log marginal likelihood: {})".format(
        #    best_restart, best_log_marginal_likelihood), file=sys.stderr)
        self.log_marginal_likelihood = best_log_marginal_likelihood
        self.competence = best_competence
        self.label_preference = best_label_preference

        # run E-Step to produce marginal likelihood of best model
        self.E_step()

        self.aggregate_labels = self.decode()

    def decode(self):
        """
        get most likely label for each instance
        :return:
        """
        entropies = self.get_label_entropies()
        entropy_threshold = self.get_entropy_for_threshold()
        result = []

        for d in range(self.num_instances):
            best_prob = float('-inf')
            best_label = -1

            if entropies[d] <= entropy_threshold:

                if entropies[d] == float('-inf'):
                    result.append('')
                else:
                    for l in range(self.num_labels):
                        if self.gold_label_marginals[d][l] > best_prob:
                            best_prob = self.gold_label_marginals[d][l]
                            best_label = l
                    result.append(self.int2label[best_label])

            else:
                result.append('')

        return result

    def decode_distribution(self):
        """
        get distribution over labels for each instance
        :return:
        """
        result = []

        for d in range(self.num_instances):
            if self.labels[d].sum() == -self.num_annotators:
                result.append('')
            else:
                probs = self.gold_label_marginals[d] / \
                        self.gold_label_marginals[d].sum()
                order = np.argsort(probs)[::-1]
                result.append(
                    list(zip([self.int2label[label] for label in order], probs[order])))

        return result

    def get_label_entropies(self):
        """
        compute entropy of each instance
        :return:
        #TODO: test!
        """
        result = []

        for d in range(self.num_instances):
            if self.labels[d].sum() == -self.num_annotators:
                result.append(float('-inf'))
            else:
                probs = self.gold_label_marginals[d] / \
                        self.gold_label_marginals[d].sum()
                entropy = np.where(probs > 0.0, -probs *
                                   np.log(probs), 0.0).sum()
                result.append(entropy)

        return result

    def get_entropy_for_threshold(self):
        """
        decide entropy-value cutoff for given threshold
        :return:
        TODO: DEPRRECATED?
        """
        if self.threshold == 0.0:
            pivot = 0
        elif self.threshold == 1.0:
            pivot = self.num_instances - 1
        else:
            pivot = int(self.num_instances * self.threshold)

        entropies = self.get_label_entropies()
        return np.sort(entropies)[pivot]

    def get_test(self):
        """
        compare predicted labels against gold standard and compute accurracy
        :return:
        """
        with open(self.test) as test_file:
            gold = [line.strip() for line in test_file.readlines()]
        #print(gold, self.labels, self.aggregate_labels)
        assert len(
            gold) == self.num_instances, 'Gold labels and input file have different number of instances ({} vs {})'.format(
            len(gold), self.num_instances)
        #print(accuracy_score(gold, self.aggregate_labels))

"""
coder_1 = ["0", "1", "0", "1", "0", "1", "0"]
coder_3 = ["0", "1", "0", "1", "0", "0", "1"]
coder_4 = ["0", "1", "0", "1", "0", "0", "1"]

dataframe = pd.DataFrame({"coder1": coder_4,
                          "coder3": coder_4,
                          "coder4": coder_4})

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
#print(algo.competence[:, 1])
#print(algo.decode())

"""
