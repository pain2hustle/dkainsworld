# Crops the photo region out of Dylan's phone screenshots (drops status bar, viewer header "X / n of 9",
# black bars and the Android nav bar). Originals stay untouched; cropped copies go to assets/items/crop/.
import json,hashlib,sys
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;P=R/'public';OUT=P/'assets/items/crop';OUT.mkdir(parents=True,exist_ok=True)
def band(mask,minlen):
 best=(0,0);s=None
 for i,v in enumerate(list(mask)+[False]):
  if v and s is None:s=i
  if not v and s is not None:
   if i-s>best[1]-best[0]:best=(s,i)
   s=None
 return best if best[1]-best[0]>=minlen else None
MANUAL={'jack-stands-1.jpg':(0,205,955,1100),'pipe-wrenches-1.jpg':(0,250,955,1720)}
def crop_box(im,name):
 if name in MANUAL:return MANUAL[name]
 a=np.asarray(im.convert('L')).astype(np.float32);h,w=a.shape
 lit=(a>28).mean(1)>0.25           # bars are near pure black; photo rows are not
 ys=[y for y in range(300,1925) if lit[y]]
 y0,y1=ys[0],ys[-1]+1
 sub=a[y0:y1];colit=(sub>28).mean(0)>0.25;xs=np.where(colit)[0]
 return (int(xs[0]),y0+3,int(xs[-1])+1,y1-3)
rows=[]
SRC=R/'handoff/Images - 19 original item photos and 8 brand assets'
for f in sorted(f for f in SRC.glob('*.jpg') if f.stem.rsplit('-',1)[-1].isdigit() and not f.name.startswith(('empty','warehouse','platform','full','header','latest'))):
 if f.name.startswith('fb-'):continue
 im=Image.open(f);box=crop_box(im,f.name)
 if not box:print('NOCROP',f.name,im.size);box=(0,0)+im.size
 c=im.crop(box).convert("RGB");c.thumbnail((960,960),Image.LANCZOS);c.save(OUT/f.name,quality=80,optimize=True,progressive=True)
 rows.append({'original':'assets/items/'+f.name,'crop':'assets/items/crop/'+f.name,'box':list(map(int,box)),'size':list(c.size),'sha256':hashlib.sha256((OUT/f.name).read_bytes()).hexdigest()})
 print(f.name,im.size,'->',box,c.size)
(R/'private/owner-photo-crops.json').write_text(json.dumps(rows,indent=1),encoding='utf8')
