import {build} from 'esbuild';
import {mkdir,copyFile} from 'node:fs/promises';
await mkdir('dist',{recursive:true});
await build({entryPoints:['src/renderer/app.js'],bundle:true,format:'esm',loader:{'.glb':'binary'},outfile:'dist/app.js',sourcemap:true});
for(const f of ['index.html','style.css'])await copyFile('src/renderer/'+f,'dist/'+f);
