'use strict';
const el=id=>document.getElementById(id),pct=n=>typeof n==='number'?(n*100).toFixed(2)+'%':'Pending';
let cachedStudy=null,showErrors=false;
function showSamples(data){
 el('studySamples').replaceChildren();
 const samples=showErrors?(data.failure_cases||[]):(data.samples||[]);
 samples.forEach(item=>{const card=document.createElement('article');card.className='sample-card';const image=document.createElement('img');image.src=item.image_url;image.alt='Held-out handwritten Telugu word';card.append(image);const content=document.createElement('div');content.className='sample-content';
 [['Reference',item.reference],['Original model',item.baseline??'Pending'],['Word adapter',item.prediction]].forEach(([name,text])=>{const small=document.createElement('small'),p=document.createElement('p');small.textContent=name;p.textContent=text;p.lang='te';if(name==='Original model')p.className='baseline';content.append(small,p)});
 if(item.visual_diff){const label=document.createElement('small');label.textContent='Edit diff · CER '+pct(item.cer);content.append(label);const diff=document.createElement('p');diff.lang='te';item.visual_diff.forEach(part=>{if(part.operation==='equal')diff.append(document.createTextNode(part.reference));else{if(part.reference){const d=document.createElement('del');d.style.color='#b04c62';d.textContent=part.reference;diff.append(d)}if(part.prediction){const i=document.createElement('ins');i.style.color='#318365';i.textContent=part.prediction;diff.append(i)}}});content.append(diff)}
 card.append(content);el('studySamples').append(card)});
}
function render(data){
 cachedStudy=data;
 const stage=data.status?.stage||'not started',progress=data.progress;
 el('studyStatus').textContent=data.status?.status==='completed'?'Pilot completed':data.failures?.length?'Run needs attention':'Study in progress';
 el('stageTitle').textContent=({'train':'Training the Telugu word adapter','validation':'Evaluating 500 validation words','baseline-test':'Testing original IndicOCR','adapted-test':'Testing the saved adapter','complete':'Pilot training and evaluation completed'})[stage]||'Waiting for local training';
 const count=stage==='train'?(progress?.example||0):(data.evaluation_progress?.[stage==='validation'?'validation':stage==='baseline-test'?'baseline':'adapted']||0),total=stage==='train'?1000:500;
 el('studyProgress').style.width=(stage==='complete'?100:Math.min(100,100*count/total))+'%';
 el('progressText').textContent=stage==='train'?`${count.toLocaleString()} / 1,000 words processed · latest training loss ${progress?.loss?.toFixed(4)||'pending'} · adapter checkpoints every 100 words`:stage==='complete'?'One fixed epoch finished. Both models were evaluated on the same 500 held-out words.':`${count} / 500 words evaluated in this stage.`;
 el('updated').textContent='Last refreshed '+new Date().toLocaleTimeString();
 el('studyFailure').textContent=(data.failures||[]).map(x=>x.type+': '+x.error).join('\n');
 const b=data.baseline,a=data.adapted;
 const ci=data.analysis?.confidence_intervals_95?.absolute_cer_reduction;
 if(ci)el('intervalNote').textContent=`Paired 95% interval for CER reduction: ${(ci[0]*100).toFixed(2)} to ${(ci[1]*100).toFixed(2)} percentage points. Bootstrap resamples source-document groups; writer identity is unverified.`;
 if(b||a){el('benchmarkRows').replaceChildren();[['Grapheme CER',pct(b?.micro_cer),pct(a?.micro_cer)],['Word error rate',pct(b?.micro_wer),pct(a?.micro_wer)],['Raw exact match',pct(b?.raw_exact_match),pct(a?.raw_exact_match)],['Test examples',b?.examples??'Pending',a?.examples??'Pending'],['Truncated predictions',b?.truncated_count??'Pending',a?.truncated_count??'Pending']].forEach(values=>{const row=document.createElement('tr');values.forEach(value=>{const td=document.createElement('td');td.textContent=value;row.append(td)});el('benchmarkRows').append(row)})}
 showSamples(data);
}
el('firstExamples').onclick=()=>{showErrors=false;if(cachedStudy)showSamples(cachedStudy)};
el('largestErrors').onclick=()=>{showErrors=true;if(cachedStudy)showSamples(cachedStudy)};
async function refresh(){try{let response=await fetch('/api/study',{cache:'no-store'});if(!response.ok)response=await fetch('study-summary.json',{cache:'no-store'});if(!response.ok)throw Error();render(await response.json())}catch{el('studyStatus').textContent='Local study connection required'}}
refresh();setInterval(refresh,15000);

