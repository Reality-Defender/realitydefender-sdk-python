Examples
========

Basic Usage Example
-----------------

The following example demonstrates basic usage of the SDK to analyze an image:

.. literalinclude:: ../../examples/basic_usage.py
   :language: python
   :linenos:
   :caption: examples/basic_usage.py

Synchronous Usage Example
---------------------

The following example shows how to use the SDK without asyncio:

.. literalinclude:: ../../examples/sync_usage.py
   :language: python
   :linenos:
   :caption: examples/sync_usage.py

Video Detection Example
---------------------

The following example shows how to use the SDK to analyze a video file:

.. literalinclude:: ../../examples/video_detection.py
   :language: python
   :linenos:
   :caption: examples/video_detection.py

Batch Processing Example
---------------------

The following example demonstrates how to process multiple files concurrently:

.. literalinclude:: ../../examples/batch_processing.py
   :language: python
   :linenos:
   :caption: examples/batch_processing.py

Running the Examples
------------------

To run these examples, make sure you have the SDK installed and an API key:

.. code-block:: bash

   cd examples
   
   # Set your API key as an environment variable
   export REALITY_DEFENDER_API_KEY='your-api-key'
   
   # Run the basic example
   python basic_usage.py
   
   # Run the event-based example
   python basic_usage.py --events
   
   # Run the synchronous example
   python sync_usage.py
   
   # Run the one-step detection example
   python sync_usage.py --one-step
   
   # Run the synchronous callbacks example
   python sync_usage.py --callbacks
   
   # Run the video detection example (requires test_video.mp4)
   python video_detection.py
   
   # Run the batch processing example (requires images in examples/images/)
   python batch_processing.py

Sample Files
----------

For testing purposes, you'll need to provide your own media files:

1. For the basic and synchronous examples, add a file named ``test_image.jpg`` to the examples directory
2. For the video detection example, add a file named ``test_video.mp4`` to the examples directory
3. For batch processing, add image files to the ``examples/images/`` directory 