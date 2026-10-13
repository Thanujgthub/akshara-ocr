"""Literal transcription and diagnostic flags. Never a spelling correction engine."""
import re
import unicodedata
from collections import Counter
import regex
from PIL import ImageFilter, ImageStat

TELUGU_PROMPT = (
    'Transcribe only the Telugu text visible in this image, in reading order. '
    'Return the transcription only, without explanations, Markdown or LaTeX wrappers. '
    'Preserve the exact spelling, punctuation, Telugu numerals and Arabic numerals as written. '
    'Do not translate, correct spelling, repeat words, or guess missing or unreadable characters. '
    'For an unreadable span write [అస్పష్టం]. If the image is completely blank, return an empty string.'
)

def uniform_visible_input(image):
    """Abstain on exactly constant RGB pixels; never infer hidden/unreadable text."""
    return all(low==high for low,high in image.convert('RGB').getextrema())

def quality(image):
    gray=image.convert('L')
    stat=ImageStat.Stat(gray)
    extrema=gray.getextrema()
    # Uniform pixels are an observable image property, not proof of absence of handwriting.
    return {'width':image.width,'height':image.height,'gray_std':stat.stddev[0],
            'edge_mean':ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).mean[0],
            'uniform_pixels':extrema[0]==extrema[1],
            'low_contrast':stat.stddev[0]<8,
            'small_height':image.height<24}

def image_token_budget(width,height,margin=0):
    """Mirror official area clamp + installed Qwen2VL processor's resize dimensions."""
    import math
    from transformers.models.qwen2_vl.image_processing_qwen2_vl import smart_resize
    width+=2*margin;height+=2*margin;area=width*height
    factor=math.sqrt(65536/area) if area<65536 else math.sqrt(2359296/area) if area>2359296 else 1
    width=max(1,round(width*factor));height=max(1,round(height*factor))
    h,w=smart_resize(height,width,factor=32,min_pixels=65536,max_pixels=16777216)
    return h*w//1024

def crop_review_reasons(row):
    reasons=[]
    if row['height']>300:reasons.append('large_crop_manual_label_alignment_review')
    if min(row['width'],row['height'])<8:reasons.append('tiny_crop_manual_review')
    try:
        if image_token_budget(row['width'],row['height'],4)>800:reasons.append('word_training_token_budget')
    except ValueError:reasons.append('processor_aspect_ratio_limit')
    return reasons

def flags(text, truncated=False, image_quality=None):
    letters=[c for c in text if unicodedata.category(c).startswith('L')]
    foreign=[c for c in letters if not '\u0c00'<=c<='\u0c7f']
    scripts=sorted({unicodedata.name(c,'UNKNOWN').split()[0] for c in foreign})
    words=text.split(); counts=Counter(words)
    refusal=bool(re.search(r'no\s+(?:text|transcription|math)|cannot\s+(?:read|transcribe)|unable\s+to',text,re.I))
    wrappers=bool(re.search(r'\$|```|<\s*/?\s*(?:table|tr|td)\b|\\(?:text|mathrm|begin)\b',text))
    uncertain='[అస్పష్టం]' in text or '\ufffd' in text
    repeat=any(n>=3 for w,n in counts.items() if len(w)>2)
    reasons=[]
    for ok,label in [(bool(foreign),'non_telugu_letters'),(refusal,'refusal'),(wrappers,'formatting_candidate'),
                     (repeat,'repetition_candidate'),(uncertain,'unreadable_marker'),(truncated,'truncated'),
                     (bool((image_quality or {}).get('uniform_pixels')),'uniform_image_review'),
                     (bool((image_quality or {}).get('low_contrast')),'low_contrast_review')]:
        if ok:reasons.append(label)
    return {'review_required':True,'uncertainty_flags':reasons,'foreign_scripts':scripts,
            'script_contamination':bool(foreign),'refusal':refusal,'malformed_output':wrappers or '\ufffd' in text,
            'repeat_candidate':repeat,'confidence':None,'confidence_calibrated':False}

def formatting_candidate(raw, verified_artifact=False):
    """Only remove a whole-output wrapper after human verification of the image.

    A delimiter may be real content. Never call this automatically for production or
    score cleaned text as raw. Return both versions with an explicit operation record.
    """
    if not verified_artifact:return {'raw':raw,'text':raw,'operations':[]}
    m=re.fullmatch(r'(\$\$|\$)([^$\\\n]+)\1',raw)
    if not m:return {'raw':raw,'text':raw,'operations':[]}
    return {'raw':raw,'text':m.group(2),'operations':['human_verified_outer_math_wrapper']}

def length_bin(text):
    n=len(regex.findall(r'\X',unicodedata.normalize('NFC',text)))
    return '1-3' if n<=3 else '4-6' if n<=6 else '7+'

def augment(image, rng):
    """One mild transform; never crop glyphs, relabel, or count it as a new example."""
    from PIL import ImageEnhance,Image
    choice=rng.choice(['none','blur','fade','skew','lighting','scale'])
    if choice=='blur':return image.filter(ImageFilter.GaussianBlur(rng.uniform(.15,.45)))
    if choice=='fade':return ImageEnhance.Contrast(image).enhance(rng.uniform(.8,.95))
    if choice=='skew':return image.rotate(rng.uniform(-1.5,1.5),resample=Image.Resampling.BICUBIC,expand=True,fillcolor='white')
    if choice=='lighting':
        mask=Image.linear_gradient('L').resize(image.size).point(lambda x:220+x*35/255).convert('RGB')
        from PIL import ImageChops
        return ImageChops.multiply(image,mask)
    if choice=='scale':
        factor=rng.uniform(.93,1.07)
        return image.resize((max(1,round(image.width*factor)),max(1,round(image.height*factor))),Image.Resampling.LANCZOS)
    return image
