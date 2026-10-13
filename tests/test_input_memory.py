"""Keep supervised token semantics while releasing duplicate image buffers."""
import unittest
import weakref
from types import SimpleNamespace
from ocr.experiment import Experiment


class InputMemoryTests(unittest.TestCase):
    def test_prefix_buffer_released_and_verbatim_labels_preserved(self):
        import torch

        class Batch(dict):
            def to(self, device):
                return self

        class Processor:
            tokenizer=SimpleNamespace(eos_token='<eos>')
            prefix_ref=None

            def __call__(self, *, text, **kwargs):
                if self.prefix_ref is None:
                    result=Batch(input_ids=torch.tensor([[7,8,9]]), pixel_values=torch.ones(3))
                    self.prefix_ref=weakref.ref(result)
                    return result
                self_outer.assertIsNone(self.prefix_ref(), 'Prefix image batch remains live')
                self_outer.assertEqual(text, ['promptతెలుగు 123<eos>'])
                return Batch(input_ids=torch.tensor([[7,8,9,11,12]]), attention_mask=torch.ones(1,5,dtype=torch.long))

        self_outer=self
        exp=Experiment.__new__(Experiment)
        exp.torch=torch;exp.processor=Processor()
        exp.model=SimpleNamespace(device='cpu',config=SimpleNamespace(image_token_id=8,video_token_id=9))
        exp.image=lambda row: object()
        exp.prompt_text=lambda: 'prompt'
        batch=exp.inputs({'transcription_raw':'తెలుగు 123'},True)
        self.assertEqual(batch['input_ids'].tolist(),[[7,8,9,11,12]])
        self.assertEqual(batch['labels'].tolist(),[[-100,-100,-100,11,12]])
