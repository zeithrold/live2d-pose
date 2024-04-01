import { makeAutoObservable } from 'mobx'
import { type Application } from 'pixi.js'

class Store {
  wsUrl: string | null = null
  live2dModelUrl: string | null = null
  configModalOpen = false
  running = false
  ws: WebSocket | null = null
  pixiApp: Application | null = null

  constructor () {
    makeAutoObservable(this)
  }

  stopWs (): void {
    if (this.ws !== null) {
      this.ws.close()
      this.ws = null
    }
  }

  setWs (ws: WebSocket): void {
    this.ws = ws
  }

  setPixiApp (pixiApp: Application): void {
    this.pixiApp = pixiApp
  }

  stopPixiApp (): void {
    if (this.pixiApp !== null) {
      this.pixiApp.stop()
      this.pixiApp = null
    }
  }

  setRunning (running: boolean): void {
    this.running = running
  }

  setConfig (config: {
    wsUrl: string | null
    live2dModelUrl: string | null
  }): void {
    this.wsUrl = config.wsUrl
    this.live2dModelUrl = config.live2dModelUrl
  }

  setConfigModalOpen (open: boolean): void {
    this.configModalOpen = open
  }

  get ready (): boolean {
    return (
      this.wsUrl != null &&
      this.live2dModelUrl != null
    )
  }
}

const store = new Store()
export default store
