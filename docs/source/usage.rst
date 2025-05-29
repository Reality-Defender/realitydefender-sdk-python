Usage
=====

The SDK offers both asynchronous and synchronous APIs to fit different programming styles and requirements.

Synchronous API (Simple)
-----------------

If you prefer a simpler approach without having to deal with asyncio, you can use the synchronous API:

.. code-block:: python

   from realitydefender import RealityDefender

   # Initialize the SDK with your API key
   client = RealityDefender({
       'api_key': 'your-api-key'
   })

   # The simplest way - one step file detection
   result = client.detect_file('/path/to/your/image.jpg')
   print(f"Status: {result['status']}, Score: {result['score']}")

   # Or for more control, you can use the separate steps:
   upload_result = client.upload_sync({
       'file_path': '/path/to/your/image.jpg'
   })
   
   print(f"Request ID: {upload_result['request_id']}")
   
   # Get detection results
   result = client.get_result_sync(upload_result['request_id'])
   print(f"Status: {result['status']}, Score: {result['score']}")

Asynchronous API (More Efficient)
----------

The SDK uses asyncio for async/await functionality, which ensures efficient API interactions:

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
       
       print(f"Request ID: {upload_result['request_id']}")
       
       # Get detection results
       result = await client.get_result(upload_result['request_id'])
       print(f"Status: {result['status']}, Score: {result['score']}")
       
       # Print model-specific results
       for model in result['models']:
           print(f"Model: {model['name']}, Status: {model['status']}, Score: {model['score']}")

   # Run the async function
   asyncio.run(detect_deepfake())

Event-based Usage (Async)
---------------

You can use the event emitter pattern for handling results asynchronously:

.. code-block:: python

   import asyncio
   from realitydefender import RealityDefender

   async def detect_with_events():
       client = RealityDefender({
           'api_key': 'your-api-key'
       })
       
       # Set up event handlers
       client.on('result', lambda result: print(f"Got result: {result['status']}"))
       client.on('error', lambda err: print(f"Error: {err}"))
       
       # Upload a file
       upload_result = await client.upload({
           'file_path': '/path/to/your/video.mp4'
       })
       
       # Start polling for results
       polling_task = client.poll_for_results(
           upload_result['request_id'],
           polling_interval=3000,  # 3 seconds
           timeout=120000         # 2 minutes
       )
       
       # Wait for the polling to complete
       await polling_task

   # Run the async function
   asyncio.run(detect_with_events())

Callback-based Usage (Sync)
-----------------

You can also use a synchronous callback approach:

.. code-block:: python

   from realitydefender import RealityDefender

   # Initialize the SDK
   client = RealityDefender({
       'api_key': 'your-api-key'
   })

   # Define callback functions
   def on_result(result):
       print(f"Got result: {result['status']}")
       print(f"Score: {result['score']}")

   def on_error(error):
       print(f"Error: {error.message}")
       print(f"Code: {error.code}")

   # Upload a file
   upload_result = client.upload_sync({
       'file_path': '/path/to/your/video.mp4'
   })

   # Start polling with callbacks
   client.poll_for_results_sync(
       upload_result['request_id'],
       polling_interval=3000,  # 3 seconds
       timeout=120000,        # 2 minutes
       on_result=on_result,
       on_error=on_error
   )

Direct Function Usage
------------------

For more control, you can use the direct functions:

.. code-block:: python

   import asyncio
   from realitydefender import (
       create_http_client, 
       upload_file, 
       get_detection_result
   )

   async def manual_detection():
       # Create HTTP client
       client = create_http_client({
           'api_key': 'your-api-key'
       })
       
       # Upload a file
       upload_result = await upload_file(client, {
           'file_path': '/path/to/your/audio.mp3'
       })
       
       # Get the result with custom polling options
       result = await get_detection_result(
           client, 
           upload_result['request_id'],
           {
               'max_attempts': 20,
               'polling_interval': 5000  # 5 seconds
           }
       )
       
       print(f"Detection result: {result}")
       
       # Remember to close the client when done
       await client.close()

   # Run the async function
   asyncio.run(manual_detection())

Error Handling
------------

The SDK uses custom exceptions for error handling:

.. code-block:: python

   import asyncio
   from realitydefender import RealityDefender, RealityDefenderError

   async def handle_errors():
       try:
           client = RealityDefender({
               'api_key': 'invalid-key'
           })
           
           await client.upload({
               'file_path': '/path/to/file.jpg'
           })
       except RealityDefenderError as e:
           print(f"Error code: {e.code}")
           print(f"Error message: {e.message}")
           
           if e.code == 'unauthorized':
               print("Please check your API key")
           elif e.code == 'invalid_file':
               print("The file could not be found or read")

   # Run the async function
   asyncio.run(handle_errors()) 