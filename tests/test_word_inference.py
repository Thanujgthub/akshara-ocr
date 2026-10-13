import unittest
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock
from ocr.word_inference import transcribe_word
from PIL import Image


def sample_image():
    image=Image.new('RGB',(80,40),'white');image.putpixel((40,20),(0,0,0));return image


class Row(list):
    def tolist(self): return list(self)


class Tensor:
    def __init__(self, rows): self.rows=rows;self.shape=(len(rows),len(rows[0]))
    def __getitem__(self, key):
        if isinstance(key,tuple):
            row,col=key
            if isinstance(row,int):return self.rows[row][col]
            return Tensor([r[col] for r in self.rows[row]])
        return Row(self.rows[key])


class Batch(dict):
    def to(self, device): return self


def backend(prefix_length=3,generated=None):
    processor=Mock();processor.return_value=Batch(input_ids=Tensor([[1]*prefix_length]))
    processor.apply_chat_template.return_value='exact template'
    processor.batch_decode.return_value=[' \nతెలుగు  \n']
    model=Mock();model.device=SimpleNamespace(type='cpu')
    model.generate.return_value=Tensor([[1]*prefix_length+(generated or [50,262146])])
    return SimpleNamespace(processor=processor,model=model,_torch=SimpleNamespace(inference_mode=nullcontext),eos_token_id=262146,pad_token_id=262144)


class WordInferenceTests(unittest.TestCase):
    def test_exact_raw_output_and_greedy_contract(self):
        b=backend();r=transcribe_word(b,sample_image(),'literal prompt')
        self.assertEqual(r['markdown'],' \nతెలుగు  \n')
        self.assertEqual(r['generated_token_ids'],[50,262146]);self.assertFalse(r['truncated'])
        b.processor.batch_decode.assert_called_once()
        self.assertEqual(b.processor.batch_decode.call_args.kwargs,{'skip_special_tokens':True,'clean_up_tokenization_spaces':False})
        kwargs=b.model.generate.call_args.kwargs
        for key,value in {'do_sample':False,'num_beams':1,'max_new_tokens':64,'eos_token_id':262146,'pad_token_id':262144,'use_cache':True}.items():
            self.assertEqual(kwargs[key],value)
        self.assertFalse(r['decoding']['whitespace_stripped'])

    def test_resource_abstention_does_not_generate(self):
        b=backend(prefix_length=1025);r=transcribe_word(b,sample_image(),'prompt')
        self.assertEqual(r['abstention'],'resource_token_budget');self.assertEqual(r['markdown'],'')
        b.model.generate.assert_not_called()

    def test_truncation_and_eos_distinct(self):
        for tokens,truncated in [([50,51],True),([50,262146],False)]:
            self.assertEqual(transcribe_word(backend(generated=tokens),sample_image(),'prompt',max_tokens=2)['truncated'],truncated)

    def test_invalid_processor_abstention(self):
        b=backend();b.processor.side_effect=ValueError('aspect ratio')
        self.assertEqual(transcribe_word(b,sample_image(),'prompt')['abstention'],'invalid_processor_input')
        b.model.generate.assert_not_called()

    def test_uniform_processed_image_abstains_before_tokenization(self):
        b=backend();r=transcribe_word(b,Image.new('RGB',(80,40),'white'),'prompt')
        self.assertEqual(r['abstention'],'uniform_pixels');b.processor.assert_not_called()
        b.model.generate.assert_not_called()


if __name__=='__main__':unittest.main()
