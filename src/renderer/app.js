import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import bytes from '../../assets/pulu-kitten-rigged.glb';
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
 const behavior=new Behavior();let renderer,mixer,model,current,active,pressed,drag=false,cursor={x:WIDTH/2,y:HEIGHT/2},last=performance.now(),lastFrame=0,stopped=false,blinkTime=0;
 const scene=new T.Scene(),camera=new T.PerspectiveCamera(30,WIDTH/HEIGHT,.01,10);camera.position.set(0,.095,.522);camera.lookAt(0,.095,0);
 scene.add(new T.HemisphereLight(0xffffff,0x9aa1ad,0.75));const light=new T.DirectionalLight(0xfff4e8,1.35);light.position.set(-.5,.9,.8);scene.add(light);const fill=new T.DirectionalLight(0xe5ebff,0.45);fill.position.set(.6,.4,-.6);scene.add(fill);
 const raycaster=new T.Raycaster(),mouse=new T.Vector2();
 const clipFor={idle:'idle_observe',walk:'walk_in_place',sleep:'sleep_loop',stretch:'stretch_exit',watch:'cursor_watch',pet:'pet_react',micro:'micro_groom'};
 function feedback(){if(behavior.pet())api.interaction('pet');}
 function stop(){stopped=true;renderer?.setAnimationLoop(null);}
 function resume(){if(renderer&&model&&!flags.hidden&&!flags.locked){stopped=false;last=performance.now();renderer.setAnimationLoop(frame);}}
 function fail(){stop();document.querySelector('#error').hidden=false;api.hit(false);}
 function frame(now){
  const fps=flags.lowPower||flags.paused||behavior.state==='sleep'?15:30;if(now-lastFrame<1000/fps)return;const dt=Math.min((now-last)/1000,.1);last=now;lastFrame=now;
  behavior.setPaused(flags.paused||flags.dragging);behavior.setReduced(flags.reduced||flags.activity==='low'||matchMedia('(prefers-reduced-motion: reduce)').matches);const state=behavior.tick(dt),t=behavior.time;
  if(state!==current){const next=mixer.clipAction(model.animations.find(c=>c.name===clipFor[state]));next.reset().setEffectiveWeight(1).play();if(active)next.crossFadeFrom(active,.25,false);active=next;current=state;}
  if(!flags.paused&&!flags.dragging){mixer.update(dt);model.scene.rotation.y=Math.max(-.12,Math.min(.12,(cursor.x-WIDTH/2)/(WIDTH*4.375)));model.scene.position.x=state==='walk'&&!behavior.reduced?Math.sin(t)*.004:0;model.scene.scale.y=1+Math.sin(t*1.6)*.005;
   blinkTime+=dt;const blink=state==='sleep'?.08:state==='pet'?.35:Math.max(.1,Math.min(1,Math.abs((blinkTime%4.8)-4.55)*15));for(const name of ['EyeL','EyeR']){const eye=model.scene.getObjectByName(name);if(eye)eye.scale.y=blink;}
  }
  renderer.render(scene,camera);
 }
 async function initialize(){
  if(renderer){renderer.dispose();renderer.domElement.remove();}document.querySelector('#error').hidden=true;
  try{renderer=new T.WebGLRenderer({alpha:true,antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setSize(WIDTH,HEIGHT);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=0.95;document.body.append(renderer.domElement);
   model=await new Promise((resolve,reject)=>new GLTFLoader().parse(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'',resolve,reject));scene.add(model.scene);mixer=new T.AnimationMixer(model.scene);current=null;active=null;{const seen=new Set();let meshes=0,skinned=0;const mats=[];model.scene.traverse(o=>{if(o.isMesh){meshes++;if(o.isSkinnedMesh)skinned++;for(const m of [].concat(o.material)){if(seen.has(m))continue;seen.add(m);mats.push({name:m.name,map:!!m.map,imgSize:m.map&&m.map.image?[m.map.image.width,m.map.image.height]:null,color:m.color&&m.color.getHexString()});}}});console.info('[PULU] loaded',JSON.stringify({meshes,skinned,clips:model.animations.length,mats}).slice(0,900));}
   const canvas=renderer.domElement;
   canvas.addEventListener('pointerdown',e=>{if(e.button!==0)return;pressed={x:e.clientX,y:e.clientY,time:performance.now()};canvas.setPointerCapture(e.pointerId);});
   canvas.addEventListener('pointermove',e=>{if(pressed&&!drag&&Math.hypot(e.clientX-pressed.x,e.clientY-pressed.y)>6){drag=true;api.drag(true);}});
   const cancel=()=>{if(drag)api.drag(false);pressed=null;drag=false;};
   canvas.addEventListener('pointerup',()=>{if(pressed&&!drag&&performance.now()-pressed.time<350)feedback();cancel();});canvas.addEventListener('pointercancel',cancel);canvas.addEventListener('lostpointercapture',cancel);
   canvas.addEventListener('contextmenu',e=>{e.preventDefault();api.command('controls');});canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();fail();});canvas.addEventListener('webglcontextrestored',()=>initialize());
   resume();api.ready();
  }catch{fail();}
 }
 api.onState(s=>{flags=s;if(s.hidden||s.locked)stop();else if(stopped)resume();});
 api.onPointer(p=>{if(p.cancelDrag){drag=false;pressed=null;return;}if(p.pet){feedback();return;}cursor=p;if(!model||flags.hidden||flags.locked)return;mouse.set(p.x/WIDTH*2-1,-p.y/HEIGHT*2+1);raycaster.setFromCamera(mouse,camera);api.hit(raycaster.intersectObject(model.scene,true).length>0);});
 document.querySelector('#retry').onclick=()=>{if(model){scene.remove(model.scene);model.scene.traverse(o=>{if(o.isMesh){o.geometry.dispose();o.material.dispose();}});model=null;}initialize();};
 initialize();
}
