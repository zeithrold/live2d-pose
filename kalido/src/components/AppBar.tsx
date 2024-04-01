import Done from '@mui/icons-material/Done'
import Warning from '@mui/icons-material/Warning'
import AppBar from '@mui/material/AppBar'
import Button from '@mui/material/Button'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import React from 'react'

export default function AppBarComponent (): React.JSX.Element {
  const [connected, setConnected] = React.useState(false)
  return (
    <AppBar>
      <Toolbar variant='dense'>
        <Typography
          sx={{
            flexGrow: 1
          }}
          variant="h6"
        >live2d-pose</Typography>
        {
          connected
            ? <Button
              variant='contained'
              color='success'
              startIcon={<Done />}
              size='small'
              onClick={() => {
                setConnected(false)
              }}>已连接至 ws://127.0.0.1</Button>
            : <Button
              size='small'
              variant='contained'
              color='error'
              startIcon={<Warning />}
              onClick={() => {
                setConnected(true)
              }}>未连接</Button>
        }
      </Toolbar>
    </AppBar>
  )
}
