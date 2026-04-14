const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('proviewDesktop', {
  isDesktop: true,
  locateFile(filePath) {
    return ipcRenderer.invoke('proview:locate-file', filePath)
  },
  openFile(filePath) {
    return ipcRenderer.invoke('proview:open-file', filePath)
  },
})
