import {SpritePlayer} from './sprite-player.js';
import spriteManifest from '../../assets/sprites/manifest.json';
import {Behavior} from '../core/behavior.js';
import {WIDTH,HEIGHT} from '../core/viewport.cjs';
const api=window.pulu,panel=new URLSearchParams(location.search).has('panel');let flags={paused:false,hidden:false,reduced:false,lowPower:false,activity:'normal',dragging:false,locked:false},local;
async function command(kind,payload){const result=await api.command(kind,payload);if(!result.ok)document.querySelector('#notice').textContent=result.error==='CONFLICT'?'资料刚刚更新，请再试一次。':'保存失败：'+result.error;return result;}
if(panel){
 document.title='PULU · 控制面板';document.body.classList.add('panel');document.querySelector('#controls').hidden=false;
 for(const button of document.querySelectorAll('[data-action]'))button.addEventListener('click',()=>command(button.dataset.action));
 document.querySelector('#nameForm').addEventListener('submit',async e=>{e.preventDefault();if(local)await command('savePreference',{kind:'petName',value:document.querySelector('#petName').value,revision:local.revision});});
 document.querySelector('#clear').addEventListener('click',()=>{document.querySelector('#confirmClear').hidden=false;document.querySelector('#cancelDelete').focus();});
 document.querySelector('#cancelDelete').addEventListener('click',()=>{document.querySelector('#confirmClear').hidden=true;document.querySelector('#clear').focus();});
 document.querySelector('#confirmDelete').addEventListener('click',async()=>{const r=await command('deleteMemory',{id:'all',revision:local.revision});if(r.ok){document.querySelector('#confirmClear').hidden=true;document.querySelector('#clear').focus();}});
 api.onState(s=>{flags=s;local=s.local;
  document.querySelector('#status').textContent=`${s.hidden?'已隐藏':'可见'} · ${s.paused?'已暂停':'活动中'} · ${s.reduced?'减少动态':'正常动态'}${s.lowPower?' · 低功耗':''}`;
  document.querySelector('#notice').textContent=s.error||(local.recovered?'存档损坏：已恢复设置，记忆未从旧备份还原。':'');
  for(const [kind,key] of [['pause','paused'],['reduce','reduced'],['lowPower','lowPower']])document.querySelector(`[data-action="${kind}"]`).setAttribute('aria-pressed',String(s[key]));
  document.querySelector('[data-action="quiet"]').setAttribute('aria-pressed',String(s.activity==='low'));
  const list=document.querySelector('#memories');list.replaceChildren();
  for(const m of local.memories){const li=document.createElement('li'),text=document.createElement('span'),button=document.createElement('button');text.textContent=(m.kind==='petName'?'称呼：':'互动偏好：')+m.value;button.textContent='删除';button.setAttribute('aria-label','删除'+text.textContent);button.onclick=()=>command('deleteMemory',{id:m.id,revision:local.revision});li.append(text,button);list.append(li);}
  document.querySelector('#summary').textContent='近14天摸摸：'+(local.summary||[]).reduce((a,d)=>a+d.pets,0)+' 次';
 });api.ready();
}else{
 const behavior=new Behavior();let player,current,pressed,drag=false,cursor={x:WIDTH/2,y:HEIGHT/2},stopped=false,sway=0;
 const canvas=document.createElement('canvas');canvas.className='sprite';canvas.width=152;canvas.height=152;
 canvas.setAttribute('role','img');canvas.setAttribute('aria-label','扑噜，一只银灰虎斑白胸小猫');document.body.append(canvas);
 const clipFor={idle:'idle_observe',walk:'walk_in_place',sleep:'sleep_loop',stretch:'stretch_exit',watch:'cursor_watch',pet:'pet_react',micro:'micro_groom'};
 function feedback(){if(behavior.pet())api.interaction('pet');}
 function stop(){stopped=true;player?.setPaused(true);}
 function resume(){stopped=false;player?.setPaused(false);}
 function fail(){stop();document.querySelector('#error').hidden=false;api.hit(false);}
 function tickBehavior(dt){
  behavior.setPaused(flags.paused||flags.dragging);
  behavior.setReduced(flags.reduced||flags.activity==='low'||matchMedia('(prefers-reduced-motion: reduce)').matches);
  const state=behavior.tick(dt);
  player?.setReduced(behavior.reduced);
  if(state!==current){current=state;player.play(clipFor[state]);}
  if(!behavior.reduced){
   const walk=state==='walk'?Math.sin(behavior.time*3)*4:0;
   if(Math.abs(walk-sway)>0.1){sway=walk;canvas.style.transform=`translateX(calc(-50% + ${walk.toFixed(1)}px))`;}
  }
 }
 function bindPointer(){
  if(canvas.dataset.bound)return;canvas.dataset.bound='1';
  canvas.addEventListener('pointerdown',e=>{if(e.button!==0)return;pressed={x:e.clientX,y:e.clientY,time:performance.now()};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(pressed&&!drag&&Math.hypot(e.clientX-pressed.x,e.clientY-pressed.y)>6){drag=true;api.drag(true);}});
  const cancel=()=>{if(drag)api.drag(false);pressed=null;drag=false;};
  canvas.addEventListener('pointerup',()=>{if(pressed&&!drag&&performance.now()-pressed.time<350)feedback();cancel();});
  canvas.addEventListener('pointercancel',cancel);canvas.addEventListener('lostpointercapture',cancel);
  canvas.addEventListener('contextmenu',e=>{e.preventDefault();api.command('controls');});
 }
 async function initialize(){
  document.querySelector('#error').hidden=true;
  try{
   player=new SpritePlayer(canvas,{onTick:tickBehavior});
   await player.load(spriteManifest);
   current=null;sway=0;bindPointer();resume();
   await player.play(clipFor[behavior.state]||'idle_observe');   // starts the rAF loop
   api.ready();
  }catch{fail();}
 }
 api.onState(s=>{flags=s;if(s.hidden||s.locked)stop();else if(stopped)resume();});
 api.onPointer(p=>{if(p.cancelDrag){drag=false;pressed=null;return;}if(p.pet){feedback();return;}cursor=p;if(!player||flags.hidden||flags.locked)return;player.hit(p.x,p.y).then(hit=>api.hit(hit));});
 document.querySelector('#retry').onclick=()=>initialize();
 initialize();
}
