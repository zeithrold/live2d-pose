import AppBar from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import React from 'react'
import ConnectButton from './ConnectButton'

export default function AppBarComponent (): React.JSX.Element {
  return (
    <AppBar>
      <Toolbar variant='dense'>
        <Typography
          sx={{
            flexGrow: 1
          }}
          variant="h6"
        >live2d-pose</Typography>
        <ConnectButton />
      </Toolbar>
    </AppBar>
  )
}
