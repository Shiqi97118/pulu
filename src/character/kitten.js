import * as T from 'three';
// Editable original design study. Units are metres, +Y up, +Z forward.
export function buildKitten() {
 const root=new T.Group();root.name='Pulu';
 const rig=new T.Group();rig.name='BodyRig';root.add(rig);
 const materials={fur:new T.MeshStandardMaterial({color:0xa9adb5,roughness:.94}),silver:new T.MeshStandardMaterial({color:0xc6c9cf,roughness:.95}),stripe:new T.MeshStandardMaterial({color:0x5a606b,roughness:.95}),white:new T.MeshStandardMaterial({color:0xf4f0e9,roughness:.9}),pink:new T.MeshStandardMaterial({color:0xc99197,roughness:.9}),rim:new T.MeshStandardMaterial({color:0x55525a,roughness:.8}),iris:new T.MeshStandardMaterial({color:0x909274,roughness:.42}),pupil:new T.MeshStandardMaterial({color:0x171c24,roughness:.2}),shine:new T.MeshBasicMaterial({color:0xffffff}),red:new T.MeshStandardMaterial({color:0xb64141,roughness:.5}),gold:new T.MeshStandardMaterial({color:0xc0a06a,metalness:.5,roughness:.4})};
 let id=0;
 function ell(parent,mat,p,s,segments=20){const m=new T.Mesh(new T.SphereGeometry(1,segments,14),materials[mat]);m.name='part_'+id++;m.position.set(...p);m.scale.set(...s);parent.add(m);return m;}
 function stroke(parent,mat,points,r=.007){const c=new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p)));const m=new T.Mesh(new T.TubeGeometry(c,12,r,5,false),materials[mat]);m.name='detail_'+id++;parent.add(m);return m;}
 ell(rig,'fur',[0,.09,-.018],[.063,.081,.055],24);
 for(const side of [-1,1]){
  ell(rig,'fur',[side*.052,.051,-.005],[.039,.047,.047]);
  ell(rig,'white',[side*.033,.016,.043],[.026,.016,.033]);
  const paw=new T.Group();paw.name=side<0?'FrontPawL':'FrontPawR';paw.position.set(side*.026,.045,.044);rig.add(paw);
  ell(paw,'white',[0,0,0],[.018,.044,.021]);ell(paw,'white',[0,-.028,.012],[.024,.017,.029]);
  for(const dx of [-.008,.004])stroke(paw,'silver',[[dx,-.029,.039],[dx,-.024,.04]],.0007);
 }
 ell(rig,'white',[0,.1,.031],[.041,.06,.035]);
 const tail=new T.Group();tail.name='Tail';tail.position.set(.055,.035,-.03);rig.add(tail);
 const tailPoints=[[0,0,0],[.035,.005,.004],[.055,.015,.035],[.05,.02,.073],[.025,.019,.083]];
 stroke(tail,'fur',tailPoints,.014);
 for(const t of [.2,.43,.66,.88]){const curve=new T.CatmullRomCurve3(tailPoints.map(p=>new T.Vector3(...p)));const pos=curve.getPoint(t);const ring=new T.Mesh(new T.TorusGeometry(.0142,.0025,5,14),materials.stripe);ring.position.copy(pos);ring.quaternion.setFromUnitVectors(new T.Vector3(0,0,1),curve.getTangent(t));tail.add(ring);}
 const collar=new T.Mesh(new T.TorusGeometry(.043,.005,7,32),materials.red);collar.rotation.x=Math.PI/2;collar.position.set(0,.145,.005);rig.add(collar);
 const bell=new T.Group();bell.name='Bell';bell.position.set(0,.131,.054);rig.add(bell);
 ell(bell,'red',[0,0,0],[.011,.012,.011]);stroke(bell,'stripe',[[-.007,-.004,.009],[0,-.006,.011],[.007,-.004,.009]],.0008);ell(bell,'gold',[0,.012,0],[.004,.004,.003]);
 const head=new T.Group();head.name='Head';head.position.set(0,.191,.01);rig.add(head);
 ell(head,'fur',[0,0,0],[.084,.065,.065],32);
 for(const side of [-1,1]) {
  ell(head,'silver',[side*.058,-.016,.017],[.032,.032,.038]);
  const ear=new T.Group();ear.name=side<0?'EarL':'EarR';ear.position.set(side*.054,.042,-.012);ear.rotation.z=side*-.12;head.add(ear);
  const shape=new T.Shape();shape.moveTo(-.023,-.009);shape.quadraticCurveTo(-.021,.014,-.011,.034);shape.quadraticCurveTo(-.005,.042,.001,.035);shape.quadraticCurveTo(.025,.007,.025,-.012);shape.quadraticCurveTo(0,-.024,-.023,-.009);
  const geom=new T.ExtrudeGeometry(shape,{depth:.013,bevelEnabled:true,bevelSegments:3,steps:1,bevelSize:.005,bevelThickness:.005,curveSegments:8});const outer=new T.Mesh(geom,materials.fur);ear.add(outer);
  const inner=new T.Mesh(geom,materials.pink);inner.scale.set(.63,.67,.2);inner.position.set(0,.001,.019);ear.add(inner);
  const eye=new T.Group();eye.name=side<0?'EyeL':'EyeR';eye.position.set(side*.035,-.002,.052);eye.rotation.y=side*.16;head.add(eye);
  ell(eye,'rim',[0,0,0],[.024,.025,.014]);ell(eye,'iris',[0,0,.006],[.0215,.022,.012]);ell(eye,'pupil',[side*-.001,.001,.015],[.0135,.018,.006]);
  ell(eye,'shine',[-.007,.009,.021],[.005,.006,.002],12);ell(eye,'shine',[.007,-.006,.021],[.002,.002,.001],10);
  ell(head,'white',[side*.017,-.029,.055],[.025,.018,.021]);
  for(let i=0;i<2;i++) stroke(head,'stripe',[[side*.062,-.013-i*.012,.047],[side*.078,-.007-i*.014,.029],[side*.081,-.002-i*.015,.012]],.003-i*.0005);
  for(let i=0;i<3;i++)stroke(head,'white',[[side*.025,-.031-i*.003,.069],[side*.065,-.028-i*.005,.073],[side*.097,-.019-i*.011,.064]],.0007);
 }
 ell(head,'white',[0,-.043,.043],[.031,.012,.021]);ell(head,'pink',[0,-.022,.077],[.008,.005,.004],16);
 stroke(head,'rim',[[0,-.026,.077],[0,-.033,.075],[-.009,-.036,.072]],.0009);stroke(head,'rim',[[0,-.033,.075],[.009,-.036,.072]],.0009);
 // M-shaped forehead tabby markings hug the ellipsoid, with tapered endpoints.
 for(const side of [-1,1]){
  stroke(head,'stripe',[[side*.007,.018,.062],[side*.012,.035,.054],[side*.021,.051,.039]],.0035);
  stroke(head,'stripe',[[side*.023,.021,.059],[side*.029,.04,.047],[side*.039,.05,.032]],.0027);
  stroke(head,'stripe',[[side*.008,.03,.057],[side*.021,.039,.052],[side*.03,.026,.056]],.0024);
  for(let i=0;i<3;i++)stroke(rig,'stripe',[[side*.045,.115-i*.022,-.045],[side*.06,.1-i*.02,-.03],[side*.064,.09-i*.02,-.01]],.0035);
 }
 root.userData={version:'0.2-study.1',status:'DESIGN_STUDY_NOT_APPROVED',units:'metres',originalSource:'src/character/kitten.js',eyeColor:'proposed olive; pending Q02'};
 return root;
}
export function createClips(){
 const q=(axis,angle)=>new T.Quaternion().setFromAxisAngle(new T.Vector3(...axis),angle).toArray();
 const rotation=(name,axis,values,times)=>new T.QuaternionKeyframeTrack(name+'.quaternion',times,values.flatMap(v=>q(axis,v)));
 const clip=(name,duration,tracks)=>new T.AnimationClip(name,duration,tracks);
 return [
 clip('idle_observe',6,[rotation('Head',[0,1,0],[0,-.06,.08,0],[0,2,4,6])]),
 clip('walk_in_place',1.2,[rotation('FrontPawL',[1,0,0],[0,.12,0,-.12,0],[0,.3,.6,.9,1.2]),rotation('FrontPawR',[1,0,0],[0,-.12,0,.12,0],[0,.3,.6,.9,1.2])]),
 clip('sleep_enter',2,[rotation('Head',[1,0,0],[0,.2],[0,2])]),
 clip('sleep_loop',6,[rotation('Head',[1,0,0],[.2,.23,.2],[0,3,6])]),
 clip('stretch_exit',3,[rotation('Head',[1,0,0],[.2,-.12,0],[0,1.5,3])]),
 clip('cursor_watch',4,[rotation('Head',[0,1,0],[0,.15,-.15,0],[0,1,3,4])]),
 clip('pet_react',1.5,[rotation('Head',[0,0,1],[0,.08,-.04,0],[0,.4,1,1.5])]),
 clip('micro_groom',3,[rotation('FrontPawL',[1,0,0],[0,-.6,-.4,0],[0,1,2,3]),rotation('Head',[1,0,0],[0,.15,.1,0],[0,1,2,3])]),
 clip('micro_ear_tail',2,[rotation('EarL',[0,0,1],[.12,.2,.12],[0,.5,2])]),
 clip('intro_peek',3,[rotation('Head',[0,0,1],[0,-.12,.08,0],[0,1,2,3])])];
}
