"""Literal word inference with the scale experiment's explicit decoding contract."""
import time
from .research_policy import quality, uniform_visible_input


def transcribe_word(backend, image, prompt, max_tokens=64):
    processor=backend.processor;torch=backend._torch
    image_quality=quality(image)
    if uniform_visible_input(image):
        return {'markdown':'','blocks':[],'abstention':'uniform_pixels','image_quality':image_quality,
                'generated_tokens':0,'truncated':False}
    text=processor.apply_chat_template(
        [{'role':'user','content':[{'type':'image'},{'type':'text','text':prompt}]}],
        add_generation_prompt=True,tokenize=False)
    try:
        inputs=processor(text=[text],images=[image],padding=True,return_tensors='pt').to(backend.model.device)
    except ValueError as error:
        return {'markdown':'','blocks':[],'abstention':'invalid_processor_input',
                'abstention_detail':str(error),'generated_tokens':0,'truncated':False,'image_quality':image_quality}
    prefix_length=inputs['input_ids'].shape[-1]
    if prefix_length>1024:
        return {'markdown':'','blocks':[],'abstention':'resource_token_budget','generated_tokens':0,'truncated':False,'image_quality':image_quality}
    gpu=backend.model.device.type=='cuda'
    if gpu:torch.cuda.synchronize()
    started=time.perf_counter()
    with torch.inference_mode():
        out=backend.model.generate(**inputs,max_new_tokens=max_tokens,do_sample=False,
            num_beams=1,use_cache=True,eos_token_id=backend.eos_token_id,pad_token_id=backend.pad_token_id)
    if gpu:torch.cuda.synchronize()
    generated=out[:,prefix_length:]
    raw=processor.batch_decode(generated,skip_special_tokens=True,clean_up_tokenization_spaces=False)[0]
    return {'markdown':raw,'blocks':[],'image_quality':image_quality,'generated_tokens':generated.shape[-1],
            'generated_token_ids':generated[0].tolist(),'latency_seconds':time.perf_counter()-started,
            'truncated':generated.shape[-1]>=max_tokens and int(generated[0,-1])!=backend.eos_token_id,
            'decoding':{'do_sample':False,'num_beams':1,'max_new_tokens':max_tokens,
                        'eos_token_id':backend.eos_token_id,'pad_token_id':backend.pad_token_id,
                        'clean_up_tokenization_spaces':False,'whitespace_stripped':False}}
