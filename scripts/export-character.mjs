import {writeFile,mkdir} from 'node:fs/promises';
import {GLTFExporter} from 'three/addons/exporters/GLTFExporter.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {buildKitten,createClips} from '../src/character/kitten.js';
class FileReaderShim{readAsArrayBuffer(blob){blob.arrayBuffer().then(v=>{this.result=v;this.onloadend?.();});}readAsDataURL(blob){blob.arrayBuffer().then(v=>{this.result='data:application/octet-stream;base64,'+Buffer.from(v).toString('base64');this.onloadend?.();});}}
globalThis.FileReader=FileReaderShim;
const model=buildKitten(),clips=createClips();
const glb=await new GLTFExporter().parseAsync(model,{binary:true,animations:clips});
await mkdir('assets',{recursive:true});await writeFile('assets/pulu-study.glb',Buffer.from(glb));
const loaded=await new Promise((resolve,reject)=>new GLTFLoader().parse(glb,'',resolve,reject));
let triangles=0,meshCount=0;const materials=new Set();loaded.scene.traverse(o=>{if(o.isMesh){meshCount++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;materials.add(o.material);}});
const report={status:'DESIGN_STUDY_NOT_APPROVED',bytes:glb.byteLength,triangles,meshCount,materials:materials.size,animations:loaded.animations.map(c=>({name:c.name,duration:c.duration,tracks:c.tracks.length})),roundtrip:'PASS',limitations:['transform-node rig, no skinned skeleton','seated walk approximation, not final gait','material/draw-call budget still requires optimization','visual approval pending']};
await writeFile('assets/manifest.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
