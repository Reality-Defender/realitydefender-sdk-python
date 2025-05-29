Reality Defender SDK
=====================

.. image:: https://codecov.io/gh/Reality-Defender/eng-sdk/graph/badge.svg?token=P98RNVB21M
   :target: https://codecov.io/gh/Reality-Defender/eng-sdk

The Reality Defender Python SDK provides tools for detecting deepfakes and manipulated media through the Reality Defender API.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   examples

Installation
-----------

.. code-block:: bash

   pip install realitydefender

Requirements
-----------

- Python 3.7 or later
- ``aiohttp`` 3.8.0 or later

Quick Start
----------

.. code-block:: python

   import asyncio
   from realitydefender import RealityDefender

   async def detect_deepfake():
       # Initialize the SDK with your API key
       client = RealityDefender({
           'api_key': 'your-api-key'
       })

       # Upload a file for analysis
       upload_result = await client.upload({
           'file_path': '/path/to/your/image.jpg'
       })
       
       # Get detection results
       result = await client.get_result(upload_result['request_id'])
       print(f"Status: {result['status']}, Score: {result['score']}")

   asyncio.run(detect_deepfake())

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 