import * as THREE from 'three';
import {Behavior} from '../core/behavior.js';
const api=window.pulu;
const panel=new URLSearchParams(location.search).has('panel');
const labels={idle:'观察',walk:'探索',sleep:'休息',stretch:'伸懒腰',watch:'看鼠标',pet:'享受抚摸',micro:'小动作'};
let flags={paused:false,hidden:false,reduced:matchMedia('(prefers-reduced-motion: reduce)').matches,locked:false};
if(panel){
 document.body.classList.add('panel');document.querySelector('#controls').hidden=false;
 for(const button of document.querySelectorAll('button'))button.addEventListener('click',()=>api.command(button.dataset.action));
 api.onState(s=>{document.querySelector('#status').textContent=`${s.hidden?'已隐藏':'可见'} · ${s.paused?'已暂停':'活动中'} · ${s.reduced?'减少动态':'正常动态'}`;});api.ready();
}else{
 const behavior=new Behavior();let renderer;
 try{
 renderer=new THREE.WebGLRenderer({alpha:true,antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setSize(300,260);document.body.append(renderer.domElement);
 const scene=new THREE.Scene();const camera=new THREE.PerspectiveCamera(35,300/260,.1,100);camera.position.set(0,1.4,6);camera.lookAt(0,.8,0);
 scene.add(new THREE.HemisphereLight(0xffffff,0x535d6d,3));const light=new THREE.DirectionalLight(0xffffff,3);light.position.set(3,5,4);scene.add(light);
 const cat=new THREE.Group();scene.add(cat);const meshes=[];
 const gray=new THREE.MeshStandardMaterial({color:0xa7abb0,roughness:.9});const white=new THREE.MeshStandardMaterial({color:0xf3f1ea,roughness:.9});const dark=new THREE.MeshStandardMaterial({color:0x464b53,roughness:.9});const red=new THREE.MeshStandardMaterial({color:0xc8443e});
 function ball(parent,mat,x,y,z,sx,sy,sz){const m=new THREE.Mesh(new THREE.SphereGeometry(1,20,14),mat);m.position.set(x,y,z);m.scale.set(sx,sy,sz);parent.add(m);meshes.push(m);return m;}
 ball(cat,gray,0,.65,0,.58,.62,.4);ball(cat,white,0,.57,.33,.4,.45,.15);
 const head=new THREE.Group();head.position.set(0,1.38,.12);cat.add(head);ball(head,gray,0,0,0,.66,.55,.43);ball(head,white,0,-.2,.34,.47,.26,.16);
 for(const x of [-.43,.43]){const ear=new THREE.Mesh(new THREE.ConeGeometry(.22,.45,3),gray);ear.position.set(x,.48,0);head.add(ear);meshes.push(ear);ball(head,dark,x*.65,.03,.41,.095,.12,.055);}
 ball(head,red,0,-.15,.51,.07,.045,.045);
 for(const x of [-.37,.37])ball(cat,white,x,.13,.3,.21,.16,.25);
 ball(cat,red,0,.98,.49,.12,.12,.1);
 for(let i=-1;i<=1;i++)ball(head,dark,i*.19,.3,.35,.045,.16,.045);
 const tail=ball(cat,gray,.66,.55,-.16,.15,.5,.15);tail.rotation.z=-.5;
 const raycaster=new THREE.Raycaster();const mouse=new THREE.Vector2();let cursor={x:150,y:130},pressed=null,drag=false,last=performance.now(),lastFrame=0,stopped=false;
 function stop(){stopped=true;renderer.setAnimationLoop(null);}
 function start(){if(stopped){stopped=false;last=performance.now();renderer.setAnimationLoop(frame);}}
 function frame(now){
  const interval=(flags.paused||behavior.state==='sleep')?1000/15:1000/30;if(now-lastFrame<interval)return;const dt=(now-last)/1000;last=now;lastFrame=now;
  behavior.setPaused(flags.paused);behavior.setReduced(flags.reduced||matchMedia('(prefers-reduced-motion: reduce)').matches);const state=behavior.tick(dt),t=behavior.time;
  if(!flags.paused){
  cat.position.x=state==='walk'&&!behavior.reduced?Math.sin(t)*.32:cat.position.x*.9;
  cat.scale.y=state==='sleep'?.72:state==='stretch'?1.08:1;
  head.rotation.y=Math.max(-.35,Math.min(.35,(cursor.x-150)/400));
  head.rotation.z=state==='pet'?.12:0;tail.rotation.z=-.5+(flags.paused?0:Math.sin(t*2)*.08);
  }
  renderer.render(scene,camera);
 }
 api.onState(s=>{flags=s;if(s.hidden||s.locked)stop();else start();});
 api.onPointer(p=>{if(p.pet){behavior.pet();return;}cursor=p;if(flags.hidden||flags.locked)return;mouse.set(p.x/300*2-1,-p.y/260*2+1);raycaster.setFromCamera(mouse,camera);const hit=raycaster.intersectObjects(meshes,false).length>0;api.hit(hit);});
 const canvas=renderer.domElement;
 canvas.addEventListener('pointerdown',e=>{if(e.button!==0)return;pressed={x:e.clientX,y:e.clientY,time:performance.now()};canvas.setPointerCapture(e.pointerId);});
 canvas.addEventListener('pointermove',e=>{if(pressed&&!drag&&Math.hypot(e.clientX-pressed.x,e.clientY-pressed.y)>6){drag=true;api.drag(true);}});
 function release(e){if(pressed&&!drag&&performance.now()-pressed.time<350)behavior.pet();if(drag)api.drag(false);pressed=null;drag=false;}
 canvas.addEventListener('pointerup',release);canvas.addEventListener('pointercancel',()=>{if(drag)api.drag(false);pressed=null;drag=false;});
 canvas.addEventListener('contextmenu',e=>{e.preventDefault();api.command('controls');});
 canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();stop();document.querySelector('#error').hidden=false;api.hit(false);});
 renderer.setAnimationLoop(frame);api.ready();
 }catch(err){document.querySelector('#error').hidden=false;api.hit(false);console.error('PULU_RENDER_INIT_FAILED',err.message);}
}
