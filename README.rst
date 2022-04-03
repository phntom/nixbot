======
nixbot
======


.. image:: https://img.shields.io/pypi/v/nixbot.svg
        :target: https://pypi.python.org/pypi/nixbot

.. image:: https://img.shields.io/travis/phntom/nixbot.svg
        :target: https://travis-ci.org/phntom/nixbot

.. image:: https://pyup.io/repos/github/phntom/nixbot/shield.svg
     :target: https://pyup.io/repos/github/phntom/nixbot/
     :alt: Updates

.. image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg



bot framework with implementations for high availability, converstations with buttons, persistent storage and personalization


* Documentation: https://phntom.github.io/nixbot
* Source: https://github.com/phntom/nixbot


Installation
------------

::

    git clone {this repo}
    cd project_directory
    # activate your venv i.e.
    pipenv shell
    pip install -e .[dev]

Usage
---------

Use Pipenv to install new modules so they're tracked correctly in the Pipfile::

    pipenv install new-package

To run the app locally and/or deploy to cloudfoundry::

    nixbot runserver
    nixbot dev deploy
