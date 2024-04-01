import Button from '@mui/material/Button'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogTitle from '@mui/material/DialogTitle'
import TextField from '@mui/material/TextField'
import { observer } from 'mobx-react'
import React from 'react'
import { store } from '../lib'

function onStart (wsUrl: string, live2dModelUrl: string): void {
  store.setConfig({
    wsUrl,
    live2dModelUrl
  })
}

const ConfigDialog = observer(() => {
  const [wsUrl, setWsUrl] = React.useState('')
  const [live2dModelUrl, setLive2dModelUrl] = React.useState('')
  React.useEffect(() => {
    if (store.live2dModelUrl != null) {
      setLive2dModelUrl(store.live2dModelUrl)
    }
    if (store.wsUrl != null) {
      setWsUrl(store.wsUrl)
    }
  }, [])
  return (
    <Dialog
      open={store.configModalOpen}
      onClose={() => {
        store.setConfigModalOpen(false)
      }}
    >
      <DialogTitle>
        配置链接
      </DialogTitle>
      <DialogContent>
          <TextField
            value={wsUrl}
            label='WebSocket URL'
            placeholder='ws://localhost:8765/browser?uuid=...'
            onChange={(e) => {
              setWsUrl(e.target.value)
            }}
            variant='standard'
            fullWidth
          />
          <TextField
            value={live2dModelUrl}
            label='live2d 模型 URL'
            placeholder='输入模型 URL，通常以.model3.json结尾'
            onChange={(e) => {
              setLive2dModelUrl(e.target.value)
            }}
            variant='standard'
            fullWidth
          />
      </DialogContent>
      <DialogActions>
        <Button
          variant='contained'
          onClick={() => {
            onStart(wsUrl, live2dModelUrl)
            store.setConfigModalOpen(false)
          }}
        >
          启动
        </Button>
      </DialogActions>
    </Dialog>
  )
})

export default ConfigDialog
