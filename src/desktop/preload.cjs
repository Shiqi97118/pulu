const {contextBridge, ipcRenderer} = require('electron');
contextBridge.exposeInMainWorld('pulu', Object.freeze({
  command: (action) => ipcRenderer.invoke('command', action),
  hit: (value) => ipcRenderer.send('hit', value),
  drag: (value) => ipcRenderer.send('drag', value),
  ready: () => ipcRenderer.send('renderer-ready'),
  onState: (fn) => { const cb=(_e,v)=>fn(v); ipcRenderer.on('state',cb); return ()=>ipcRenderer.removeListener('state',cb); },
  onPointer: (fn) => { const cb=(_e,v)=>fn(v); ipcRenderer.on('pointer',cb); return ()=>ipcRenderer.removeListener('pointer',cb); }
}));
