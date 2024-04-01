# live2d-pose
A Live2D pose capturer built on the top of JetBot, with MediaPipe and KalidoKit.

The project consists of two components: **image processor backend with MediaPipe**, and **Live2D model viewer with Kalidokit**, two components, together with JetBot, are connected with WebSockets.

## Technical Details

The main concept of `live2d-pose` is to connect JetBot and browser with WebSocket, backend landmarks image from JetBot, then send result to browser.

### Backend: MediaPipe Face Landmarker
Backend is based on [MediaPipe](https://developers.google.com/mediapipe) Face Landmarker by Google. The following code shows basic usage of MediaPipe Face Landmarker:

```python
option = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=self.callback,
)
with FaceLandmarker.create_from_options(option) as landmarker:
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image) # numpy.ndarray
    landmarker.detect_async(mp_image, timestamp_ms)
```

### Frontend: KalidoKit

[KalidoKit](https://github.com/yeemachine/kalidokit) is a About
Blendshape and kinematics calculator. Originally KalidoKit accepts landmarks directly from MediaPipe on browser, but we seperate it to combine Live2D model bind and face tracking on JetBot.

Using KalidoKit is also simple. You can quick start once you get MediaPipe landmark result from WebSocket:

```javascript
const riggedFace = Face.solve(points, {
  runtime: "mediapipe",
  imageSize: {
    width: 640,
    height: 480
  }
});
// Control Live2D model...
```

## Usage

You need to store Live2D model (`.model3.json`) on a browser accessible place.

1. Clone git repository: `git clone https://github.com/zeithrold/live2d-pose`
2. Create virtual environment with `python -m venv venv` and install dependencies: `pip install -r requirements.txt`
   > Note: Mediapipe don't provide wheels for aarch64 architechture
3. Download MediaPipe model from [Direct Link](https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task), save it to `mp/models/`
4. Locate to `mp` directory, Run `python app.py [...args]`
5. Run custom camera capturing script connecting to backend machine. (We provided an example script for local machine using webcam.)
6. Open link displayed on backend, and enjoy.

Args for `app.py` is as follows:
```
--ip IP, -i IP        server ip to bind
--port PORT, -p PORT  server port to bind
--model MODEL         url where stores Live2D model (.model3.json)
--frontend FRONTEND   url where serves KalidoKit frontend
```

If you pretend to serve KalidoKit fronend on local machine(e.g. SimpleHTTPServer), **DON'T FORGET** to set CORS properly.

For Live2D model url, a possible example is `http://example-s3.com/live2d/zeithrold.model3.json`.


Due to latency issue, we **HIGHLY RECOMMEND** connect JetBot and backend in a local network.

## WebSocket Protocol Definitions
1. When image capturer connects backend first, backend will create a MediaPipe thread. When it completes, backend will send a JSON message: `{"type": "initialized"}`.
2. Then it's time for image capturer to send image size (width, height) in JSON format like `{"imageSize": {"width": 640, "height": 480}}`, when accepted, backend will send a JSON message: `{"type": "ok"}`
3. The backend will print a URL for web browser(or OBS), when page is prepared, let image capturer send binary OpenCV-Encoded (supports compression) like `cv2.imencode(".jpg", img, params)[1].tobytes()` image data, then all process will begin.

Note that the frequency should not too fast, otherwise will cause no time left for backend to send Keep-Alive ping, resulting connection crash.

