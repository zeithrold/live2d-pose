import { makeAutoObservable } from 'mobx'

class Store {
  wsUrl: string | null = null
  live2dModelUrl: string | null = null
  configModalOpen = false
  running = false
  constructor () {
    makeAutoObservable(this)
  }

  setRunning (running: boolean): void {
    this.running = running
  }

  setConfig (config: { wsUrl: string, live2dModelUrl: string }): void {
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
