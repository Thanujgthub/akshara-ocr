const byId=id=>document.getElementById(id);
const percent=value=>typeof value==='number'?(100*value).toFixed(2)+'%':'Pending';
async function refresh(){
  try{
    const responses=await Promise.all([fetch('/api/research-v2',{cache:'no-store'}),fetch('/api/health',{cache:'no-store'})]);
    if(responses.some(r=>!r.ok))throw new Error('Progress service unavailable; last values may be stale.');
    const [d,health]=await Promise.all(responses.map(r=>r.json()));
    byId('state').textContent=d.status.status;byId('stage').textContent=d.status.stage;
    byId('updated').textContent='Last fetched '+new Date().toLocaleTimeString();
    for(const split of ['train','validation','final-test'])byId(split).textContent=d.protocol?.manifests?.[split]?.count?.toLocaleString()??'Pending';
    const p=d.progress||d.evaluation;
    const n=p?.example??p?.evaluated??0,total=p?.examples_per_epoch??p?.total??0;
    byId('bar').value=total?Math.min(100,100*n/total):0;
    byId('progress').textContent=p?`${n.toLocaleString()} / ${total.toLocaleString()} in this stage${p.epoch?' · epoch '+p.epoch:''}${typeof p.loss==='number'?' · loss '+p.loss.toFixed(4):''}`:d.status.note||'Waiting for the next measured progress record.';
    const t=d.training_timing;
    byId('timing').textContent=t?`Recent ${t.recent_median_seconds_per_word.toFixed(2)} seconds/example. About ${Math.ceil(t.current_epoch_remaining_seconds_excluding_pauses/60)} minutes left in this epoch; excludes pauses and evaluation.`:'';
    byId('metrics').replaceChildren();
    for(const e of d.experiments||[]){const row=document.createElement('tr');for(const v of [e.name,e.metrics.examples,percent(e.metrics.micro_cer),percent(e.metrics.raw_exact_match)]){const cell=document.createElement('td');cell.textContent=v;row.append(cell)}byId('metrics').append(row)}
    byId('selection').textContent=d.selection?`Validation-locked selection: ${d.selection.variant}. Final test cannot change it.`:'Selection has not been locked.';
    byId('api').textContent=health.training_active?'API inference paused for GPU training/testing.':health.model_load_verified?'API model loaded; parity verification is a separate check.':'API responding; model has not been loaded or verified in this server session.';
    byId('failure').textContent=d.failure?JSON.stringify(d.failure,null,2):'No reported coordinator failure.';
  }catch(e){byId('state').textContent=e.message;byId('bar').removeAttribute('value')}
}
refresh();setInterval(refresh,5000);
