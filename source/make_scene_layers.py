# Splits the approved warehouse art into layers: empty warehouse (back) + platform cutout (front),
# using the pixel difference between the two approved, aligned renders. Originals are not modified.
import numpy as np,cv2,json,hashlib
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent;H=R/'handoff/Images - 19 original item photos and 8 brand assets';P=R/'public/assets';D=R/'private/layers'
a=np.asarray(Image.open(H/'empty-warehouse.jpg').convert('RGB')).astype(np.float32)
b=np.asarray(Image.open(H/'warehouse-with-platform.jpg').convert('RGB')).astype(np.float32)
diff=np.abs(a-b).sum(2);diff=cv2.GaussianBlur(diff,(0,0),3)
m=(diff>38).astype(np.uint8)*255
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((25,25),np.uint8))
n,lab,stats,_=cv2.connectedComponentsWithStats(m)
keep=np.zeros_like(m)
for i in range(1,n):
 x,y,w,h,area=stats[i]
 if area>20000:keep[lab==i]=255
# fill holes
ff=keep.copy();cv2.floodFill(ff,None,(0,0),255);keep=keep|cv2.bitwise_not(ff)
alpha=cv2.GaussianBlur(keep,(0,0),2.2)
Image.fromarray(keep).save(D/'platform-mask.png')
ys,xs=np.where(keep>0);print('bbox',xs.min(),ys.min(),xs.max(),ys.max())
x0,y0,x1,y1=max(xs.min()-8,0),max(ys.min()-8,0),min(xs.max()+8,2047),1117
rgba=np.dstack([b.astype(np.uint8),alpha])[y0:y1,x0:x1]
Image.fromarray(rgba,'RGBA').save(P/'scene-platform.webp',quality=88,method=6)
Image.open(H/'empty-warehouse.jpg').save(P/'scene-warehouse.webp',quality=84,method=6)
info={'platform_box':[int(x0),int(y0),int(x1),int(y1)],'canvas':[2048,1117]}
for f in ['scene-platform.webp','scene-warehouse.webp']:info[f]=hashlib.sha256((P/f).read_bytes()).hexdigest()
(D/'layers.json').write_text(json.dumps(info,indent=1));print(info)
prev=Image.new('RGB',(2048,1117),(255,0,255));prev.paste(Image.fromarray(rgba,'RGBA'),(int(x0),int(y0)),Image.fromarray(rgba,'RGBA'));prev.resize((1024,558)).save(D/'platform-check.jpg')
