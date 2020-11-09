======================================
Quick Inter Coder Agreement in Python
======================================


Quica (Quick Inter Coder Agreement in Python) is a tool to run inter coder agreement pipelines in an easy and effective way.
Multiple measures are run and results are collected in a single table than can be easily exported in Latex.
quica supports binary or multiple coders.

.. image:: https://raw.githubusercontent.com/vinid/quica/master/logo.svg

.. image:: https://img.shields.io/pypi/v/quica.svg
        :target: https://pypi.python.org/pypi/quica

.. image:: https://github.com/vinid/quica/workflows/Python%20package/badge.svg
        :target: https://github.com/vinid/quica/actions

.. image:: https://readthedocs.org/projects/quica/badge/?version=latest
        :target: https://quica.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
        :target: https://lbesson.mit-license.org/
        :alt: License

Quick Inter Coder Agreement in Python


* Free software: MIT license
* Documentation: https://quica.readthedocs.io.

Installation
------------

.. code-block:: bash

    pip install -U quica

Jump start Tutorial
-------------------

.. |colab1| image:: https://colab.research.google.com/assets/colab-badge.svg
    :target: https://colab.research.google.com/drive/14x6OOQ09Ojn54mNH8JY83bztrJ61yg0o?usp=sharing
    :alt: Open In Colab


+----------------------------------------------------------------+--------------------+
| Name                                                           | Link               |
+================================================================+====================+
| Different possible usages of QUICA                             | |colab1|           |
+----------------------------------------------------------------+--------------------+

Get Quick Agreement
-------------------

If you already have a python dataframe you can run Quica with few liens of code! Let's assume you have two
coders; we will create a pandas dataframe just to show how to use the library. As for now, we support only integer values
and we still have not included weighting.

.. code-block:: python

    from quica.quica import Quica
    import pandas as pd

    coder_1 = [0, 1, 0, 1, 0, 1]
    coder_3 = [0, 1, 0, 1, 0, 0]

    dataframe = pd.DataFrame({"coder1" : coder_1,
                  "coder3" : coder_3})

    quica = Quica(dataframe=dataframe)
    print(quica.get_results())

This is the expected output:

.. code-block:: python

    Out[1]:
                 score
    names
    krippendorff  0.685714
    fleiss        0.666667
    scotts        0.657143
    raw           0.833333
    mace          0.426531
    cohen         0.666667

It was pretty easy to get all the scores, right? What if we do not have a pandas dataframe? what if we want to directly get
the latex table to put into the paper? worry not, my friend: it's easier done than said!

.. code-block:: python

    from quica.measures.irr import *
    from quica.dataset.dataset import IRRDataset
    from quica.quica import Quica

    coder_1 = [0, 1, 0, 1, 0, 1]
    coder_3 = [0, 1, 0, 1, 0, 0]

    disagreeing_coders = [coder_1, coder_3]
    disagreeing_dataset = IRRDataset(disagreeing_coders)

    quica = Quica(disagreeing_dataset)

    print(quica.get_results())
    print(quica.get_latex())

you should get this in output, note that the latex table requires the booktabs package:

.. code-block:: python


    Out[1]:
                 score
    names
    krippendorff  0.685714
    fleiss        0.666667
    scotts        0.657143
    raw           0.833333
    mace          0.426531
    cohen         0.666667

    Out[2]:

    \begin{tabular}{lr}
    \toprule
    {} &     score \\
    names        &           \\
    \midrule
    krippendorff &  0.685714 \\
    fleiss       &  0.666667 \\
    scotts       &  0.657143 \\
    raw          &  0.833333 \\
    mace         &  0.426531 \\
    cohen        &  0.666667 \\
    \bottomrule
    \end{tabular}

Features
--------

.. code-block:: python

    from quica.measures.irr import *
    from quica.dataset.dataset import IRRDataset
    from quica.quica import Quica

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
    assert kri.compute_irr(agreeing_dataset) == 1
    assert cohen.compute_irr(disagreeing_dataset) < 1
    assert cohen.compute_irr(disagreeing_dataset) < 1

Supported Algorithms
--------------------

+ **MACE** (Multi-Annotator Competence Estimation)
     + Hovy, D., Berg-Kirkpatrick, T., Vaswani, A., & Hovy, E. (2013, June). Learning whom to trust with MACE. In Proceedings of the 2013 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (pp. 1120-1130).

     + We define the inter coder agreeement as the average competence of the users.
+ Krippendorff's Alpha
+ Cohens' K
+ Fleiss' K
+ Scotts' PI
+ Raw Agreement: Standard Accuracy

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template. Thanks to Pietro Lesci and Dirk Hovy
for their implementation of MACE.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
