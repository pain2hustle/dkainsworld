# Merges private/fb-import.json (fb_import.py) into inventory.json: one listing per unsold Facebook item,
# all photos, full description, price (owner overrides win), View on Facebook link. Re-run after fb_import.py.
import json, re
from pathlib import Path
R = Path(__file__).resolve().parent
imp = json.loads((R / 'private/fb-import.json').read_text(encoding='utf8'))
inv = json.loads((R / 'inventory.json').read_text(encoding='utf8'))
# Stable ids for listings already on the site
IDS = {'28444710648484140': 'fb-milwaukee-toolbox', '2106563970226121': 'fb-mustang-sunshade', '1103700079241670': 'fb-cobra-cctv', '29340354208899220': 'fb-chesterfield-chairs'}
# Prices Austin gave for Dylan (override Facebook)
OWNER_PRICE = {'2106563970226121': '$25', '1103700079241670': '$140'}
SHORT = {'28444710648484140': 'Milwaukee tool box', '2106563970226121': 'Car sunshade', '1103700079241670': 'Security cameras', '29340354208899220': 'Chesterfield chairs',
         '2008682646482497': '90s comic books', '1628587512279660': "Joe's Jeans pumps", '1403768231871988': 'Extension cord', '1027551473419732': 'Penny boards',
         '2203877097045285': 'Stanley tape measure', '1014728867580413': 'Sperry wire tracker', '835829219345219': 'Air hoses', '1103673808801497': 'Hole saws', '2208222510038444': 'Milwaukee hole saws', '1044954511602596': 'Bassett armchair', '28539791478950006': 'Adidas sneakers', '2244632312989493': 'Bartman figurine', '1616813373472251': 'Mini fridge', '1644836923844130': 'Mountain bike', '1768720581025846': 'Rolling backpack', '1145957804605334': 'Hockey gear'}
CAT = [(r'chair|couch|sofa|dresser|table|desk|mirror|lamp|cabinet|shelf|furniture', 'furniture'), (r'penny board|skate|longboard', 'boards'),
       (r'tool|wrench|socket|ratchet|drill|saw|hole saw|milwaukee|tape measure|tracker|hose|extension cord|surveillance|camera', 'tools'), (r'backpack', 'backpacks')]
def cat(t):
    for rx, c in CAT:
        if re.search(rx, t, re.I): return c
    return 'finds'
def clean_title(t): return re.sub(r'^[•\s]+', '', t).strip()
def clean_desc(d):
    d = re.sub(r'\s+\n', '\n', d).strip(); d = re.sub(r'\n{2,}', '\n', d)
    return d[:700].rsplit(' ', 1)[0] + '…' if len(d) > 700 else d
keep = [i for i in inv if i.get('platform') != 'facebook-marketplace']
added = []
for x in imp:
    if x['sold'] or x['pending'] or not x['files']: continue
    iid = x['id']; lid = IDS.get(iid, x['slug'])
    added.append(dict(id=lid, title=clean_title(x['title']), category=cat(x['title']), price_text=OWNER_PRICE.get(iid, x['price'] or 'See price on Facebook'),
        description=clean_desc(x['desc']) or 'See the Facebook listing for details.', availability='Listed on Facebook Marketplace · ask Dylan',
        condition='See the Facebook listing', brand='', model='', photos=['/' + f['path'] for f in x['files']],
        sourceUrl=f'https://www.facebook.com/marketplace/item/{iid}/', platform='facebook-marketplace', sourceStatus='verified', photoCredit=''))
ORDER = ['tools', 'boards', 'furniture', 'backpacks', 'finds']
inv2 = sorted(keep + added, key=lambda x: ORDER.index(x['category']) if x['category'] in ORDER else 9)  # organized by category, store items first within each
(R / 'inventory.json').write_text(json.dumps(inv2, ensure_ascii=False, indent=2), encoding='utf8')
(R / 'private/fb-short.json').write_text(json.dumps({IDS.get(k, next((x['slug'] for x in imp if x['id'] == k), k)): v for k, v in SHORT.items()}, ensure_ascii=False, indent=1), encoding='utf8')
print(len(keep), 'store items +', len(added), 'Facebook items =', len(inv2))
for a in added: print(' ', a['id'], a['category'], a['price_text'], len(a['photos']), 'photos')
