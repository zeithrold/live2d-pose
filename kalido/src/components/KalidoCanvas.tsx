import Typography from '@mui/material/Typography'
import { observer } from 'mobx-react'
import React from 'react'
import { listenToMediaPipe } from '../lib'
import { createLive2D, createWsCallback } from '../lib/live2d'
import store from '../lib/store'

const KalidoCanvas = observer(() => {
  React.useEffect(() => {
    if (
      canvasRef.current == null ||
      store.live2dModelUrl == null ||
      store.wsUrl == null ||
      !store.ready
    ) {
      return
    }
    if (!store.running) {
      store.stopWs()
      store.stopPixiApp()
      return
    }
    const canvas = canvasRef.current
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
    const { model, pixiApp } = createLive2D(store.live2dModelUrl, canvas)
    const callback = createWsCallback(model)
    const ws = listenToMediaPipe(
      store.wsUrl,
      callback,
      (_) => {
        store.setRunning(true)
      },
      (_) => {
        store.setRunning(false)
        pixiApp.stop()
      })
    store.setWs(ws)
  }, [store.ready, store.running])
  if (store.live2dModelUrl == null || store.wsUrl == null) {
    return <Typography variant='h3'>
      请先配置 wsUrl 和 live2dModelUrl
    </Typography>
  }
  const canvasRef = React.useRef<HTMLCanvasElement>(null)
  return (
    <canvas ref={canvasRef}></canvas>
  )
})

export default KalidoCanvas
