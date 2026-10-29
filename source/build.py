from pathlib import Path
from bs4 import BeautifulSoup
import json,hashlib,shutil,csv,sys,html,cv2,numpy as np,zxingcpp
from PIL import Image
import marketplace_support as marketplace
import header_cutout_support
R=Path(__file__).resolve().parent;P=R/'public';E=html.escape
assetroot=Path(r'D:\AMH\DKAINSWORLD-Recovery\asset-source\dkainsworld');prov=json.loads((assetroot/'item-photo-provenance.json').read_text(encoding='utf8'))
for item in prov['assets']:
 src=assetroot/item['path'];assert hashlib.sha256(src.read_bytes()).hexdigest()==item['sha256'];dst=P/item['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
(R/'private/item-photo-provenance.json').write_text(json.dumps(prov,indent=2),encoding='utf8')
# Original item photo updates must be installed with verified provenance first.
extra_file=R/'private/photo-update-provenance.json'
assert extra_file.is_file(), 'Waiting for verified original 11-photo handoff'
extra=json.loads(extra_file.read_text(encoding='utf8'))
expected={'pipe-wrenches':3,'pick-your-tools':3,'dbz-orange-yellow':3,'kid-goku':2}
assert len(extra['assets'])==11
for ident,count in expected.items():
 assert sum(x['listing_id']==ident for x in extra['assets'])==count
# The 11 full screenshots stay in the handoff folder (hash-checked); the site serves only their cropped copies.
HANDOFF=R/'handoff/Images - 19 original item photos and 8 brand assets'
for x in extra['assets']:
 assert hashlib.sha256((HANDOFF/Path(x['path']).name).read_bytes()).hexdigest()==x['sha256']
 (P/x['path']).unlink(missing_ok=True)
for name in ['zelle.svg','venmo.svg','cashapp.svg']:shutil.copy2(Path(r'D:\AMH\CreatorReleases\DesignRepair\maria-reference\assets')/name,P/'assets'/name)
shutil.copy2(Path(r'D:\AMH\CreatorReleases\DesignRepair\source\creator-sites\adina-y-flores\site\assets\paypal-mark.svg'),P/'assets/paypal-mark.svg')
# Branded QR: error correction H (30%) so Dylan's logo can sit in the middle; must still decode with two readers.
qp=cv2.QRCodeEncoder_Params();qp.correction_level=cv2.QRCODE_ENCODER_CORRECT_LEVEL_H
qr=cv2.QRCodeEncoder_create(qp).encode('https://dkainsworld.pages.dev/');qr=np.pad(qr,4,constant_values=255);qr=cv2.resize(qr,None,fx=16,fy=16,interpolation=cv2.INTER_NEAREST)
qimg=Image.fromarray(qr).convert('RGB');qa=np.asarray(qimg).copy();qa[(qa[...,0]<128)]=(20,27,43);qimg=Image.fromarray(qa)
from PIL import ImageDraw
emb=Image.open(P/'assets/dkainsworld-emblem.webp').convert('RGBA');side=int(qimg.width*0.25);emb.thumbnail((side,side),Image.LANCZOS)
pad=int(side*0.12);bw,bh=emb.width+pad*2,emb.height+pad*2;box=Image.new('RGBA',(bw,bh),(0,0,0,0));ImageDraw.Draw(box).rounded_rectangle((0,0,bw-1,bh-1),radius=int(bw*.16),fill=(255,255,255,255))
box.alpha_composite(emb,(pad,pad));qimg=qimg.convert('RGBA');qimg.alpha_composite(box,((qimg.width-bw)//2,(qimg.height-bh)//2));qimg=qimg.convert('RGB');qimg.save(P/'assets/site-qr.png')
qr=np.asarray(qimg.convert('L'));decoded=zxingcpp.read_barcode(qr);assert decoded and decoded.text=='https://dkainsworld.pages.dev/'
assert cv2.QRCodeDetector().detectAndDecode(np.asarray(qimg))[0]=='https://dkainsworld.pages.dev/','OpenCV could not read the branded QR'
for sc in (0.35,0.2):
 small=qimg.resize((int(qimg.width*sc),)*2,Image.LANCZOS);d2=zxingcpp.read_barcode(np.asarray(small.convert('L')));assert d2 and d2.text=='https://dkainsworld.pages.dev/',f'QR unreadable at {sc}'
(R/'private/qr-check.json').write_text(json.dumps({'decoded':decoded.text,'format':str(decoded.format),'size':list(qr.shape),'passed':True},indent=2),encoding='utf8')
def item(id,title,cat,price,description,photos=None,brand='',model=''):
 return dict(id=id,title=title,category=cat,price_text=price,description=description,availability='Ask for current availability',condition='Ask Dylan for condition details',brand=brand,model=model,photos=photos or [])
seed=[
 item('jack-stands','Performance Tool W41022 jack stand pair','tools','Ask for prices','Pair pictured. Ask Dylan about condition and current price. Source screenshots may contain historical prices; those are not current asking prices.',[f'/assets/items/jack-stands-{i}.jpg' for i in [2,3,4,1]],'Performance Tool','W41022'),
 item('mixed-tools','Assorted wrenches & mixed tools','tools','Tools from $1 · ask for prices','Hundreds of assorted wrenches and sets, SAE and metric. Mixed brands made in USA, Japan and Taiwan. More stock than pictured; prices vary by item.',[f'/assets/items/mixed-tools-{i}.jpg' for i in range(1,5)]),
 item('pipe-wrenches','Pipe wrenches','tools','$15 each','Ask Dylan which pipe wrenches are available and about their size and condition.'),
 item('pick-your-tools','Assorted / pick-your-own tool sets','tools','$35 each','Contents vary. Talk to Dylan about putting together a set and confirm the included tools.'),
 item('sockets','Sockets','tools','Ask for prices','Ask about current sockets, drive sizes, SAE or metric options and condition.'),
 item('ratchets','Ratchets','tools','Ask for prices','Ask about available ratchets, brands, drive sizes and condition.'),
 item('extensions','Tool extensions','tools','Ask for prices','Ask Dylan about available extensions and the sizes you need.'),
 item('screwdrivers','Screwdrivers','tools','Ask for prices','Tell Dylan which screwdriver types and sizes you are looking for.'),
 item('handyman-tools','Handyman tools','tools','Ask for prices','A varied tool assortment. Call with the job or tool you have in mind.'),
 item('skateboards','Skateboards','boards','Ask for prices','Ask about the current boards, setup, dimensions and condition.'),
 item('longboards','Longboards','boards','Ask for prices','Check the available longboards and ask about their setup and condition.'),
 item('dressers','Dressers','furniture','Ask for prices','Ask for current photos, dimensions, condition and pickup arrangements.'),
 item('couches','Couches','furniture','Ask for prices','Ask for current photos, measurements, condition and pickup arrangements.'),
 item('mirrors','Mirrors','furniture','Ask for prices','Ask about current styles, sizes, condition and pickup arrangements.'),
 item('dbz-orange-yellow','Orange & yellow Dragon Ball Z bags','backpacks','$20 for both · $15 each','The orange and yellow bags are a separate listing from the blue/black Kid Goku backpack. Ask Dylan for current photos and condition.'),
 item('kid-goku','Blue/black Kid Goku backpack','backpacks','$30','Separate Kid Goku backpack listing. Ask for current photos and condition.'),
 item('flea-market','Flea market finds','finds','Ask for prices','Tell Dylan what you are looking for and find out what is in the mix.')]
fields=list(seed[0])+marketplace.FIELDS+['photoCredit'];inventory=R/'inventory.json';csvpath=R/'inventory.csv'
if '--from-csv' in sys.argv:
 with csvpath.open(encoding='utf-8-sig',newline='') as f:items=list(csv.DictReader(f))
 for it in items:it['photos']=[p.strip() for p in it['photos'].split(';') if p.strip()]
 inventory.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf8')
elif not inventory.exists():inventory.write_text(json.dumps(seed,ensure_ascii=False,indent=2),encoding='utf8')
items=json.loads(inventory.read_text(encoding='utf8'));assert len({i['id'] for i in items})==len(items)
for it in items:
 for field in marketplace.FIELDS+['photoCredit']:it.setdefault(field,'')
 marketplace.verified_url(it)
for ident,count in expected.items():
 it=next(x for x in items if x['id']==ident)
 it['photos']=['/'+x['path'].lstrip('/') for x in extra['assets'] if x['listing_id']==ident]
 assert len(it['photos'])==count
examples=json.loads((R/'private/example-photo-provenance.json').read_text(encoding='utf8'))
for x in examples['assets']:
 assert hashlib.sha256((P/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
 it=next(i for i in items if i['id']==x['listing_id']);it['photos']=['/'+x['path']];it['photoCredit']=x['credit']
fbprov=json.loads((R/'private/fb-listing-provenance.json').read_text(encoding='utf8'))
for x in fbprov['assets']:assert hashlib.sha256((P/x['path']).read_bytes()).hexdigest()==x['sha256'],x['path']
assert all(i['photos'] for i in items),'Every listing needs a photo'
crops={'/'+c['original']:c for c in json.loads((R/'private/owner-photo-crops.json').read_text(encoding='utf8'))}
for c in crops.values():assert hashlib.sha256((P/c['crop']).read_bytes()).hexdigest()==c['sha256'],c['crop']
for i in items:i['photos']=['/'+crops[x]['crop'] if x in crops else x for x in i['photos']]
inventory.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf8')

with csvpath.open('w',encoding='utf8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for it in items:w.writerow({**it,'photos':';'.join(it['photos'])})
shutil.copy2(inventory,P/'inventory.json');shutil.copy2(csvpath,P/'inventory.csv')
s=BeautifulSoup((Path(r'D:\AMH\DKAINSWORLD\public\index.html')).read_text(encoding='utf8'),'html.parser')
def fragment(text):return BeautifulSoup(text,'html.parser')
def replace(n,text):n.replace_with(fragment(text))
def fill(n,text):n.clear();n.extend(fragment(text).contents)
# Preserve all original artwork bytes and the established page layout.
fill(s.select_one('.hero-actions'),'<a class="button button-primary" href="#browse">Browse Items <span aria-hidden="true">↗</span></a><button class="button button-outline" type="button" data-qr>Show Site QR</button>')
s.select_one('.tiny-star').string='✦'
for n in s.select('.category-strip b'):n.string='✦'
s.select_one('#browse-title').string='Browse the current mix.'
s.select_one('.section-heading>p').string='Real photos and asking prices from Dylan, plus his Facebook listings. Call Dylan to confirm the details.'
s.select_one('label[for=search]').string='Search items'
s.select_one('#search')['placeholder']='Try wrenches, couches, DBZ…';s.select_one('#search')['aria-controls']='inventory-grid'
s.select_one('#result-count').string=f'{len(items)} listings to explore'
for b in s.select('[data-filter]'):
 if b['data-filter']=='all':b.string='All items'
icons={c['data-category']:str(c.select_one('.card-art svg')) for c in s.select('.category-card')}
newcards=[]
for it in items:
 img=it['photos'][0] if it['photos'] else None
 if img:
  n=len(it['photos']);example=bool(it['photoCredit']);fb=it['platform']=='facebook-marketplace'
  alt=f'Photo from Dylan’s Facebook listing: {it["title"]}' if fb else it['title']
  tag='<b class="photo-tag photo-fb">On Facebook</b>' if fb else ''
  label=('View photo' if n==1 else f'View {n} photos')
  art=f'<button type="button" class="item-photo" data-gallery="{E(it["id"])}" aria-label="{label} of {E(it["title"])}"><img src="{E(img)}" alt="{E(alt)}" loading="lazy" width="955" height="2048">{tag}<span>{label}</span></button>'
 else:art=f'<div class="card-art unpictured" aria-hidden="true">{icons[it["category"]]}<span class="art-label">ASK DYLAN FOR PHOTOS</span></div>'
 search=' '.join(str(it[k]) for k in ['title','description','brand','model','price_text']) + ' ' + {'backpacks':'dbz dragon ball z bags backpacks','furniture':'','boards':'skateboards longboards skate boards long boards'}.get(it['category'],'') + (' jackstands jack stands' if it['id']=='jack-stands' else '') + (' sofa sofas' if it['id']=='couches' else '')
 newcards.append(f'<article class="category-card item-card {dict(tools="gold",boards="blue",furniture="lavender",backpacks="coral",finds="mint")[it["category"]]}" id="item-{E(it["id"])}" data-category="{it["category"]}" data-search="{E(search,quote=True)}">{art}<div class="card-body"><p class="eyebrow">{E(it["category"].upper())}</p><h3>{E(it["title"])}</h3><p class="asking-price">{E(it["price_text"])}</p><p>{E(it["description"])}</p><p class="availability">{E(it["availability"])}</p><div class="card-links"><a class="card-link" href="tel:+15104350747" aria-label="Ask Dylan about {E(it["title"],quote=True)}">Ask Dylan <span aria-hidden="true">↗</span></a>'+(f'<a class="card-fb-link" href="{E(it["sourceUrl"])}" target="_blank" rel="noopener noreferrer"><span class="facebook-mark" aria-hidden="true">f</span>View on Facebook</a>' if marketplace.verified_url(it) else '')+'</div></div></article>')
s.select_one('#category-grid')['id']='inventory-grid';fill(s.select_one('#inventory-grid'),''.join(newcards))
# Phone: item list is its own swipe window; easy jump to first / last item.
s.select_one('#inventory-grid').insert_before(fragment('<div class="list-jump" aria-label="Item list controls"><button type="button" data-jump="top" aria-label="First item">↑ First</button><span id="list-pos" aria-live="polite"></span><button type="button" data-jump="bottom" aria-label="Last item">↓ Last</button></div>'))
s.select_one('#empty-state h3').string='No items match that search.';s.select_one('#reset-search').string='Show all items';s.select_one('#empty-state p').string='Try tools, furniture, or ask Dylan about what you need.'
fill(s.select_one('.listing-note>div'),'<h3>Before you come by</h3><p>Call or text Dylan to confirm the item, price and pickup.</p>')
s.select_one('.listing-note').insert(0,fragment('<img class="note-logo" src="/assets/dkainsworld-emblem.webp" width="1100" height="760" alt="" loading="lazy">'))
CATNAME={'tools':'Tools','boards':'Boards','furniture':'Furniture','backpacks':'Backpacks','finds':'Finds'}
rows=''.join(f'<li><a href="#item-{E(it["id"])}"><img src="{E(it["photos"][0])}" alt="" width="56" height="56" loading="lazy"><span class="pl-name">{E(it["title"])}<small>{CATNAME[it["category"]]}{" · Facebook" if it["platform"]=="facebook-marketplace" else ""}</small></span><b>{E(it["price_text"])}</b><i aria-hidden="true">›</i></a></li>' for it in items)
credits=''.join(f'<li>{E(it["title"])}: {it["photoCredit"]}</li>' for it in items if it['photoCredit'])
s.select_one('#browse').insert_after(fragment(f'<section class="price-list section-wrap" id="price-list" aria-labelledby="price-list-title"><p class="eyebrow">QUICK LOOK</p><h2 id="price-list-title">Every item and price</h2><p>Tap an item to jump to its card. Call Dylan to confirm before you come by.</p><div class="pl-panel"><div class="pl-head"><span>{len(items)} items</span><span>Price</span></div><ul>{rows}</ul></div></section>'))
pass  # credits page removed at owner request; credit-requiring photos replaced with generated ones
s.select_one('.steps h3').string='Find your item'
# Steps as dark bordered cards with icon tiles (owner-requested, Lanna Thai card style); footer = owner's space art.
ICON={'find':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></svg>',
 'look':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 8h3l1.6-2.2h6.8L17 8h3v11H4z"/><circle cx="12" cy="13.2" r="3.4"/></svg>',
 'visit':'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-6.5-6-6.5-11a6.5 6.5 0 0 1 13 0c0 5-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/></svg>'}
steps=[('find','STEP 01','Find your item','Search the mix for the things you need or the things you love.'),
 ('look','STEP 02','Get the full picture','Ask Dylan for photos, size, condition and price. Check what’s available.'),
 ('visit','STEP 03','Plan your visit','Confirm the details and pickup, then open the map when you’re ready.')]
STEP_GO={'find':'#browse','look':'#request-item','visit':'#contact'}
fill(s.select_one('.steps'),''.join(f'<li class="step-card{" step-card-hot" if k=="visit" else ""}"><a class="step-link" href="{STEP_GO[k]}" data-step="{k}"><span class="step-icon">{ICON[k]}</span><div><small>{n}</small><h3>{E(t)}</h3><p>{E(d)}</p></div><i class="step-go" aria-hidden="true">›</i></a></li>' for k,n,t,d in steps))
s.select_one('.how-section')['data-cards']=''
s.select_one('.how-intro').insert(0,fragment('<img class="how-brand" src="/assets/dkainsworld-emblem.webp" width="1100" height="760" loading="lazy" alt="DKAINSWORLD">'))
# Footer globe = Austin's own artificialmindhive.com globe code, copied byte-for-byte (no remake): amh-hive/space.
SPACE=Path(r'C:\Users\Servi\code\amh-hive\space')
space_files=['space-kit.js','vendor/three.module.js','vendor/three.core.js','vendor/LICENSE.txt','earth-day.webp','earth-lights.webp','earth-spec.webp','earth-clouds.webp']
for f in space_files:
 d=P/'space'/f;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SPACE/f,d);assert hashlib.sha256(d.read_bytes()).hexdigest()==hashlib.sha256((SPACE/f).read_bytes()).hexdigest()
(R/'private/globe-source.json').write_text(json.dumps({'source':str(SPACE),'files':{f:hashlib.sha256((SPACE/f).read_bytes()).hexdigest() for f in space_files}},indent=1),encoding='utf8')
art=s.select_one('.footer-art');art['data-globe']='';fill(art,'<img class="footer-emblem" src="/assets/dkainsworld-emblem.webp" width="1100" height="760" loading="lazy" alt="DKAINSWORLD"><div class="footer-globe" data-space-globe data-base="/space/" data-rocks="0" data-fill=".86" data-fill-phone=".86" aria-hidden="true"></div>')
s.body.append(fragment('<script type="module" src="/space/space-kit.js"></script>'))
# Punch easter egg (owner's clip, UFC logo covered with Dylan's, UFC text cropped): 3 s after load, once per session.
shutil.copy2(R/'punch-egg.js',P/'punch-egg.js');assert (P/'assets/punch.mp4').is_file(),'missing punch clip';(P/'assets/punch.webm').unlink(missing_ok=True)
s.body.append(fragment('<script src="/punch-egg.js" defer></script>'))
s.select_one('.footer-copy>a').string='Dylan · (510) 435-0747';s.select_one('.footer-copy small').string='© 2026 DKAINSWORLD';s.select_one('.back-top').string='Back to top ↑'
s.select_one('.bottom-nav a span').string='Browse Items'
# Exact official platform homepages only, never guessed payment recipient paths.
# Zelle recipient = Dylan's phone number (owner-confirmed 2026-10-29); tap copies it. Others: homepages until handles arrive. No Venmo.
EMAIL='dkain1017dk@gmail.com'
# Payment buttons: tap one -> popup with that method's details + copy buttons (owner-confirmed handles 2026-10-29).
PAY={'zelle':('Zelle','zelle.svg',[('Phone','(510) 435-0747','5104350747'),('Email',EMAIL,EMAIL)],'Send in your bank app with Zelle to either one.'),
 'cashapp':('Cash App','cashapp.svg',[('Email',EMAIL,EMAIL)],'Send in Cash App to this email.'),
 'paypal':('PayPal','paypal-mark.svg',[('Email',EMAIL,EMAIL)],'Send in PayPal to this email.'),
 'chime':('Chime','',[('Text Dylan for his Chime info','(510) 435-0747','5104350747')],'Dylan takes Chime. Ask him for his Chime details.')}
def payicon(icon):return f'<img src="/assets/{icon}" alt="" width="28" height="28">' if icon else '<span class="pay-mark">C</span>'
payments=''.join(f'<button type="button" class="pay-chip pay-{k}" data-pay="{k}">{payicon(ic)}<span>{n}</span></button>' for k,(n,ic,_,_) in PAY.items())
paypanels=''.join(f'<div class="pay-panel" data-pay-panel="{k}" hidden><div class="pay-panel-head">{payicon(ic)}<h3>{n}</h3></div><p>{note}</p>'+''.join(f'<button type="button" class="pay-copy" data-copy="{c}" data-copy-idle="Tap to copy"><span>{lab}</span><b>{E(v)}</b><small data-copy-label>Tap to copy</small></button>' for lab,v,c in rows)+'</div>' for k,(n,ic,rows,note) in PAY.items())
paydialog=f'<dialog id="pay-dialog" class="pay-dialog" aria-labelledby="pay-title"><div class="modal-heading"><h2 id="pay-title">Pay Dylan</h2><button type="button" class="close-modal" data-close="pay-dialog" aria-label="Close payment details">×</button></div>{paypanels}<p class="pay-warn">Confirm the item and price with Dylan before you pay. All items are sold as-is.</p></dialog>'
platforms=[1,2]
paymentsection=f'<section class="payments-section section-wrap" id="payment-options"><p class="eyebrow">PLAN WITH DYLAN</p><h2>Paying Dylan</h2><p>Tap how you want to pay to see Dylan’s details.</p><div class="payment-grid pay-chips">{payments}</div></section>'
s.select_one('#contact').insert_after(fragment(paymentsection))
menu_button=s.new_tag('button',id='menu-open',type='button');menu_button['class']='menu-toggle';menu_button['aria-label']='Open menu';menu_button['aria-expanded']='false';menu_button['aria-controls']='site-menu';menu_button.string='☰';s.select_one('header').append(menu_button)
modal=f'''<dialog id="site-menu" class="site-menu" aria-labelledby="menu-title"><div class="modal-heading"><h2 id="menu-title">DKAINSWORLD</h2><button type="button" class="close-modal" data-close="site-menu" aria-label="Close menu">×</button></div><button class="menu-qr" type="button" data-qr><img src="/assets/site-qr.png" width="80" height="80" alt=""><span>Show Site QR Code<small>Share dkainsworld.pages.dev</small></span></button><nav aria-label="Expanded navigation"><a href="#browse">Browse Items</a><a href="#categories">Categories</a><a href="#payment-options">Payment platforms</a><a href="tel:+15104350747">Call Dylan · (510) 435-0747</a><a href="https://maps.app.goo.gl/Nu84KZXRDFjCbwpp7?g_st=ac" target="_blank" rel="noopener noreferrer">Directions ↗</a></nav><div class="payment-grid">{payments}</div><p class="payment-note">Tap a payment to see Dylan’s details.</p></dialog>
<dialog id="qr-dialog" class="qr-dialog" aria-labelledby="qr-title"><div class="modal-heading"><h2 id="qr-title">Take DKAINSWORLD with you.</h2><button type="button" class="close-modal" data-close="qr-dialog" aria-label="Close QR code">×</button></div><img src="/assets/site-qr.png" width="444" height="444" alt="QR code for https://dkainsworld.pages.dev/"><p>Scan to open the site.</p><a class="qr-url" href="https://dkainsworld.pages.dev/">dkainsworld.pages.dev</a><a class="button button-dark" href="/assets/site-qr.png" download="DKAINSWORLD-QR.png">Save QR image</a></dialog>
<dialog id="gallery-dialog" class="gallery-dialog" aria-labelledby="gallery-title"><div class="modal-heading"><h2 id="gallery-title">Item photos</h2><button type="button" class="close-modal" data-close="gallery-dialog" aria-label="Close photos">×</button></div><div class="gallery-stage"><button class="gallery-arrow" type="button" id="photo-prev" aria-label="Previous photo">‹</button><img id="gallery-image" src="/assets/items/crop/jack-stands-2.jpg" alt="Jack stand pair"><button class="gallery-arrow" type="button" id="photo-next" aria-label="Next photo">›</button></div><div class="gallery-controls"><p id="photo-count" aria-live="polite"></p></div><p class="source-note"></p></dialog>'''
s.body.append(fragment(modal))
s.body.append(fragment(paydialog))
s.body.append(fragment('<dialog id="terms-dialog" class="terms-dialog" aria-labelledby="terms-title"><div class="modal-heading"><h2 id="terms-title">Terms &amp; privacy</h2><button type="button" class="close-modal" data-close="terms-dialog" aria-label="Close terms">×</button></div><div class="terms-body">\n<h3>Buying from DKAINSWORLD</h3><ul>\n<li>Items are secondhand. Prices on this site are Dylan’s asking prices and can change. Call or text Dylan to confirm price, condition and availability before you come by.</li>\n<li>Photos show the item or the type of item. Ask Dylan for current photos of the exact piece.</li>\n<li>Pickup, holds and payment are arranged directly with Dylan.</li>\n<li><b>All items are sold as-is.</b> Please inspect the item before you pay. Paying means you accept the item as-is, and it is yours.</li><li>Problem with your item? Contact Dylan within 1 hour of buying. All sales are final.</li><li>Store credit may be possible if you reach out the same day and the item is unused and in the same working condition. This is not guaranteed; it is up to Dylan.</li></ul>\n<h3>Payments</h3><ul>\n<li>Dylan takes Zelle, Cash App, PayPal and Chime.</li>\n<li>Zelle: (510) 435-0747 or dkain1017dk@gmail.com. Cash App and PayPal: dkain1017dk@gmail.com. Ask Dylan for his Chime info.</li>\n<li>Confirm the item and price with Dylan before sending money. Double-check the name before you send.</li></ul>\n<h3>Privacy</h3><ul>\n<li>This site has no accounts and no sign-up, and it does not save what you type. “Request an item” only opens your own messages app with the text filled in.</li>\n<li>Call, text, email, map and Facebook links open those apps or sites, which have their own privacy rules.</li></ul>\n<p class="terms-note">DKAINSWORLD · Fremont, CA · Updated October 2026</p></div></dialog>'))
fill(s.select_one('.hero-actions'),'<a class="button button-primary" href="#browse">Browse Items <span aria-hidden="true">↗</span></a><a class="button button-outline" href="tel:+15104350747">Call Dylan</a><a class="button button-outline button-text" href="sms:+15104350747">Text Dylan</a><a class="button button-outline" href="https://maps.app.goo.gl/Nu84KZXRDFjCbwpp7?g_st=ac" target="_blank" rel="noopener noreferrer">Directions</a><button class="button button-outline" data-qr type="button">QR Code</button>')
s.select_one('.tiny-star')['aria-hidden']='true'
# Browser UI colours match the site (Chrome, Samsung Internet, Edge/Bing, Safari; Firefox Android ignores theme-color).
for m in s.select('meta[name=theme-color]'):m.decompose()
s.head.append(fragment('<meta name="theme-color" content="#141b2b"><meta name="color-scheme" content="dark light"><meta name="msapplication-navbutton-color" content="#141b2b"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'))
# Branded menu: Dylan's logo as the title.
fill(s.select_one('#menu-title'),'<img class="menu-logo" src="/assets/dkainsworld-emblem.webp" width="1100" height="760" alt="DKAINSWORLD">')
# Text Dylan: opens the visitor's messaging app (top, contact, footer, menu, bottom nav).
SMS='sms:+15104350747'
CHAT='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/></svg>'
s.select_one('.contact-actions a[href^="tel:"]').insert_after(fragment(f'<a class="button button-outline button-text" href="{SMS}">{CHAT} Text Dylan</a>'))
MAIL_SVG='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6.5 8.5 6 8.5-6"/></svg>'
s.select_one('.contact-actions a.button-text').insert_after(fragment(f'<a class="button button-outline button-email" href="mailto:dkain1017dk@gmail.com?subject=DKAINSWORLD%20question&amp;body=Hi%20Dylan%2C%0A%0A">{MAIL_SVG} Email Dylan</a>'))
s.select_one('.footer-copy>a').insert_after(fragment(f'<a class="footer-text" href="{SMS}">Text Dylan</a>'))
s.select_one('.contact-actions span').insert_before(marketplace.store_link(s))
# Request an item: builds a prefilled text to Dylan (nothing is stored or sent by the site).
s.select_one('#contact>div').append(fragment('<form class="request-form" id="request-item" novalidate><img class="req-logo" src="/assets/dkainsworld-emblem.webp" width="1100" height="760" alt="" loading="lazy"><h3>Request an item</h3><label for="req-what">What are you looking for?</label><input id="req-what" name="what" type="text" maxlength="140" placeholder="e.g. 3/8 socket set, a dresser, DBZ bag" required><label for="req-budget">Budget (optional)</label><input id="req-budget" name="budget" type="text" maxlength="40" placeholder="e.g. $40"><a class="button button-primary req-send" href="sms:+15104350747">Text my request to Dylan</a><p class="req-note">Opens your messages app with the request filled in. Nothing is saved on this site.</p></form>'))
# Facebook dock above the bottom nav (shows after the hero), and footer legal line low in the grass.
# (Owner removed the always-on Facebook dock 2026-10-29; Facebook stays in hero, listings, contact, menu, footer.)
s.select_one('#site-menu nav a[href^="tel:"]').insert_after(fragment(f'<a href="{SMS}">Text Dylan · (510) 435-0747</a>'))
s.select_one('.bottom-nav a[href^="tel:"]').insert_after(fragment(f'<a href="{SMS}">{CHAT}<span>Text Dylan</span></a>'))
s.select_one('#site-menu nav a[href^="sms:"]').insert_after(fragment('<a href="#request-item">Request an item</a>'))
s.select_one('#site-menu nav').append(fragment('<button type="button" class="menu-terms" data-terms>Terms &amp; privacy</button>'))
# Email Dylan (owner-supplied address 2026-10-29), under Text Dylan in the menu.
s.select_one('#site-menu nav a[href^="sms:"]').insert_after(fragment('<a href="mailto:dkain1017dk@gmail.com?subject=DKAINSWORLD%20question">Email Dylan · dkain1017dk@gmail.com</a>'))
s.select_one('.desktop-nav .nav-phone').insert_before(fragment('<a href="#request-item">Request an item</a>'))
s.select_one('.footer-text').insert_after(fragment('<a class="footer-text" href="#request-item">Request an item</a>'))
s.select_one('.footer-copy a[href="#request-item"]').insert_after(fragment('<button type="button" class="footer-qr" data-qr>Show Site QR Code</button>'))
s.select_one('.back-top').insert_after(fragment('<a class="peak-title" href="https://www.ebparks.org/parks/mission-peak" target="_blank" rel="noopener noreferrer" aria-label="Mission Peak Regional Preserve, Fremont, California, 2,517 feet above sea level. Opens the East Bay Regional Park District page."><small><span class="tiny-star peak-star" aria-hidden="true">✦</span>Fremont, CA</small><strong>Mission Peak <i aria-hidden="true">↗</i></strong><span>2,517 ft (767 m) above sea level</span><em>Secondhand. First choice.</em></a>'))
s.select_one('.footer-copy').insert(0,fragment('<img class="footer-card-logo" src="/assets/dkainsworld-emblem.webp" width="1100" height="760" alt="" loading="lazy">'))
s.select_one('.footer-copy').append(fragment('<a class="footer-email" href="mailto:dkain1017dk@gmail.com?subject=DKAINSWORLD%20question&amp;body=Hi%20Dylan%2C%0A%0A">✉ dkain1017dk@gmail.com</a>'))
marketplace.decorate(s,items)
s.select_one('.section-heading .fb-store-link').decompose()  # owner: no double FB button under the hero
# Green strip: scrolling list of Dylan's real items (+ flea-market types -> his Flea market finds listing); tap opens that item.
STRIP=[('jack-stands','Jack stands'),('mixed-tools','Wrenches & tools'),('pipe-wrenches','Pipe wrenches'),('pick-your-tools','Tool sets'),('sockets','Sockets'),('ratchets','Ratchets'),('extensions','Extensions'),('screwdrivers','Screwdrivers'),('handyman-tools','Handyman tools'),('fb-milwaukee-toolbox','Milwaukee tool box'),('skateboards','Skateboards'),('longboards','Longboards'),('dressers','Dressers'),('couches','Couches'),('mirrors','Mirrors'),('dbz-orange-yellow','DBZ bags'),('kid-goku','Kid Goku backpack'),('fb-mustang-sunshade','Car sunshade'),('fb-cobra-cctv','Security cameras'),('flea-market','Flea market finds'),('flea-market','Vintage'),('flea-market','Collectibles'),('flea-market','Home goods')]
_ids={i['id'] for i in items};assert all(k in _ids for k,_ in STRIP),'strip item missing'
def _strip(hidden):return ''.join(f'<button type="button" class="strip-item" data-gallery="{k}"'+(' tabindex="-1"' if hidden else '')+f'>{E(t)}</button><b aria-hidden="true">✦</b>' for k,t in STRIP)
_st=s.select_one('.category-strip');_st['aria-label']='Items Dylan has';_st.name='nav'
fill(_st,f'<div class="strip-track"><div class="strip-set">{_strip(False)}</div><div class="strip-set" aria-hidden="true">{_strip(True)}</div></div>')
legal=s.new_tag('div');legal['class']='footer-legal'
legal.append(s.select_one('.footer-copy small').extract());legal.append(s.select_one('.footer-copy .fb-store-link').extract())
s.select_one('.site-footer').append(legal)
(P/'credits.html').unlink(missing_ok=True)
legal.append(fragment('<button type="button" class="terms-link" data-terms>Terms &amp; privacy</button>'))
credit_txt='; '.join(f'{E(i["title"])}: {i["photoCredit"]}' for i in items if i['photoCredit'])
legal.append(fragment(f'<button type="button" class="credits-tip" aria-expanded="false" aria-controls="credits-box">Photo credits</button><div class="credits-box" id="credits-box" role="note" hidden>Some listing photos via Wikimedia Commons. {credit_txt}</div>'))
# Austin's bee-facts box (from his poem page) above the footer; mini version at the bottom of the menu.
import extra_facts as _xf
_bees=fragment((R/'private/bees/bees-dk.html').read_text(encoding='utf8'))
for _li in _bees.select('#blist li'):
 if _li.find('b'):_li['data-titled']='1'
 if not _li.find('b'):
  _txt=_li.get_text(' ',strip=True);_li.clear();_li.append(fragment(f'<span>{E(_txt)}</span>'))
_bl=_bees.select_one('#blist')
# (Owner: keep every fact — no de-duplication.)
for _cat,_rows in (('Human story',_xf.HUMANS),('Trade through time',_xf.PERIODS),('China',_xf.CHINA),('Greece',_xf.GREECE),('Asia',_xf.ASIA),('What they ate',_xf.FOOD)):
 for _t,_d,_u in _rows:_bl.append(fragment(f'<li data-s="dk" data-category="{_cat}"><b>{E(_t)}</b> <span>{E(_d)}</span>'+(f' <a class="fact-source" href="{E(_u)}" target="_blank" rel="noopener">Source · {_cat}</a>' if _u.startswith('https://') else '')+'</li>'))
_bees.select_one('.btitle b').string='A LITTLE BUZZ FROM APIARY'
s.select_one('.site-footer').insert_before(fragment('<div class="bees-wrap">'+str(_bees)+'</div>'))
s.select_one('#site-menu').append(fragment('<button type="button" class="bmini" id="bmini"><img src="/assets/apiary-logo.png" alt="" width="22" height="22"><span><small>A LITTLE BUZZ FROM APIARY</small><span class="bmini-fact"><b>Bee facts</b></span></span></button>'))
shutil.copy2(R/'bees-dk.js',P/'bees-dk.js');shutil.copy2(R/'private/bees/apiary-logo.png',P/'assets/apiary-logo.png')
s.body.append(fragment('<script src="/bees-dk.js" defer></script>'))
shutil.copy2(R/'private/amh-ufo-logo.svg',P/'assets/amh-ufo-logo.svg')
s.select_one('.site-footer').append(fragment('<div class="amh-credit"><a href="https://artificialmindhive.com/" target="_blank" rel="noreferrer"><img src="/assets/amh-ufo-logo.svg" alt="Artificial Mind Hive UFO logo" width="64" height="64" loading="lazy"><span><small>Website built by</small><strong>Artificial Mind Hive</strong></span><strong>Visit AMH ↗</strong></a></div>'))
_ct=s.select_one('.credits-tip');s.select_one('.amh-credit').append(_ct.extract())  # tiny label under the AMH bar (no extra space)
# Layered landing scene: approved warehouse backdrop + Blender orbit loop (screen-blended) + approved floating emblem.
scene_proof=json.loads((R/'private/scene-asset-provenance.json').read_text(encoding='utf8'))
for rel,meta in scene_proof['derived'].items():assert hashlib.sha256((P/rel).read_bytes()).hexdigest()==meta['sha256'],rel
layers=json.loads((R/'private/layers/layers.json').read_text(encoding='utf8'))
stages=json.loads((R/'private/build-frames/stages.json').read_text(encoding='utf8'))
(P/'assets/emblem-stage2-ring.webp').unlink(missing_ok=True)
for k,v in {k:v for k,v in stages['files'].items() if k in('stage1-plaque','stage3-globe')}.items():assert hashlib.sha256((P/'assets'/f'emblem-{k}.webp').read_bytes()).hexdigest()==v,k
for rel in ['scene-platform.webp','scene-warehouse.webp','scene-warehouse-tall.webp']:assert hashlib.sha256((P/'assets'/rel).read_bytes()).hexdigest()==layers[rel],rel
for rel in ['assets/orbit-loop.mp4','assets/orbit-loop.webm']:(P/rel).unlink(missing_ok=True)
s.select_one('.hero')['data-layered-scene']=''
replace(s.select_one('.hero-art'),'<div class="hero-scene" aria-hidden="true"><picture><source media="(max-width:800px)" srcset="/assets/scene-warehouse-tall.webp" width="1024" height="1536"><img class="hero-scene-backdrop" src="/assets/scene-warehouse.webp" alt="" width="2048" height="1117" fetchpriority="high"></picture><div class="hero-orbit"><img class="hero-scene-platform" src="/assets/scene-platform.webp" alt="" width="1229" height="350"><img class="hero-stage hero-stage3" src="/assets/emblem-stage3-globe.webp" alt="" width="1100" height="760"><img class="hero-stage hero-stage1" src="/assets/emblem-stage1-plaque.webp" alt="" width="1100" height="760"><span class="hero-flash"></span><img class="hero-scene-emblem" src="/assets/dkainsworld-emblem.webp" alt="" width="1100" height="'+str(scene_proof['derived']['assets/dkainsworld-emblem.webp']['size'][1])+'"></div></div>')
header_css=header_cutout_support.apply(R,P,s)
header_css+='\n'+(R/'scene-v3.css').read_text(encoding='utf8')
(P/'index.html').write_text(str(s),encoding='utf8')
app=Path(r'D:\AMH\DKAINSWORLD\public\app.js').read_text(encoding='utf8').replace("' category' : ' categories'","' listing' : ' listings'")
app += '\nconst INVENTORY = '+json.dumps(items,ensure_ascii=False)+';\n'
app += r'''
const menuDialog=document.querySelector('#site-menu'),menuOpen=document.querySelector('#menu-open');
const qrDialog=document.querySelector('#qr-dialog'),galleryDialog=document.querySelector('#gallery-dialog');
let qrTrigger=null,photoTrigger=null,photos=[],photoIndex=0,photoTitle='';
menuOpen.addEventListener('click',()=>{menuDialog.showModal();menuOpen.setAttribute('aria-expanded','true');menuDialog.querySelector('[data-qr]').focus()});
menuDialog.addEventListener('close',()=>{menuOpen.setAttribute('aria-expanded','false');if(!qrDialog.open)menuOpen.focus()});
menuDialog.querySelectorAll('nav a').forEach(a=>a.addEventListener('click',()=>menuDialog.close()));
document.querySelectorAll('[data-close]').forEach(b=>b.addEventListener('click',()=>document.getElementById(b.dataset.close).close()));
[menuDialog,qrDialog,galleryDialog].forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close()}}));
document.querySelectorAll('[data-qr]').forEach(b=>b.addEventListener('click',()=>{qrTrigger=b.closest('#site-menu')?menuOpen:b;if(menuDialog.open)menuDialog.close();qrDialog.showModal();qrDialog.querySelector('[data-close]').focus()}));
qrDialog.addEventListener('close',()=>qrTrigger?.focus());
function showPhoto(){const has=photos.length>0;document.querySelector('#gallery-image').hidden=!has;galleryDialog.querySelector('.gallery-controls').hidden=!has;if(!has)return;document.querySelector('#gallery-image').src=photos[photoIndex];document.querySelector('#gallery-image').alt=photoTitle+' — photo '+(photoIndex+1);document.querySelector('#photo-count').textContent=(photoIndex+1)+' of '+photos.length;}
document.querySelectorAll('[data-gallery]').forEach(b=>b.addEventListener('click',()=>{const it=INVENTORY.find(x=>x.id===b.dataset.gallery);if(!it)return;photos=it.photos;photoIndex=0;photoTitle=it.title;photoTrigger=b;updateItemDetails(it);document.querySelector('#gallery-title').textContent=it.title;showPhoto();galleryDialog.showModal();galleryDialog.querySelector('[data-close]').focus()}));
function galleryItems(){return [...document.querySelectorAll('.item-card:not([hidden]) [data-gallery]')]}
function openItem(btn,last){const it=INVENTORY.find(x=>x.id===btn.dataset.gallery);if(!it)return;photos=it.photos;photoIndex=last?photos.length-1:0;photoTitle=it.title;photoTrigger=btn;updateItemDetails(it);document.querySelector('#gallery-title').textContent=it.title;showPhoto()}
function stepItem(d){const list=galleryItems(),k=list.indexOf(photoTrigger);if(k<0||list.length<2)return false;openItem(list[(k+d+list.length)%list.length],d<0);return true}
document.querySelector('#photo-prev').addEventListener('click',()=>{if(photoIndex===0&&stepItem(-1))return;photoIndex=(photoIndex+photos.length-1)%photos.length;showPhoto()});
document.querySelector('#photo-next').addEventListener('click',()=>{if(photoIndex===photos.length-1&&stepItem(1))return;photoIndex=(photoIndex+1)%photos.length;showPhoto()});
{let sx=null,sy=0;const stage=galleryDialog.querySelector('.gallery-stage');
stage.addEventListener('touchstart',e=>{sx=e.touches[0].clientX;sy=e.touches[0].clientY},{passive:true});
stage.addEventListener('touchend',e=>{if(sx===null)return;const dx=e.changedTouches[0].clientX-sx,dy=e.changedTouches[0].clientY-sy;sx=null;if(Math.abs(dx)>40&&Math.abs(dx)>Math.abs(dy))document.querySelector(dx<0?'#photo-next':'#photo-prev').click()},{passive:true});}
galleryDialog.addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();document.querySelector('#photo-next').click()}if(e.key==='ArrowLeft'){e.preventDefault();document.querySelector('#photo-prev').click()}});
galleryDialog.addEventListener('close',()=>photoTrigger?.focus());
'''
app += marketplace.JS
app += r'''
{const d=document.getElementById('pay-dialog');if(d){let from=null;document.querySelectorAll('[data-pay]').forEach(b=>b.addEventListener('click',()=>{from=b;const m=document.getElementById('site-menu');if(m&&m.open){m.close();from=document.getElementById('menu-open')}
d.querySelectorAll('[data-pay-panel]').forEach(p=>p.hidden=p.dataset.payPanel!==b.dataset.pay);d.showModal();d.querySelector('[data-close]').focus()}));
d.addEventListener('click',e=>{if(e.target===d)d.close()});d.addEventListener('close',()=>from&&from.focus());}}
'''
app += r'''
{const d=document.getElementById('terms-dialog');if(d){let from=null;document.querySelectorAll('[data-terms]').forEach(b=>b.addEventListener('click',()=>{from=b;const m=document.getElementById('site-menu');if(m&&m.open){m.close();from=document.getElementById('menu-open')}d.showModal();d.querySelector('[data-close]').focus()}));
d.addEventListener('click',e=>{if(e.target===d)d.close()});d.addEventListener('close',()=>from&&from.focus());}}
'''
app += r'''
{const t=document.querySelector('.credits-tip'),bx=document.getElementById('credits-box');if(t&&bx){let at=0;
const close=()=>{if(bx.hidden)return;bx.hidden=true;t.setAttribute('aria-expanded','false');['pointerdown','scroll','wheel','touchmove','keydown'].forEach(e=>removeEventListener(e,outside,true))};
const outside=e=>{if(performance.now()-at<250)return;if(e.type==='pointerdown'&&(t.contains(e.target)))return;close()};
t.addEventListener('click',()=>{if(!bx.hidden){close();return}bx.hidden=false;t.setAttribute('aria-expanded','true');at=performance.now();['pointerdown','scroll','wheel','touchmove','keydown'].forEach(e=>addEventListener(e,outside,{capture:true,passive:true}))});}}
'''
app += r'''
{const fa=document.querySelector('.footer-art[data-globe]');if(fa){if('IntersectionObserver' in window){const io=new IntersectionObserver(e=>{if(e[0].isIntersecting){fa.classList.add('arrived');io.disconnect()}},{threshold:.25});io.observe(fa)}else fa.classList.add('arrived')}}
'''
app += r'''
{const H=document.documentElement,EV=['pointerdown','touchstart','scroll','wheel','keydown'],T=[];let boxAt=0,want=false;
// at 1.5 s box lands (3 s), then plaque (2 s); full emblem only after a touch, 1.5 s after the plaque has landed, dropping from the header. Nothing is skipped.
const startBox=()=>{if(boxAt)return;boxAt=performance.now();H.classList.add('scene-box');T.push(setTimeout(()=>H.classList.add('scene-plaque'),3000));T.push(setTimeout(()=>{if(want)H.classList.add('scene-go')},5500))};
const touch=()=>{if(want)return;want=true;EV.forEach(e=>removeEventListener(e,touch,true));startBox();const left=Math.max(0,boxAt+5500-performance.now());setTimeout(()=>{H.classList.add('scene-plaque');H.classList.add('scene-go')},left);setTimeout(()=>H.classList.add('scene-box','scene-plaque','scene-go'),left+4000)};
setTimeout(startBox,1500);EV.forEach(e=>addEventListener(e,touch,{capture:true,passive:true}));}
'''
app += r'''
{const f=document.querySelector('#request-item');if(f){const a=f.querySelector('.req-send'),ios=/iPad|iPhone|iPod/.test(navigator.userAgent)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
const build=()=>{const w=f.what.value.trim(),b=f.budget.value.trim();const msg='Hi Dylan, I found DKAINSWORLD. I\'m looking for '+(w||'an item')+(b?' (budget '+b+')':'')+'. Do you have it?';a.href='sms:+15104350747'+(ios?'&':'?')+'body='+encodeURIComponent(msg)};
['input','change','keyup','compositionend','blur'].forEach(e=>{f.what.addEventListener(e,build);f.budget.addEventListener(e,build)});a.addEventListener('pointerdown',build);a.addEventListener('click',build);build();
f.addEventListener('submit',e=>{e.preventDefault();build();a.click()});}}
'''
app += r'''
{const g=document.querySelector('#inventory-grid'),pos=document.querySelector('#list-pos');
const vis=()=>[...g.querySelectorAll('.item-card:not([hidden])')];
const upd=()=>{const v=vis();if(!v.length){pos.textContent='';return}const top=g.scrollTop;let k=v.findIndex(c=>c.offsetTop+c.offsetHeight/2>top);if(k<0)k=v.length-1;pos.textContent=(k+1)+' of '+v.length};
g.addEventListener('scroll',upd,{passive:true});new MutationObserver(upd).observe(g,{attributes:true,subtree:true,attributeFilter:['hidden']});upd();
document.querySelectorAll('[data-jump]').forEach(b=>b.addEventListener('click',()=>{const v=vis();const c=b.dataset.jump==='top'?v[0]:v[v.length-1];if(c)g.scrollTo({top:c.offsetTop,behavior:'smooth'})}));}
'''
app += r'''
{const b=document.body;let t=null;
addEventListener('scroll',()=>{b.classList.add('is-scrolling');clearTimeout(t);t=setTimeout(()=>b.classList.remove('is-scrolling'),220)},{passive:true});
const hero=document.querySelector('.hero');if(hero&&'IntersectionObserver' in window){new IntersectionObserver(e=>b.classList.toggle('past-hero',!e[0].isIntersecting),{threshold:0}).observe(hero)}}
'''
app += r'''
document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{const label=b.querySelector('[data-copy-label]');let ok=false;try{await navigator.clipboard.writeText(b.dataset.copy);ok=true}catch(e){}if(label)label.textContent=ok?'Copied ✓ '+b.dataset.copy:b.dataset.copy;setTimeout(()=>{if(label)label.textContent=b.dataset.copyIdle||''},2400)}));
'''
app += r'''
const orbitFx=document.querySelector('.hero-orbit-fx'),calm=matchMedia('(prefers-reduced-motion: reduce)');
function syncMotion(){if(!orbitFx)return;if(calm.matches){orbitFx.pause();orbitFx.removeAttribute('autoplay')}else{orbitFx.play().catch(()=>{})}}
syncMotion();calm.addEventListener?.('change',syncMotion);
'''
(P/'app.js').write_text(app,encoding='utf8')
css=Path(r'D:\AMH\DKAINSWORLD\public\styles.css').read_text(encoding='utf8')
css+=r'''
.site-header{gap:18px}.menu-toggle{min-width:44px;min-height:44px;border:1px solid #66736b;background:transparent;color:#fff;border-radius:8px;font-size:24px}.desktop-nav{margin-left:auto}.hero-actions button{font:inherit;font-size:13px;font-weight:800}.item-photo{display:block;width:100%;height:265px;border:0;padding:0;position:relative;overflow:hidden;background:#161b1b}.item-photo img{width:100%;height:100%;object-fit:cover;object-position:50% 44%}.item-photo>span{position:absolute;bottom:12px;right:12px;padding:8px 12px;background:#111e;color:#fff;border-radius:30px;font-size:11px;font-weight:700}.item-card .card-body .asking-price{color:#243c34;font-size:19px;font-weight:800;line-height:1.35;margin:15px 0 0}.item-card .card-body .availability{font-size:11px;margin-top:auto;margin-bottom:17px;color:#5d6c60}.unpictured{height:140px}.unpictured>svg{width:65px;height:65px}.item-card .card-body>p{overflow-wrap:anywhere}.payments-section{padding-top:60px;padding-bottom:60px}.payments-section>p:not(.eyebrow){max-width:740px;margin:18px 0 25px;color:var(--muted);font-size:14px}.payments-section .eyebrow{margin-bottom:14px}.payment-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.payment-link{display:flex;align-items:center;gap:12px;background:#fff;border:1px solid #c9d0c2;padding:18px;border-radius:10px;font-weight:800}.payment-link img{width:28px;height:28px;object-fit:contain}.payment-link small{display:block;font-size:10px;font-weight:400;color:#59605e;margin-top:4px}.qr-bottom{margin-top:25px}dialog{color:var(--ink);border:1px solid #b8c4b2;border-radius:18px;padding:28px;max-height:calc(100dvh - 40px);max-width:calc(100vw - 28px);overflow:auto;background:var(--paper);box-shadow:0 25px 80px #0005}dialog::backdrop{background:#111b}body:has(dialog[open]){overflow:hidden}.modal-heading{display:flex;align-items:flex-start;gap:18px;justify-content:space-between;margin-bottom:20px}.modal-heading h2{font-size:25px;letter-spacing:-.03em}.close-modal{width:44px;height:44px;min-width:44px;border-radius:50%;border:1px solid #bec8b7;background:#fff;color:#141b1d;font-size:27px}.site-menu{width:590px}.menu-qr{display:flex;align-items:center;gap:18px;padding:16px;background:#fff;width:100%;border:1px solid #c4cfb8;border-radius:12px;text-align:left;font-weight:800}.menu-qr img{width:80px;height:80px}.menu-qr small{display:block;font-size:11px;font-weight:400;margin-top:8px}.site-menu nav{display:flex;flex-direction:column;gap:5px;margin:20px 0}.site-menu nav a{padding:14px 0;border-bottom:1px solid var(--line);font-size:16px;font-weight:700}.site-menu .payment-grid{grid-template-columns:1fr 1fr}.payment-note{font-size:12px;color:var(--muted);margin-top:18px}.qr-dialog{width:460px;text-align:center}.qr-dialog>img{width:min(320px,100%);height:auto;margin:0 auto;background:#fff}.qr-dialog>p{margin:16px 0 5px}.qr-url{display:block;font-size:17px;font-weight:800;overflow-wrap:anywhere;margin-bottom:20px}.gallery-dialog{width:900px}.gallery-dialog>img{height:min(65dvh,760px);width:100%;object-fit:contain;background:#111}.source-note{font-size:11px;color:#59605e;margin-bottom:12px}.gallery-controls{display:flex;align-items:center;justify-content:space-between;margin-top:15px}.gallery-controls .button{min-width:55px}.gallery-controls p{font-weight:700}.qr-dialog a:focus-visible{outline:3px solid #2680a2}.brand-art{mask-image:radial-gradient(circle at center,#000 58%,transparent 72%)}.brand-art img{transform:scale(1.7);object-position:50% 43%}
@media(max-width:800px){.desktop-nav{display:none}.site-header{justify-content:space-between}.payment-grid{grid-template-columns:1fr 1fr}.hero-actions{gap:12px}.hero-actions .button{flex:1;white-space:nowrap}.item-photo{height:280px}}
@media(max-width:520px){.site-header{padding:15px 20px}.hero-actions .button{font-size:11px;padding:14px 12px}.payments-section{padding-top:40px;padding-bottom:40px}.payment-link{padding:14px 12px;gap:8px;font-size:14px}.payment-link img{width:23px;height:23px}.payment-link small{font-size:9px}.item-photo{height:280px}.item-card .card-body .asking-price{font-size:20px}.modal-heading h2{font-size:22px}dialog{padding:20px}.bottom-nav a{font-size:9px}.site-menu .payment-grid{gap:8px}}
'''
css += '\n.payment-link img{flex-shrink:0;padding:4px;border-radius:6px;width:32px;height:32px}.payment-link img[src$="zelle.svg"]{background:#6d1ed4}.payment-link img[src$="venmo.svg"]{background:#008cff}.payment-link img[src$="cashapp.svg"]{background:#008a35}.payment-link img[src$="paypal-mark.svg"]{padding:0}\n'
css += '\n'+(R/'hero-refinements.css').read_text(encoding='utf8')
css += marketplace.CSS + header_css + '\n' + (R/'items-v3.css').read_text(encoding='utf8') + '\n' + (R/'sections-v4.css').read_text(encoding='utf8') + '\n' + (R/'punch-egg.css').read_text(encoding='utf8') + chr(10) + (R/'bees-dk.css').read_text(encoding='utf8')
(P/'styles.css').write_text(css,encoding='utf8')
readme='''# DKAINSWORLD recovery\n\nAuthoritative recovery workspace: D:/AMH/DKAINSWORLD-Recovery. Original D:/AMH/DKAINSWORLD is untouched. Only public/ belongs in Pages deployment.\n\nEdit inventory.json then run build.py with Python312. Or edit inventory.csv and run build.py --from-csv. The builder exports matching public JSON/CSV, HTML and searchable inquiry cards. Photos are semicolon-separated paths in CSV. Confirm prices/availability with Dylan; do not infer specifications or safety condition.\n\nApproved eight-photo source commit: bf2b4277dafdea90bf2d1d39e0a5217f049d445d. Original screenshot bytes preserved; gallery explicitly distinguishes historical screenshot prices from current asking prices. Pending pipe-wrench, tool-set and backpack photos are not included.\n\nContact: +15104350747. Directions use the exact owner URL without asserting a business address. Payment buttons link only to official platform homepages, not recipient accounts. Real site QR decodes to https://dkainsworld.pages.dev/.\n'''
# Release README is maintained separately so rebuilds preserve verified release history.
print(json.dumps({'inventory_listings':len(items),'item_photos':len(prov['assets']),'qr_decode':decoded.text,'payment_homepages':len(platforms),'originals_unchanged':True,'public_files':sum(p.is_file() for p in P.rglob('*'))}))
# Cache-bust changed assets: /assets/<file> (not item photos) gets ?v=<hash8> in HTML and CSS so phones never show stale copies.
import re as _re
def _bust(text):
 def rep(m):
  rel=m.group(1);f=P/rel.lstrip('/')
  if '/items/' in rel or not f.is_file():return m.group(0)
  return rel+'?v='+hashlib.sha256(f.read_bytes()).hexdigest()[:8]
 return _re.sub(r'(/assets/[A-Za-z0-9._/-]+\.(?:png|webp|jpg|svg|mp4|webm))(?![?\w])',rep,text)
for _f in ['index.html','styles.css','app.js','punch-egg.js']:
 _p=P/_f;_p.write_text(_bust(_p.read_text(encoding='utf8')),encoding='utf8')
# AI + search files: llms.txt (plain summary for AI assistants), sitemap.xml with image entries, robots.txt.
import datetime as _dt
_today=_dt.date.today().isoformat();_B='https://dkainsworld.pages.dev'
_lines=['# DKAINSWORLD','','> Dylan’s secondhand store in Fremont, California: tools, boards, furniture, backpacks and flea-market finds. Call or text Dylan to confirm an item before you come by.','',
 '## Contact','- Call or text: (510) 435-0747','- Email: dkain1017dk@gmail.com','- Directions: https://maps.app.goo.gl/Nu84KZXRDFjCbwpp7?g_st=ac','- Facebook Marketplace store: https://www.facebook.com/marketplace/profile/100005788064086/','',
 '## Payments','- Zelle: (510) 435-0747 or dkain1017dk@gmail.com','- Cash App and PayPal: dkain1017dk@gmail.com','- Chime: ask Dylan','',
 '## Terms','- All items are sold as-is. Inspect the item before paying; paying means you accept it.','- Contact Dylan within 1 hour of buying if there is a problem. All sales are final.','- Store credit may be possible the same day if the item is unused and in the same working condition (not guaranteed).','',
 '## Items and prices (confirm with Dylan)']
for _i in items:_lines.append(f'- {_i["title"]}: {_i["price_text"]}'+(f' — {_i["sourceUrl"]}' if _i.get('sourceUrl') else ''))
_lines+=['','## Site',f'- Home: {_B}/',f'- Item data (JSON): {_B}/inventory.json',f'- Item data (CSV): {_B}/inventory.csv','',f'Updated {_today}.']
(P/'llms.txt').write_text('\n'.join(_lines)+'\n',encoding='utf8')
_imgs=''.join(f'<image:image><image:loc>{_B}{x}</image:loc><image:title>{E(i["title"])}</image:title></image:image>' for i in items for x in i['photos'][:1])
(P/'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"><url><loc>{_B}/</loc><lastmod>{_today}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority>{_imgs}</url><url><loc>{_B}/llms.txt</loc><lastmod>{_today}</lastmod></url></urlset>\n',encoding='utf8')
(P/'robots.txt').write_text(f'User-agent: *\nAllow: /\n\n# Plain-text summary for AI assistants: {_B}/llms.txt\nSitemap: {_B}/sitemap.xml\n',encoding='utf8')
