import {
  type MediaPipeFaceLandmark,
  MediaPipeInitialResponseSchema,
  type ImageSize
} from './types'

/**
 * Parse the message received from the WebSocket server
 *
 * @param message The message received from the WebSocket server
 * @returns A 2D array of MediaPipeFaceLandmark objects, where
 * the first dimension represents the face index and the second
 * dimension represents the landmark index
 */
function parseMessage (message: Float32Array): MediaPipeFaceLandmark[][] {
  // Convert 1 * n array to -1 * 478 * 3(x, y, z) object array
  const faces = message.length / 3 / 478
  const landmarks: MediaPipeFaceLandmark[][] = []
  for (let i = 0; i < faces; i++) {
    const face: MediaPipeFaceLandmark[] = []
    for (let j = 0; j < 478; j++) {
      face.push({
        x: message[i * 478 * 3 + j * 3],
        y: message[i * 478 * 3 + j * 3 + 1],
        z: message[i * 478 * 3 + j * 3 + 2]
      })
    }
    landmarks.push(face)
  }
  return landmarks
}

/**
 * Create a WebSocket connection to the specified URL and listen for messages
 *
 * @param url The WebSocket URL to connect to
 * @param callback The callback function to be called when a message is received
 */
function listenToMediaPipe (
  url: string,
  callback: (imageSize: ImageSize, landmarks: MediaPipeFaceLandmark[][]
  ) => void, onClose: (event: CloseEvent) => void): void {
  const ws = new WebSocket(url)
  ws.addEventListener('open', (_) => {
    console.debug(`[ws] 成功创建 WebSocket 连接: ${url}`)
  })
  let imageSize: ImageSize | null = null
  ws.addEventListener('message', (event) => {
    if (typeof event.data === 'string') {
      const rawResponse = JSON.parse(event.data)
      try {
        const response = MediaPipeInitialResponseSchema
          .validateSync(rawResponse)
        imageSize = response.videoSize
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

    const data: Blob = event.data
    data.arrayBuffer().then((buffer) => {
      const message = new Float32Array(buffer)
      const landmarks = parseMessage(message)
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      callback(imageSize!, landmarks)
    }).catch((error) => {
      console.error(`[ws] 无法解析 WebSocket 数据(返回的数据并不是一个二进制数据。): ${error}`)
    })
  })
  ws.addEventListener('error', (event) => {
    console.error('[ws] WebSocket 连接出现错误.')
    onClose(event as CloseEvent)
  })
  ws.addEventListener('close', onClose)
}

export { listenToMediaPipe }
