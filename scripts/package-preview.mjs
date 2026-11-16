import {cp,mkdir,access} from 'node:fs/promises';
import path from 'node:path';
if(process.platform!=='darwin'||process.arch!=='arm64')throw new Error('This preview packaging script currently targets macOS Apple Silicon.');
const destination=path.resolve(process.argv[2]||'artifacts/PULU.app');
try{await access(destination);throw new Error('Destination exists; choose a new preview path to preserve existing output.');}catch(e){if(e.code!=='ENOENT')throw e;}
await cp('node_modules/electron/dist/Electron.app',destination,{recursive:true});
const app=path.join(destination,'Contents/Resources/app');await mkdir(path.join(app,'src/desktop'),{recursive:true});
await cp('src/desktop',path.join(app,'src/desktop'),{recursive:true});
await cp('dist',path.join(app,'dist'),{recursive:true});
await cp('package.json',path.join(app,'package.json'));
console.log(destination);
