from pathlib import Path
from PIL import Image
import json,hashlib

def apply(root,public,soup):
    proof=root/'private/header-cutout-provenance.json'
    assert proof.is_file(), 'Waiting for verified original-logo transparent cutout'
    meta=json.loads(proof.read_text(encoding='utf8'))
    image=public/meta['path']
    assert image.resolve().is_relative_to(public.resolve()) and image.suffix.lower()=='.png' and not image.is_symlink()
    assert hashlib.sha256(image.read_bytes()).hexdigest()==meta['sha256']
    with Image.open(image) as img:
        assert img.mode=='RGBA' and img.getchannel('A').getextrema()==(0,255), 'Expected actual transparent silhouette PNG'
        size=img.size
    node=soup.select_one('.brand-art img')
    node['src']='/'+meta['path'].lstrip('/')
    node['alt']='Original DKAINS WORLD globe, ring and plaque logo'
    node['width']=str(size[0]);node['height']=str(size[1])
    return (root/'header-cutout.css').read_text(encoding='utf8')
