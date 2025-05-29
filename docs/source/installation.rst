Installation
============

Requirements
-----------

- Python 3.7 or later
- ``aiohttp`` 3.8.0 or later

Installing with pip
------------------

The recommended way to install the Reality Defender SDK is via pip:

.. code-block:: bash

   pip install realitydefender

Installing from source
--------------------

You can also install the SDK directly from the source code:

.. code-block:: bash

   git clone https://github.com/Reality-Defender/eng-sdk.git
   cd eng-sdk/python
   pip install -e .

Development installation
----------------------

For development, you can install the SDK with development dependencies:

.. code-block:: bash

   git clone https://github.com/Reality-Defender/eng-sdk.git
   cd eng-sdk/python
   pip install -e ".[dev]"

This will install additional packages needed for development, testing, and documentation: 