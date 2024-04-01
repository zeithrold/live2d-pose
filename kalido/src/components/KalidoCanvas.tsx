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
      !store.running ||
      !store.ready
    ) {
      return
    }
    const canvas = canvasRef.current
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
    const { model, pixiApp } = createLive2D(store.live2dModelUrl, canvas)
    const callback = createWsCallback(model)
    listenToMediaPipe(store.wsUrl, callback, (_) => {
      pixiApp.stop()
    })
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
