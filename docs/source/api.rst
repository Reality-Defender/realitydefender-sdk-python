API Reference
============

RealityDefender Class
------------------

.. autoclass:: realitydefender.RealityDefender
   :members:
   :special-members: __init__
   
Asynchronous Methods
^^^^^^^^^^^^^^^^^^^

- ``__init__(config: RealityDefenderConfig)`` - Initialize the SDK
- ``async upload(options: UploadOptions) -> UploadResult`` - Upload a file for analysis
- ``async get_result(request_id: str, options: GetResultOptions = None) -> DetectionResult`` - Get detection results
- ``poll_for_results(request_id: str, polling_interval: int = None, timeout: int = None) -> asyncio.Task`` - Start polling for results

Synchronous Methods
^^^^^^^^^^^^^^^^^

- ``upload_sync(options: UploadOptions) -> UploadResult`` - Upload a file for analysis (synchronous version)
- ``get_result_sync(request_id: str, options: GetResultOptions = None) -> DetectionResult`` - Get detection results (synchronous version)
- ``detect_file(file_path: str) -> DetectionResult`` - One-step file detection (upload and get results)
- ``poll_for_results_sync(request_id: str, polling_interval: int = None, timeout: int = None, on_result: Callable = None, on_error: Callable = None)`` - Synchronous polling with callbacks

Types
-----

.. automodule:: realitydefender.types
   :members:

Error Handling
------------

.. autoclass:: realitydefender.errors.RealityDefenderError
   :members:
   :special-members: __init__

.. autodata:: realitydefender.errors.ErrorCode
   :annotation:

Client
------

.. autofunction:: realitydefender.client.create_http_client

.. autoclass:: realitydefender.client.http_client.HttpClient
   :members:
   :special-members: __init__

Detection Functions
----------------

.. autofunction:: realitydefender.detection.upload.upload_file

.. autofunction:: realitydefender.detection.results.get_detection_result

Utilities
--------

.. autofunction:: realitydefender.utils.async_utils.sleep

.. autofunction:: realitydefender.utils.file_utils.get_file_info

Constants
--------

.. automodule:: realitydefender.core.constants
   :members:

Event Emitter
-----------

.. autoclass:: realitydefender.core.events.EventEmitter
   :members:
   :special-members: __init__ 