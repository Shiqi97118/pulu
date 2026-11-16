const {app,BrowserWindow,ipcMain,Menu,Tray,nativeImage,screen,powerMonitor} = require('electron');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
let pet, panel, tray, timer, dragging=false, dragStart=null, pointer=null, quitting=false;
const state={paused:false,hidden:false,reduced:false,locked:false};
const smoke=process.argv.includes('--smoke');
if(smoke) app.setPath('userData',path.join(app.getPath('temp'),'pulu-smoke-user-data'));
const html=path.resolve(__dirname,'../../dist/index.html');
const fileURL=pathToFileURL(html).href;
function trusted(e) {return [pet,panel].some(w=>w&&!w.isDestroyed()&&e.sender===w.webContents)&&e.senderFrame&&e.senderFrame===e.sender.mainFrame&&e.senderFrame.url.split('?')[0]===fileURL;}
function sendState(){ for(const w of [pet,panel]) if(w&&!w.isDestroyed())w.webContents.send('state',state); }
function protect(w){
 w.webContents.setWindowOpenHandler(()=>({action:'deny'}));
 w.webContents.on('will-navigate',e=>e.preventDefault());
 w.webContents.session.setPermissionRequestHandler((_wc,_permission,cb)=>cb(false));
 w.webContents.session.webRequest.onBeforeRequest((details,cb)=>cb({cancel:!details.url.startsWith('file://')}));
}
function place(x,y){const area=screen.getDisplayNearestPoint({x:Math.round(x+150),y:Math.round(y+130)}).workArea;pet.setPosition(Math.round(Math.min(Math.max(x,area.x),area.x+Math.max(0,area.width-300))),Math.round(Math.min(Math.max(y,area.y),area.y+Math.max(0,area.height-260))))}
function recover(){if(!pet||pet.isDestroyed())return; const a=screen.getPrimaryDisplay().workArea;place(a.x+a.width-320,a.y+a.height-280);}
function hide(){state.hidden=true;dragging=false;pet.hide();sendState();}
function show(){state.hidden=false;recover();pet.showInactive();sendState();}
function controls(){if(!panel||panel.isDestroyed()){panel=new BrowserWindow({width:430,height:520,title:'PULU · 控制面板',webPreferences:{preload:path.join(__dirname,'preload.cjs'),contextIsolation:true,nodeIntegration:false,sandbox:true}});protect(panel);panel.loadFile(html,{query:{panel:'1'}});}else panel.show();}
function command(action){switch(action){case 'pause':state.paused=!state.paused;break;case 'reduce':state.reduced=!state.reduced;break;case 'hide':hide();break;case 'show':show();break;case 'controls':controls();break;case 'pet':pet.webContents.send('pointer',{pet:true});break;case 'quit':app.quit();break;default:throw new Error('FORBIDDEN');}sendState();return state;}
if(!app.requestSingleInstanceLock())app.quit();
else {
app.on('second-instance',()=>{if(pet)show();});
app.whenReady().then(()=>{
 pet=new BrowserWindow({width:300,height:260,frame:false,transparent:true,resizable:false,show:false,alwaysOnTop:true,skipTaskbar:true,focusable:false,webPreferences:{preload:path.join(__dirname,'preload.cjs'),contextIsolation:true,nodeIntegration:false,sandbox:true}});
 protect(pet);pet.setIgnoreMouseEvents(true,{forward:true});pet.loadFile(html);recover();
 pet.once('ready-to-show',()=>pet.showInactive());
 pet.webContents.on('render-process-gone',()=>{hide();controls();});
 pet.on('closed',()=>{if(!quitting)app.quit();});
 const icon=nativeImage.createFromDataURL('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg==');
 tray=new Tray(icon);if(process.platform==='darwin')tray.setTitle('扑噜');tray.setToolTip('PULU 技术验证');
 tray.setContextMenu(Menu.buildFromTemplate([{label:'控制面板',click:controls},{label:'显示 / 找回小猫',click:show},{label:'隐藏',click:hide},{label:'暂停 / 继续',click:()=>command('pause')},{type:'separator'},{label:'退出 PULU',click:()=>app.quit()}]));
 Menu.setApplicationMenu(Menu.buildFromTemplate([{label:'PULU',submenu:[{label:'控制面板',click:controls},{label:'隐藏',click:hide},{label:'显示',click:show},{label:'退出',role:'quit'}]}]));
 timer=setInterval(()=>{if(state.hidden||state.locked||pet.isDestroyed())return;const p=screen.getCursorScreenPoint();pointer=p;if(dragging&&dragStart)place(dragStart.x+p.x-dragStart.px,dragStart.y+p.y-dragStart.py);const b=pet.getBounds();pet.webContents.send('pointer',{x:p.x-b.x,y:p.y-b.y});},50);
 for(const evt of ['display-removed','display-metrics-changed'])screen.on(evt,recover);
 powerMonitor.on('suspend',()=>{state.locked=true;pet.hide();sendState();});
 powerMonitor.on('lock-screen',()=>{state.locked=true;pet.hide();sendState();});
 const wake=()=>{state.locked=false;if(!state.hidden){recover();pet.showInactive();}sendState();};
 powerMonitor.on('resume',wake);powerMonitor.on('unlock-screen',wake);
 ipcMain.handle('command',(e,action)=>{if(!trusted(e)||typeof action!=='string')throw new Error('FORBIDDEN');return command(action);});
 ipcMain.on('hit',(e,value)=>{if(!trusted(e)||e.sender!==pet.webContents||typeof value!=='boolean'||dragging)return;pet.setIgnoreMouseEvents(!value,{forward:true});});
 ipcMain.on('drag',(e,value)=>{if(!trusted(e)||e.sender!==pet.webContents||typeof value!=='boolean')return;dragging=value;if(value){const b=pet.getBounds();const p=screen.getCursorScreenPoint();dragStart={x:b.x,y:b.y,px:p.x,py:p.y};pet.setIgnoreMouseEvents(false);}else dragStart=null;});
 ipcMain.on('renderer-ready',e=>{if(!trusted(e))return;sendState();if(smoke&&e.sender===pet.webContents){console.log('PULU_SMOKE_READY');setTimeout(()=>app.quit(),1000);}});
 if(smoke)setTimeout(()=>{console.error('PULU_SMOKE_TIMEOUT');app.exit(1);},15000).unref();
});
app.on('before-quit',()=>{quitting=true;clearInterval(timer);if(tray)tray.destroy();});
app.on('window-all-closed',()=>app.quit());
}
