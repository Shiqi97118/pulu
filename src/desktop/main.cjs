const {app,BrowserWindow,ipcMain,Menu,Tray,nativeImage,screen,powerMonitor,dialog,globalShortcut}=require('electron');
const path=require('node:path');const fs=require('node:fs/promises');const {pathToFileURL}=require('node:url');const {LocalStore}=require('../core/store.cjs');
app.setName('PULU');let pet,panel,tray,timer,store,dragStart,quitting=false,flushing=false;let lastHit=false,lastPointer='';
const {WIDTH:W,HEIGHT:H}=require('../core/viewport.cjs');const flags={hidden:false,locked:false,dragging:false,error:null};const smoke=process.argv.includes('--smoke');
const shotArg=process.argv.find(a=>a.startsWith('--shot='));const shotPath=shotArg?shotArg.slice(7):null;
if(smoke||shotPath)app.setPath('userData',path.join(app.getPath('temp'),shotPath?'pulu-shot-user-data':'pulu-smoke-user-data'));
const html=path.resolve(__dirname,'../../dist/index.html'),fileURL=pathToFileURL(html).href;
const valid=(e)=>[pet,panel].some(w=>w&&!w.isDestroyed()&&e.sender===w.webContents)&&e.senderFrame&&e.senderFrame===e.sender.mainFrame&&e.senderFrame.url.split('?')[0]===fileURL;
function snapshot(){return {...store.snapshot().settings,...flags,local:store.snapshot()};}
function sendState(){for(const w of [pet,panel])if(w&&!w.isDestroyed())w.webContents.send('state',snapshot());}
function guard(w){w.webContents.setWindowOpenHandler(()=>({action:'deny'}));w.webContents.on('will-navigate',e=>e.preventDefault());w.webContents.session.setPermissionRequestHandler((_w,_p,cb)=>cb(false));w.webContents.session.webRequest.onBeforeRequest((d,cb)=>cb({cancel:!['file://','blob:','data:'].some(s=>d.url.startsWith(s))}));}
function place(x,y){const a=screen.getDisplayNearestPoint({x:Math.round(x+W/2),y:Math.round(y+H/2)}).workArea;pet.setPosition(Math.round(Math.min(Math.max(x,a.x),a.x+Math.max(0,a.width-W))),Math.round(Math.min(Math.max(y,a.y),a.y+Math.max(0,a.height-H))));}
function recover(){if(!pet||pet.isDestroyed())return;const a=screen.getPrimaryDisplay().workArea;place(a.x+a.width-W-24,a.y+a.height-H-12);}
function endDrag(cancel=false){if(cancel&&dragStart)place(dragStart.x,dragStart.y);flags.dragging=false;dragStart=null;globalShortcut.unregister('Escape');sendState();}
function hide(){endDrag();flags.hidden=true;pet.hide();sendState();}
function show(){flags.hidden=false;if(!flags.locked){recover();pet.showInactive();}sendState();}
function controls(){if(!panel||panel.isDestroyed()){panel=new BrowserWindow({width:480,height:740,title:'PULU',webPreferences:{preload:path.join(__dirname,'preload.cjs'),contextIsolation:true,nodeIntegration:false,sandbox:true}});guard(panel);panel.loadFile(html,{query:{panel:'1'}});}else panel.show();}
async function action(kind,payload){
 const rev=store.snapshot().revision;
 switch(kind){
 case 'pause':await store.settings({paused:!store.snapshot().settings.paused},rev);break;
 case 'reduce':await store.settings({reduced:!store.snapshot().settings.reduced},rev);break;
 case 'lowPower':await store.settings({lowPower:!store.snapshot().settings.lowPower},rev);break;
 case 'quiet':await store.settings({activity:store.snapshot().settings.activity==='low'?'normal':'low'},rev);break;
 case 'hide':hide();break;case 'show':show();break;case 'controls':controls();break;
 case 'pet':pet.webContents.send('pointer',{pet:true});break;
 case 'savePreference':if(!payload||typeof payload.kind!=='string')throw Error('VALIDATION');await store.savePreference(payload.kind,payload.value,payload.revision);break;
 case 'deleteMemory':if(!payload||typeof payload.id!=='string')throw Error('VALIDATION');await store.deleteMemory(payload.id,payload.revision);break;
 case 'export':{const choice=await dialog.showSaveDialog(panel,{defaultPath:'pulu-local-data.json',filters:[{name:'JSON',extensions:['json']}]});if(!choice.canceled)await fs.writeFile(choice.filePath,JSON.stringify(store.snapshot(),null,2),{mode:0o600});break;}
 case 'quit':app.quit();break;default:throw Error('FORBIDDEN');
 }
 sendState();return snapshot();
}
if(!app.requestSingleInstanceLock())app.quit();else{
app.on('second-instance',()=>{if(pet)show();});
app.whenReady().then(async()=>{
 pet=new BrowserWindow({width:W,height:H,frame:false,transparent:true,resizable:false,show:false,alwaysOnTop:true,skipTaskbar:true,focusable:false,webPreferences:{preload:path.join(__dirname,'preload.cjs'),contextIsolation:true,nodeIntegration:false,sandbox:true}});
 store=new LocalStore(app.getPath('userData'));try{await store.load();}catch(e){dialog.showErrorBox('PULU',e.message+'\nPlease preserve your data directory for recovery.');app.quit();return;}
 guard(pet);if(shotPath)pet.webContents.on('console-message',(ev,level,msg)=>console.log('RENDERER:',msg));pet.setIgnoreMouseEvents(true,{forward:true});recover();
 ipcMain.handle('command',async(e,kind,payload)=>{if(!valid(e)||typeof kind!=='string')throw Error('FORBIDDEN');try{return {ok:true,state:await action(kind,payload)};}catch(error){return {ok:false,error:error.message};}});
 ipcMain.on('hit',(e,v)=>{if(!valid(e)||e.sender!==pet.webContents||typeof v!=='boolean'||flags.dragging||v===lastHit)return;lastHit=v;pet.setIgnoreMouseEvents(!v,{forward:true});});
 ipcMain.on('drag',(e,v)=>{if(!valid(e)||e.sender!==pet.webContents||typeof v!=='boolean')return;if(!v){endDrag();return;}if(flags.dragging)return;const b=pet.getBounds(),p=screen.getCursorScreenPoint();flags.dragging=true;dragStart={x:b.x,y:b.y,px:p.x,py:p.y};pet.setIgnoreMouseEvents(false);if(!globalShortcut.register('Escape',()=>{pet.webContents.send('pointer',{cancelDrag:true});endDrag(true);})){flags.error='Escape shortcut unavailable; release pointer to finish dragging.';}sendState();});
 ipcMain.on('interaction',(e,type)=>{if(!valid(e)||e.sender!==pet.webContents||type!=='pet')return;store.recordPet().then(sendState).catch(()=>{flags.error='STORAGE';sendState();});});
 ipcMain.on('renderer-ready',e=>{if(!valid(e))return;sendState();if(smoke&&e.sender===pet.webContents){console.log('PULU_SMOKE_READY');setTimeout(()=>app.quit(),1000);}
 if(shotPath&&e.sender===pet.webContents){setTimeout(async()=>{try{const image=await e.sender.capturePage();await fs.writeFile(shotPath,image.toPNG());console.log('PULU_SHOT_SAVED',shotPath);}catch(error){console.log('PULU_SHOT_FAILED',error.message);}app.quit();},1200);}});
 const icon=nativeImage.createFromPath(path.join(__dirname,'tray.png'));icon.setTemplateImage(true);tray=new Tray(icon);if(process.platform==='darwin')tray.setTitle('扑噜');tray.setToolTip('PULU');
 const menu=[{label:'控制面板',click:controls},{label:'显示 / 找回小猫',click:show},{label:'隐藏 / 演示模式',click:hide},{label:'暂停 / 继续',click:()=>action('pause').catch(()=>{})},{type:'separator'},{label:'退出 PULU',click:()=>app.quit()}];tray.setContextMenu(Menu.buildFromTemplate(menu));Menu.setApplicationMenu(Menu.buildFromTemplate([{label:'PULU',submenu:menu}]));
 pet.once('ready-to-show',()=>pet.showInactive());pet.webContents.on('render-process-gone',()=>{hide();flags.error='RENDERER_STOPPED';controls();});pet.on('closed',()=>{if(!quitting)app.quit();});pet.loadFile(html);
 timer=setInterval(()=>{if(flags.hidden||flags.locked||pet.isDestroyed())return;const p=screen.getCursorScreenPoint();if(flags.dragging&&dragStart)place(dragStart.x+p.x-dragStart.px,dragStart.y+p.y-dragStart.py);const b=pet.getBounds(),key=`${p.x},${p.y},${b.x},${b.y}`;if(key!==lastPointer||lastHit){lastPointer=key;pet.webContents.send('pointer',{x:p.x-b.x,y:p.y-b.y});}},50);
 for(const name of ['display-removed','display-metrics-changed'])screen.on(name,recover);
 const suspend=()=>{endDrag();flags.locked=true;pet.hide();sendState();},wake=()=>{flags.locked=false;if(!flags.hidden){recover();pet.showInactive();}sendState();};
 powerMonitor.on('suspend',suspend);powerMonitor.on('lock-screen',suspend);powerMonitor.on('resume',wake);powerMonitor.on('unlock-screen',wake);
 if(smoke)setTimeout(()=>app.exit(1),15000).unref();
}).catch(e=>{dialog.showErrorBox('PULU startup error',String(e));app.quit();});
app.on('before-quit',e=>{if(store&&!flushing){e.preventDefault();flushing=true;store.flush().finally(()=>app.quit());return;}quitting=true;clearInterval(timer);globalShortcut.unregisterAll();tray?.destroy();});
app.on('window-all-closed',()=>app.quit());
}
