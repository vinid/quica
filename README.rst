======================================
Quick Inter Coder Agreement in Python
======================================

Quica (Quick Inter Coder Agreement in Python) is a tool to run inter coder agreement pipelines in an easy and effective ways.
Multiple measures are run and results are collected in a single table than can be easily exported in Latex.
quica supports binary or multiple coders.

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

Get Quick Agreement
-------------------

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

you should get these in output:

.. code-block:: python


    Out[1]:
                    score
    names
    krippendorff  0.685714
    fleiss        0.666667
    scotts        0.657143
    cohen         0.666667

    Out[2]:

    \begin{tabular}{lr}
    \toprule
    {} &     score \\
    names       &           \\
    \midrule
    krippendorf &  0.685714 \\
    fleiss      &  0.666667 \\
    scotts      &  0.657143 \\
    cohen       &  0.666667 \\
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
    assert cohen.compute_irr(agreeing_dataset) == 1
    assert cohen.compute_irr(disagreeing_dataset) < 1
    assert cohen.compute_irr(disagreeing_dataset) < 1

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
