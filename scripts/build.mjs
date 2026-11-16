import {build} from 'esbuild';
import {mkdir,copyFile,readdir} from 'node:fs/promises';
await mkdir('dist',{recursive:true});
await build({entryPoints:['src/renderer/app.js'],bundle:true,format:'esm',loader:{'.glb':'binary', '.json':'json'},outfile:'dist/app.js',sourcemap:true});
for(const f of ['index.html','style.css'])await copyFile('src/renderer/'+f,'dist/'+f);
await mkdir('dist/sprites',{recursive:true});
for(const f of await readdir('assets/sprites')){
  if(f.endsWith('.webp'))await copyFile('assets/sprites/'+f,'dist/sprites/'+f);
}
