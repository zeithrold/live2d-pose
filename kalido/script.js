const {
  Application,
  live2d: { Live2DModel },
} = PIXI;

// Kalidokit provides a simple easing function
// (linear interpolation) used for animation smoothness
// you can use a more advanced easing function if you want
const {
  Face,
  Vector: { lerp },
  Utils: { clamp },
} = Kalidokit;

function parseMessage(message) {
  // Convert 1 * n array to -1 * 478 * 3(x, y, z) object array
  const faces = message.length / 3 / 478;
  const landmarks = [];
  for (let i = 0; i < faces; i++) {
    const face = [];
    for (let j = 0; j < 478; j++) {
      face.push({
        x: message[i * 478 * 3 + j * 3],
        y: message[i * 478 * 3 + j * 3 + 1],
        z: message[i * 478 * 3 + j * 3 + 2],
      });
    }
    landmarks.push(face);
  }
  return landmarks;
}

const searchParams = new URLSearchParams(window.location.search)
const wsUrl = decodeURIComponent(searchParams.get('ws'))
const modelUrl = decodeURIComponent(searchParams.get('model'))


let currentModel, facemesh;

(async function main() {
  // create pixi application
  const app = new PIXI.Application({
    view: document.getElementById("live2d"),
    autoStart: true,
    transparent: true,
    backgroundAlpha: 0,
    resizeTo: window,
  });

  // load live2d model
  currentModel = await Live2DModel.from(modelUrl, { autoInteract: false });
  currentModel.scale.set(0.1);
  currentModel.interactive = true;
  currentModel.anchor.set(0.5, 0.5);
  currentModel.position.set(window.innerWidth * 0.5, window.innerHeight * 0.8);

  // Add events to drag model
  currentModel.on("pointerdown", (e) => {
    currentModel.offsetX = e.data.global.x - currentModel.position.x;
    currentModel.offsetY = e.data.global.y - currentModel.position.y;
    currentModel.dragging = true;
  });
  currentModel.on("pointerup", (e) => {
    currentModel.dragging = false;
  });
  currentModel.on("pointermove", (e) => {
    if (currentModel.dragging) {
      currentModel.position.set(
        e.data.global.x - currentModel.offsetX,
        e.data.global.y - currentModel.offsetY
      );
    }
  });

  // Add mousewheel events to scale model
  document.querySelector("#live2d").addEventListener("wheel", (e) => {
    e.preventDefault();
    currentModel.scale.set(
      clamp(currentModel.scale.x + event.deltaY * -0.001, -0.5, 10)
    );
  });

  // add live2d model to stage
  app.stage.addChild(currentModel);

  const ws = new WebSocket(wsUrl);
  let imageSize = null
  ws.addEventListener('message', (event) => {
    if (typeof event.data === 'string') {
      const rawResponse = JSON.parse(event.data)
      try {
        console.log('[ws] 收到 MediaPipeInitialResponse 数据.')
        console.log(rawResponse)
        const response = rawResponse
        imageSize = response.imageSize
      } catch (error) {
        console.error('[ws] 无法解析 WebSocket 数据(返回的数据并不是一个 ' +
          `MediaPipeInitialResponse 对象。): ${error}`)
      }
      return
    }
    if (imageSize == null) {
      console.error('[ws] 无法解析 WebSocket 数据(尚未接收到视频大小信息。)')
      return
    }

    const data = event.data
    data.arrayBuffer().then((buffer) => {
      const message = new Float32Array(buffer)
      const landmarks = parseMessage(message)
      return landmarks
    }).catch((error) => {
      console.error(`[ws] 无法解析 WebSocket 数据(返回的数据并不是一个二进制数据。): ${error}`)
    }).then((landmarks) => {
      if (landmarks == null) {
        console.error('[ws] 无法解析 WebSocket 数据(返回的数据并不是一个 ' +
          'MediaPipeFaceLandmark 对象数组。)')
        return
      }
      animateLive2DModel(landmarks[0])
    }).catch((error) => {
      console.error(`[ws] 回调函数出现错误: ${error}`)
    })
  });
})();

const onResults = (results) => {
  animateLive2DModel(results.multiFaceLandmarks[0]);
};

const animateLive2DModel = (points) => {
  if (!currentModel || !points) return;

  let riggedFace;

  if (points) {
    // use kalidokit face solver
    riggedFace = Face.solve(points, {
      runtime: "mediapipe",
      imageSize
    });
    rigFace(riggedFace, 0.5);
  }
};

// update live2d model internal state
const rigFace = (result, lerpAmount = 0.7) => {
  if (!currentModel || !result) return;
  const updateFn = currentModel.internalModel.motionManager.update;
  const coreModel = currentModel.internalModel.coreModel;

  currentModel.internalModel.motionManager.update = (...args) => {
    // disable default blink animation
    currentModel.internalModel.eyeBlink = undefined;

    coreModel.setParameterValueById(
      "ParamEyeBallX",
      lerp(
        result.pupil.x,
        coreModel.getParameterValueById("ParamEyeBallX"),
        lerpAmount
      )
    );
    coreModel.setParameterValueById(
      "ParamEyeBallY",
      lerp(
        result.pupil.y,
        coreModel.getParameterValueById("ParamEyeBallY"),
        lerpAmount
      )
    );

    // X and Y axis rotations are swapped for Live2D parameters
    // because it is a 2D system and KalidoKit is a 3D system
    coreModel.setParameterValueById(
      "ParamAngleX",
      lerp(
        result.head.degrees.y,
        coreModel.getParameterValueById("ParamAngleX"),
        lerpAmount
      )
    );
    coreModel.setParameterValueById(
      "ParamAngleY",
      lerp(
        result.head.degrees.x,
        coreModel.getParameterValueById("ParamAngleY"),
        lerpAmount
      )
    );
    coreModel.setParameterValueById(
      "ParamAngleZ",
      lerp(
        result.head.degrees.z,
        coreModel.getParameterValueById("ParamAngleZ"),
        lerpAmount
      )
    );

    // update body params for models without head/body param sync
    const dampener = 0.3;
    coreModel.setParameterValueById(
      "ParamBodyAngleX",
      lerp(
        result.head.degrees.y * dampener,
        coreModel.getParameterValueById("ParamBodyAngleX"),
        lerpAmount
      )
    );
    coreModel.setParameterValueById(
      "ParamBodyAngleY",
      lerp(
        result.head.degrees.x * dampener,
        coreModel.getParameterValueById("ParamBodyAngleY"),
        lerpAmount
      )
    );
    coreModel.setParameterValueById(
      "ParamBodyAngleZ",
      lerp(
        result.head.degrees.z * dampener,
        coreModel.getParameterValueById("ParamBodyAngleZ"),
        lerpAmount
      )
    );

    // Simple example without winking.
    // Interpolate based on old blendshape, then stabilize blink with `Kalidokit` helper function.
    let stabilizedEyes = Kalidokit.Face.stabilizeBlink(
      {
        l: lerp(
          result.eye.l,
          coreModel.getParameterValueById("ParamEyeLOpen"),
          0.7
        ),
        r: lerp(
          result.eye.r,
          coreModel.getParameterValueById("ParamEyeROpen"),
          0.7
        ),
      },
      result.head.y
    );
    // eye blink
    coreModel.setParameterValueById("ParamEyeLOpen", stabilizedEyes.l);
    coreModel.setParameterValueById("ParamEyeROpen", stabilizedEyes.r);

    // mouth
    coreModel.setParameterValueById(
      "ParamMouthOpenY",
      lerp(
        result.mouth.y,
        coreModel.getParameterValueById("ParamMouthOpenY"),
        0.3
      )
    );
    // Adding 0.3 to ParamMouthForm to make default more of a "smile"
    coreModel.setParameterValueById(
      "ParamMouthForm",
      0.3 +
      lerp(
        result.mouth.x,
        coreModel.getParameterValueById("ParamMouthForm"),
        0.3
      )
    );
  };
};
