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
    const active=d.status.status==='running';
    const completed=d.status.status==='completed'&&Boolean(d.final);
    const n=p?.example??p?.evaluated??0,total=p?.examples_per_epoch??p?.total??0;
    byId('bar').value=completed?100:total?Math.min(100,100*n/total):0;
    byId('progress').textContent=completed?'Training, validation and all final comparisons are complete. Model/API verification is shown below.':p?`${active?'':'Last recorded: '}${n.toLocaleString()} / ${total.toLocaleString()} in this stage${p.epoch?' · epoch '+p.epoch:''}${typeof p.loss==='number'?' · loss '+p.loss.toFixed(4):''}`:d.status.note||'Waiting for the next measured progress record.';
    const t=d.training_timing;
    byId('timing').textContent=active&&t?`Recent ${t.recent_median_seconds_per_word.toFixed(2)} seconds/example. About ${Math.ceil(t.current_epoch_remaining_seconds_excluding_pauses/60)} minutes left in this epoch; excludes pauses and evaluation.`:d.status.status==='completed'?'':'Training ETA is unavailable while this stage is stopped or preparing.';
    byId('metrics').replaceChildren();
    for(const e of d.experiments||[]){const row=document.createElement('tr');for(const v of [e.name,e.metrics.examples,percent(e.metrics.micro_cer),percent(e.metrics.raw_exact_match)]){const cell=document.createElement('td');cell.textContent=v;row.append(cell)}byId('metrics').append(row)}
    byId('selection').textContent=d.selection?`Validation-locked selection: ${d.selection.variant}. Final test cannot change it.`:'Selection has not been locked.';
    const final=d.status.status==='completed'?d.final:null;
    byId('finalResults').hidden=!final;
    byId('finalStatus').textContent=final?'Completed sealed comparison on identical frozen inputs.':'Sealed; final results appear only after the complete study is recorded.';
    byId('finalMetrics').replaceChildren();
    if(final){
      const analysis=d.selected_analysis;
      const diagnostics={};
      for(const [name,m] of Object.entries(final.final_metrics||{})){
        const supplemental=analysis?.raw_nfc_final_metrics?.[name];
        const row=document.createElement('tr');
        for(const value of [name,m.examples,percent(supplemental?.raw_micro_cer??m.raw_micro_cer),percent(supplemental?.nfc_micro_cer??m.micro_cer),percent(supplemental?.raw_micro_wer),percent(supplemental?.nfc_micro_wer??m.micro_wer),percent(supplemental?.raw_exact_match??m.raw_exact_match),percent(supplemental?.nfc_exact_match??m.nfc_exact_match)]){const cell=document.createElement('td');cell.textContent=value;row.append(cell)}
        byId('finalMetrics').append(row);
        diagnostics[name]=Object.fromEntries(['script_contamination_rate','refusal_rate','malformed_output_rate','repetition_candidate_rate','abstention_rate','truncated_count','latency_median_seconds','latency_p95_seconds','peak_allocated_vram_bytes','peak_vram_scope','resumed_predictions_count','subgroups'].filter(key=>key in m).map(key=>[key,m[key]]));
      }
      byId('finalDiagnostics').textContent=JSON.stringify(diagnostics,null,2);
      const intervals=[];
      for(const [label,key] of [['Original versus candidate','final_paired_original_candidate'],['Pilot versus candidate','final_paired_pilot_candidate']]){
        const comparison=final[key],interval=comparison?.cer_reduction_95;
        if(Array.isArray(interval)&&interval.length===2)intervals.push(`${label}: paired 95% interval for NFC CER reduction [${(100*interval[0]).toFixed(2)}, ${(100*interval[1]).toFixed(2)}] percentage points. ${comparison.interpretation||''}`);
      }
      const selected=analysis?.paired_original_selected;
      if(selected){
        for(const [key,label] of [['raw_cer_reduction','raw CER reduction'],['nfc_cer_reduction','NFC CER reduction'],['raw_wer_reduction','raw WER reduction'],['nfc_wer_reduction','NFC WER reduction'],['raw_exact_gain','raw exact gain'],['nfc_exact_gain','NFC exact gain']]){
          const interval=selected.intervals_95?.[key];
          if(Array.isArray(interval)&&interval.length===2)intervals.push(`Original versus selected (${analysis.selection}): ${label} paired 95% interval [${(100*interval[0]).toFixed(2)}, ${(100*interval[1]).toFixed(2)}] percentage points.`);
        }
        intervals.push(selected.interpretation||'',...(selected.warnings||[]));
      }
      byId('pairedIntervals').textContent=intervals.join(' ');
    }
    const parity=d.status.api_parity;
    const verifiedParity=parity?.passed===true&&parity.mismatches?.length===0&&parity.validation_examples>0&&parity.api_requests===2*parity.validation_examples&&typeof parity.selection_sha256==='string'&&parity.selection_sha256===d.selected_analysis?.selection_sha256&&parity.selection===d.selection?.variant&&parity.validation_manifest_sha256===d.protocol?.manifests?.validation?.sha256;
    byId('api').textContent=health.training_active?'API inference paused for study preparation, training or testing.':health.model_load_verified?(verifiedParity?`API model loaded. Recorded original/selected parity passed: ${parity.api_requests} / ${parity.api_requests} requests on ${parity.validation_examples} validation crops.`:'API model loaded; parity verification is a separate check.'):'API responding; model has not been loaded or verified in this server session.';
    byId('failure').textContent=d.failure?JSON.stringify(d.failure,null,2):'No active coordinator failure. Earlier recovery evidence remains preserved in the run logs.';
  }catch(e){byId('state').textContent=e.message;byId('bar').removeAttribute('value')}
}
refresh();setInterval(refresh,5000);
