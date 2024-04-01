import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Modal from '@mui/material/Modal'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import { observer } from 'mobx-react'
import React from 'react'
import { store } from '../lib'

function onStart (wsUrl: string, live2dModelUrl: string): void {
  store.setConfig({
    wsUrl,
    live2dModelUrl
  })
  store.setRunning(true)
}

const ConfigModal = observer(() => {
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
    <Modal
      open={store.configModalOpen}
    >
      <Box>
        <Typography variant="h6" component="h2">
          Text in a modal
        </Typography>
        <Box sx={{
          mt: 2
        }}>
          <TextField
            variant='outlined'
            value={wsUrl}
            placeholder='输入WebSocket URL'
            onChange={(e) => {
              setWsUrl(e.target.value)
            }}
          />
          <TextField
            variant='outlined'
            value={live2dModelUrl}
            placeholder='输入模型 URL'
            onChange={(e) => {
              setLive2dModelUrl(e.target.value)
            }}
          />
        </Box>
        <Box sx={{
          mt: 2
        }}>
          <Button
            variant='contained'
            onClick={() => {
              store.setConfigModalOpen(false)
              onStart(wsUrl, live2dModelUrl)
            }}
          >启动</Button>
        </Box>
      </Box>
    </Modal>
  )
})

export default ConfigModal
