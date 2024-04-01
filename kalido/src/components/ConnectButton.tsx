import Done from '@mui/icons-material/Done'
import Warning from '@mui/icons-material/Warning'
import Button from '@mui/material/Button'
import CircularProgress from '@mui/material/CircularProgress'
import { observer } from 'mobx-react'
import React from 'react'
import { store } from '../lib'
import ConfigDialog from './ConfigDialog'

function onDisconnectClick (): void {
  store.setConfig({ wsUrl: null, live2dModelUrl: null })
  store.setRunning(!store.running)
}

const ConnectButton = observer(() => {
  const color = store.ready ? (store.running ? 'success' : 'warning') : 'error'
  const StartIcon =
    store.ready
      ? store.running
        ? <Done />
        : <CircularProgress />
      : <Warning />
  const text = (
    store.ready
      ? (store.running ? `已连接至${store.wsUrl}` : `正在连接至${store.wsUrl}`)
      : '请先连接'
  )
  const disabled = store.ready && !store.running
  return (
    <div>
      <Button
        color={color}
        startIcon={StartIcon}
        variant='contained'
        disabled={disabled}
        onClick={() => {
          if (store.running) {
            onDisconnectClick()
          } else {
            store.setConfigModalOpen(true)
          }
        }}
      >
        {text}
      </Button>
      <ConfigDialog />
    </div>
  )
})

export default ConnectButton
