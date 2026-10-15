/** Build the existing studio for static hosting; never package model/data/run folders. */
import {cpSync,existsSync,mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {resolve,dirname,isAbsolute,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const output=resolve(root,process.argv[2]||'public-release');
if(output===root||!relative(root,output)||relative(root,output).startsWith('..')||isAbsolute(relative(root,output)))throw Error('Output must be a new directory within this checkout.');
if(existsSync(output))throw Error('Output already exists; use a new directory to preserve earlier builds.');
const d=JSON.parse(readFileSync(resolve(root,'dist/capped-study-results-20261015.json'),'utf8'));
if(d.selection_sha256!=='32e18a5c4a29f3855bf323f51944a7ccae53659f60982d3d40b284960e63f00b'||d.selection!=='candidate'||d.protocol.train.count!==25000||d.protocol.validation.count!==5000||d.protocol['final-test'].count!==3000)throw Error('Unexpected frozen study identity.');
mkdirSync(output,{recursive:true});
cpSync(resolve(root,'dist'),output,{recursive:true});
writeFileSync(resolve(output,'deployment-config.js'),"window.AKSHARA_DEPLOYMENT = {staticHosting: true, apiBase: ''};\n");
const metrics=Object.fromEntries(Object.entries(d.models).map(([k,v])=>[k,{...v.final,micro_cer:v.final.nfc_micro_cer,micro_wer:v.final.nfc_micro_wer,...v.timing,...v.diagnostics,subgroups:v.subgroups}]));
const status={recorded_utc:d.generated_utc,status:{status:'completed',stage:'Completed capped study · published snapshot',api_parity:d.api_parity},protocol:{manifests:d.protocol},selection:{variant:d.selection},experiments:Object.values(d.models).map(v=>({name:v.label,metrics:v.validation})),final:{final_metrics:metrics},selected_analysis:{selection:d.selection,selection_sha256:d.selection_sha256,raw_nfc_final_metrics:Object.fromEntries(Object.entries(d.models).map(([k,v])=>[k,v.final])),paired_original_selected:d.paired_original_selected},failure:null};
writeFileSync(resolve(output,'published-study-status.json'),JSON.stringify(status,null,2)+'\n');
console.log(JSON.stringify({output,selection:d.selection,staticHosting:true,inferenceConfigured:false}));
