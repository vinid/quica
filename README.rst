======================================
Quick Inter Coder Agreement in Python
======================================

quica is a tool to run inter coder agreement pipelines in an easy and effective ways. Multiple measures are run and results are collected in a single table than can be easily exported in Latex.


.. image:: https://img.shields.io/pypi/v/quica.svg
        :target: https://pypi.python.org/pypi/quica

.. image:: https://img.shields.io/travis/vinid/quica.svg
        :target: https://travis-ci.com/vinid/quica

.. image:: https://readthedocs.org/projects/quica/badge/?version=latest
        :target: https://quica.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/vinid/quica/shield.svg
     :target: https://pyup.io/repos/github/vinid/quica/
     :alt: Updates



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

    quica = Quica()
    print(quica.get_results(disagreeing_dataset))
    print(quica.get_latex(disagreeing_dataset))


    Out[4]:
                    score
    names
    krippendorff  0.685714
    fleiss        0.666667
    scotts        0.657143
    cohen         0.666667

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
