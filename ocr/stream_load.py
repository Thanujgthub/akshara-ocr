"""Load the original safetensors one tensor at a time on memory-limited Windows.

No checkpoint conversion, quantization, or parameter substitution is performed.
"""
import json
import struct
from pathlib import Path

def load_model(checkpoint, device, dtype):
    import torch
    from accelerate import init_empty_weights
    from accelerate.utils import set_module_tensor_to_device
    from transformers import AutoConfig, AutoModelForImageTextToText
    checkpoint = Path(checkpoint)
    config = AutoConfig.from_pretrained(checkpoint, local_files_only=True)
    with init_empty_weights():
        model = AutoModelForImageTextToText.from_config(config, dtype=dtype, attn_implementation='sdpa')
    expected = dict(model.named_parameters())
    loaded = set()
    dtypes = {'BF16':torch.bfloat16,'F32':torch.float32,'F16':torch.float16,'I64':torch.int64}
    with (checkpoint/'model-00001-of-00001.safetensors').open('rb') as source:
        size = struct.unpack('<Q', source.read(8))[0]
        header = json.loads(source.read(size))
        for name, meta in header.items():
            if name == '__metadata__': continue
            if name not in expected: raise RuntimeError('Unexpected checkpoint parameter: '+name)
            if list(expected[name].shape) != meta['shape']: raise RuntimeError('Checkpoint shape mismatch: '+name)
            start, end = meta['data_offsets']
            source.seek(8+size+start)
            raw = bytearray(source.read(end-start))
            if len(raw) != end-start: raise RuntimeError('Truncated weight: '+name)
            value = torch.frombuffer(raw, dtype=dtypes[meta['dtype']]).reshape(meta['shape'])
            set_module_tensor_to_device(model, name, device, value=value, dtype=dtype)
            loaded.add(name)
            del value, raw
    missing=set(expected)-loaded
    if missing-{'lm_head.weight'}: raise RuntimeError('Missing checkpoint parameters: '+str(missing))
    if missing and not config.text_config.tie_word_embeddings: raise RuntimeError('Missing untied head')
    model.tie_weights()
    if any(p.is_meta for p in model.parameters()): raise RuntimeError('Unloaded meta parameter')
    for name, buffer in list(model.named_buffers()):
        if buffer.device.type != torch.device(device).type:
            set_module_tensor_to_device(model,name,device,value=buffer)
    model.eval()
    return model
