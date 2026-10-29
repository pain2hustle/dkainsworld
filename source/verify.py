from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlsplit,unquote
import json,hashlib,subprocess,urllib.request,re,time
from PIL import Image
import zxingcpp
R=Path(__file__).resolve().parent;P=R/'public';errors=[]
inv=json.loads((P/'inventory.json').read_text(encoding='utf8'));assert len(inv)==20 and all(x['photos'] for x in inv)
assert len({p for x in inv for p in x['photos']})==33
assert next(x for x in inv if x['id']=='jack-stands')['price_text']=='$35'
expected_prices={'pipe-wrenches':'$15 each','pick-your-tools':'$35 each','dbz-orange-yellow':'$20 for both · $15 each','kid-goku':'$30'}
for id,price in expected_prices.items():assert next(x for x in inv if x['id']==id)['price_text']==price
payments={'https://cash.app/','https://www.paypal.com/'}
s=BeautifulSoup((P/'index.html').read_text(encoding='utf8'),'html.parser');ids=[x['id'] for x in s.select('[id]')];assert len(ids)==len(set(ids))
assert len(s.select('[data-qr]'))==3
assert [x.get_text(' ',strip=True) for x in s.select('.bottom-nav span')]==['Browse Items','Categories','Call Dylan','Text Dylan','Directions'] and len(s.select('a[href="sms:+15104350747"]'))==6
assert len(s.select('.pay-chip[data-pay]'))==8 and len(s.select('#pay-dialog [data-pay-panel]'))==4 and len(s.select('#pay-dialog [data-copy="dkain1017dk@gmail.com"]'))==3 and len(s.select('#pay-dialog [data-copy="5104350747"]'))==2 and 'venmo' not in str(s).lower()
assert {x['href'] for x in s.select('a[href^="tel:"]')}=={'tel:+15104350747'}
assert all(x['href']=='https://maps.app.goo.gl/Nu84KZXRDFjCbwpp7?g_st=ac' for x in s.select('a[href*="maps.app.goo.gl"]'))
assert s.select_one('link[rel=canonical]')['href']=='https://dkainsworld.pages.dev/'
assert not (P/'credits.html').exists() and not s.select('a.credits-link')
assert [x['href'] for x in s.select('#site-menu nav a[href^="mailto:"]')]==['mailto:dkain1017dk@gmail.com?subject=DKAINSWORLD%20question'] and s.select_one('.footer-email')['href'].startswith('mailto:dkain1017dk@gmail.com?subject=DKAINSWORLD%20question')
for htmlfile in P.rglob('*.html'):
 doc=BeautifulSoup(htmlfile.read_text(encoding='utf8'),'html.parser');localids={x['id'] for x in doc.select('[id]')}
 for n in doc.select('[src],link[href],a[href]'):
  v=n.get('src') or n.get('href','');u=urlsplit(v)
  if u.scheme or u.netloc:continue
  if not u.path:
   if u.fragment and u.fragment not in localids:errors.append('Missing fragment '+v)
   continue
  dest=P/unquote(u.path.lstrip('/')) if u.path.startswith('/') else htmlfile.parent/unquote(u.path)
  if u.path=='/':dest=P/'index.html'
  if not dest.is_file():errors.append('Missing local asset '+v)
for x in json.loads((R/'private/item-photo-provenance.json').read_text())['assets']:
 assert hashlib.sha256((P/x['path']).read_bytes()).hexdigest()==x['sha256']
extra=json.loads((R/'private/photo-update-provenance.json').read_text(encoding='utf8'))
assert len(extra['assets'])==11
for x in extra['assets']:
 assert hashlib.sha256((R/'handoff/Images - 19 original item photos and 8 brand assets'/Path(x['path']).name).read_bytes()).hexdigest()==x['sha256'] and not (P/x['path']).exists()
for ident,expected in {'pipe-wrenches':3,'pick-your-tools':3,'dbz-orange-yellow':3,'kid-goku':2}.items():
 it=next(x for x in inv if x['id']==ident);assert len(it['photos'])==expected
 button=s.select_one('.item-photo[data-gallery="'+ident+'"]');assert button is not None
 card=button.find_parent('article');assert card is not None and not card.has_attr('hidden')
 assert it['price_text'] in card.get_text(' ',strip=True)
 assert button.select_one('img')['src']==it['photos'][0]
assert 'sample' not in ' '.join(x.get_text(' ',strip=True) for x in s.select('#browse,#price-list,#contact,#payment-options')).lower()
for name,sha in {'dkainsworld-original.jpg':'c40ead21a8d64d88b4d64431ac448eb7387c329413dbd1a36de496e06c2283df','dkainsworld-header.jpg':'ad45b19bea65868f8b2a3dbcb7360150e800fa7c6f38d88a5a9fb7a4502640a1'}.items():assert hashlib.sha256((P/'assets'/name).read_bytes()).hexdigest()==sha
assert zxingcpp.read_barcode(Image.open(P/'assets/site-qr.png')).text=='https://dkainsworld.pages.dev/'
node=subprocess.run([r'C:\Program Files\nodejs\node.exe','--check',str(P/'app.js')],capture_output=True,text=True);assert node.returncode==0,node.stderr
manifest=[];local=[]
for f in sorted(P.rglob('*')):
 if not f.is_file():continue
 rel=f.relative_to(P).as_posix();b=f.read_bytes();sha=hashlib.sha256(b).hexdigest();manifest.append({'path':rel,'bytes':len(b),'sha256':sha})
 if rel.endswith(('.html','.js','.json','.csv','.css','.txt','.xml')):
  txt=b.decode('utf8');assert not any(x in txt for x in ['libfile_','completion_token','CLOUDFLARE_API_TOKEN','http_headers'])
 with urllib.request.urlopen('http://127.0.0.1:8766/'+rel,timeout=15) as resp:local.append({'path':rel,'status':resp.status,'hash_match':hashlib.sha256(resp.read()).hexdigest()==sha})
 time.sleep(.03)
assert all(x['status']==200 and x['hash_match'] for x in local)
report={'ready_static':not errors,'project':'dkainsworld','account':'a08783a0d3715df907ed5ccad38f0dcf','branch':'main','target':'https://dkainsworld.pages.dev/','inventory_count':len(inv),'item_photo_count':33,'qr_decoded':'https://dkainsworld.pages.dev/','original_assets_verified':True,'errors':errors,'files':manifest}
(R/'private/release-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf8');(R/'private/local-file-verification.json').write_text(json.dumps(local,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='files'}));print(json.dumps({'files':len(manifest),'bytes':sum(x['bytes'] for x in manifest),'all_local_files_http200_and_hash_matched':True}));raise SystemExit(bool(errors))
