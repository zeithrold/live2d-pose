import { type TFace, Vector, Face } from 'kalidokit'
import { Live2DModel } from 'pixi-live2d-display'
import * as PIXI from 'pixi.js'
import { type ImageSize, type MediaPipeFaceLandmark } from './types'

declare global {
  interface Window {
    PIXI: typeof PIXI
  }
}

window.PIXI = PIXI

function rigFace (
  model: Live2DModel,
  result: TFace | undefined,
  lerpAmount: number
): void {
  if (result === undefined) return
  const motionManager = model.internalModel.motionManager
  const coreModel: any = model.internalModel.coreModel
  function setParam (value: any, paramName: string): void {
    coreModel.setParameterValueById(
      paramName,
      Vector.lerp(value, coreModel.getParameterValueById(paramName), lerpAmount)
    )
  }
  // Code from KalidoKit Demo code
  motionManager.update = function (model: object, now: number): boolean {
    setParam(result.pupil.x, 'ParamEyeBallX')
    setParam(result.pupil.y, 'ParamEyeBallY')
    setParam(result.head.degrees.y, 'ParamAngleX')
    setParam(result.head.degrees.x, 'ParamAngleY')
    setParam(result.head.degrees.z, 'ParamAngleZ')
    const dampener = 0.3
    setParam(result.head.degrees.y * dampener, 'ParamBodyAngleX')
    setParam(result.head.degrees.x * dampener, 'ParamBodyAngleY')
    setParam(result.head.degrees.z * dampener, 'ParamBodyAngleZ')
    const stabilizedEyes = Face.stabilizeBlink({
      l: Vector.lerp(
        result.eye.l,
        coreModel.getParameterValueById('ParamEyeLOpen'),
        0.7
      ),
      r: Vector.lerp(
        result.eye.r,
        coreModel.getParameterValueById('ParamEyeROpen'),
        0.7)
    }, result.head.y)
    coreModel.setParameterValueById('ParamEyeLOpen', stabilizedEyes.l)
    coreModel.setParameterValueById('ParamEyeROpen', stabilizedEyes.r)
    setParam(result.mouth.y, 'ParamMouthOpenY')
    setParam(result.mouth.x, 'ParamMouthForm')
    return true
  }
}

function createWsCallback (model: Live2DModel, lerpAmount = 0.7):
(imageSize: ImageSize, landmarks: MediaPipeFaceLandmark[][]) => void {
  return function (
    imageSize: ImageSize,
    landmarks: MediaPipeFaceLandmark[][]
  ): void {
    const face = landmarks[0]
    const result = Face.solve(face, { runtime: 'mediapipe', imageSize })
    rigFace(model, result, lerpAmount)
  }
}

function createLive2D (modelUrl: string, canvasElement: HTMLCanvasElement): {
  model: Live2DModel
  pixiApp: PIXI.Application
} {
  const pixiApp = new PIXI.Application({
    view: canvasElement,
    autoStart: true,
    // transparent: true,
    backgroundAlpha: 0,
    resizeTo: window
  })
  const model = Live2DModel.fromSync(modelUrl)
  // TODO: Add optimization to Live2DModel
  pixiApp.stage.addChild(model as unknown as PIXI.Container)
  return { model, pixiApp }
}

export { rigFace, createWsCallback, createLive2D }
