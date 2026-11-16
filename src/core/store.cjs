const fs=require('node:fs/promises');const path=require('node:path');const {randomUUID}=require('node:crypto');
const defaults={paused:false,reduced:false,lowPower:false,activity:'normal'};
class LocalStore{
 constructor(dir){this.dir=dir;this.file=path.join(dir,'pet.json');this.backup=path.join(dir,'settings-backup.json');this.queue=Promise.resolve();this.data=null;this.recovered=false;}
 validate(d){if(d?.schemaVersion!==1||!Number.isInteger(d.revision)||d.revision<0||!Number.isInteger(d.memoryEpoch)||d.memoryEpoch<0||typeof d.petId!=='string'||!Array.isArray(d.memories)||d.memories.length>32||!d.settings||Object.keys(defaults).some(k=>typeof d.settings[k]!==typeof defaults[k])||!['low','normal'].includes(d.settings.activity))throw Error('INVALID_SAVE');return d;}
 fresh(){return {schemaVersion:1,petId:randomUUID(),revision:0,memoryEpoch:0,settings:{...defaults},memories:[],summary:[],updatedAt:new Date().toISOString()};}
 async load(){await fs.mkdir(this.dir,{recursive:true,mode:0o700});try{this.data=this.validate(JSON.parse(await fs.readFile(this.file,'utf8')));}catch(e){if(e.code==='ENOENT'){this.data=this.fresh();return this.snapshot();}try{this.data=this.validate(JSON.parse(await fs.readFile(this.backup,'utf8')));this.recovered=true;}catch{throw Error('SAVE_CORRUPT_NO_RECOVERY');}}return this.snapshot();}
 snapshot(){return structuredClone({...this.data,recovered:this.recovered});}
 async atomic(file,value){const temp=file+'.tmp';await fs.writeFile(temp,JSON.stringify(value),{mode:0o600});await fs.rename(temp,file);}
 async persist(next){
 // Backup intentionally never contains memories or interaction history, so recovery cannot resurrect deleted content.
 await this.atomic(this.backup,{...next,memories:[],summary:[]});await this.atomic(this.file,next);this.data=next;
 }
 mutate(expected,change){const job=this.queue.then(async()=>{if(expected!==this.data.revision)throw Error('CONFLICT');const n=structuredClone(this.data);change(n);n.revision++;n.updatedAt=new Date().toISOString();await this.persist(n);return this.snapshot();});this.queue=job.catch(()=>{});return job;}
 settings(patch,expected){if(!patch||Object.keys(patch).some(k=>!(k in defaults)||typeof patch[k]!==typeof defaults[k])||(patch.activity&&!['low','normal'].includes(patch.activity)))return Promise.reject(Error('VALIDATION'));return this.mutate(expected,n=>Object.assign(n.settings,patch));}
 savePreference(kind,value,expected){if(!['petName','interactionStyle'].includes(kind)||typeof value!=='string'||!value.trim()||value.length>24||(kind==='interactionStyle'&&!['quiet','playful'].includes(value)))return Promise.reject(Error('VALIDATION'));return this.mutate(expected,n=>{n.memories=n.memories.filter(m=>m.kind!==kind);n.memories.push({id:randomUUID(),kind,value:value.trim(),source:'userConfirmed',createdAt:new Date().toISOString(),epoch:n.memoryEpoch});});}
 deleteMemory(id,expected){if(id!=='all'&&typeof id!=='string')return Promise.reject(Error('VALIDATION'));return this.mutate(expected,n=>{n.memoryEpoch++;n.memories=id==='all'?[]:n.memories.filter(m=>m.id!==id);if(id==='all')n.summary=[];});}
 recordPet(){const run=this.queue.then(async()=>{const n=structuredClone(this.data),day=new Date().toISOString().slice(0,10);n.summary=(n.summary||[]).filter(d=>d.day>=new Date(Date.now()-13*86400000).toISOString().slice(0,10));let d=n.summary.find(d=>d.day===day);if(!d){d={day,pets:0};n.summary.push(d);}d.pets++;n.revision++;n.updatedAt=new Date().toISOString();await this.persist(n);return this.snapshot();});this.queue=run.catch(()=>{});return run;}
 async flush(){await this.queue;}
}
module.exports={LocalStore};
