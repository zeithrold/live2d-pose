import { object, number, string, type InferType } from 'yup'

const MediaPipeInitialResponseSchema = object({
  status: string().required(),
  videoSize: object({
    width: number().required(),
    height: number().required()
  }).required()
}).required()

type MediaPipeInitialResponse = InferType<typeof MediaPipeInitialResponseSchema>

interface MediaPipeFaceLandmark {
  x: number
  y: number
  z: number
}

interface ImageSize {
  width: number
  height: number
}

export {
  MediaPipeInitialResponseSchema,
  type MediaPipeInitialResponse,
  type MediaPipeFaceLandmark,
  type ImageSize
}
