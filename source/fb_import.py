# Imports Dylan's Facebook Marketplace listings from item links (public crawler view): title, full description,
# price, sold/pending status and ALL listing photos. Sold or pending listings are skipped.
# Usage: py -3.12 fb_import.py   (IDs in FB_IDS; add new ones there)
import re, json, html, hashlib, io, time, urllib.request
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parent; P = R / 'public'; RAW = R / 'private/fb/raw'; RAW.mkdir(parents=True, exist_ok=True)
OUT = P / 'assets/items/fb'; OUT.mkdir(parents=True, exist_ok=True)
FB_IDS = ["28444710648484140", "2106563970226121", "1103700079241670", "29340354208899220", "2008682646482497", "1628587512279660", "1403768231871988", "1027551473419732", "2203877097045285", "1014728867580413", "835829219345219", "1103673808801497", "2208222510038444", "1044954511602596", "28539791478950006", "2244632312989493", "1616813373472251", "1644836923844130", "1768720581025846", "1145957804605334", "1549779063518130", "1651662660121132", "1035967888804760", "3233886933476283", "1005832162256428", "1017019954148846", "2418709711938761", "2001603063827002", "1444410677446708", "2242251913179357", "1683382969613386", "3720166458140699", "1341542560710808", "1724769695638118", "1510657350522808", "994432646903937", "1053338103752905", "4440859556151452", "1338103018508645", "1486178936592935", "1019185017158760", "1004420352306605", "2537282790065638", "2720288441689939", "996628529622866", "1050699060862774", "1342858441106436", "4565419877025851", "4346578868944441", "1397719152190559", "1512123540497265", "852481161267142", "1183144577532101", "1095130130072110", "1645688946906173", "1489753759743287", "28806313225651782", "1655503066201577", "1407076118241862", "1401473024867070", "1746001770008176", "1729951008111216", "1683101783233505", "1599695811831897", "1451318676844393", "1549724643017094", "4560253797586892", "1756692298905972", "4594829944134761", "1060265963299849", "1551909639540911", "2071479266789763", "1620915199660258", "950015467383839", "1637823094611293", "1067598032659300", "1091829010242822", "946221801828887", "1539579527494709", "1049864824448653", "1071618805214050", "1230470772572261", "2123862794877598", "1094768000205523", "1053398287602883", "2000900333948632", "1666254698838371", "29145503811705350", "1761576208299792", "1914258656203978", "1457010839598594", "3252317828289773", "1786815835931167", "2221441265367695", "1291399169556014", "1541255611023548", "1700999081584495", "1486421209895232", "1752984489452333", "1025732646917776", "1036536502183817", "2167895340725140", "1574919324062321", "1328399855384967", "1130691399862274", "1722338088765573", "2478287719279943", "1714399126417415", "1515167466724871", "1272085784998456", "1506822784243207", "2189238478566562", "1709868413643944", "2153189092214442", "1400130288532240", "980665261375375", "28544960785193905", "1024763066670807"]
UA = 'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)'
CAT = [(r'chair|couch|sofa|dresser|table|desk|mirror|lamp|cabinet|shelf|bed|furniture', 'furniture'), (r'tool|wrench|socket|ratchet|drill|saw|milwaukee|dewalt|klein|craftsman|jack', 'tools'),
       (r'skate|longboard|board', 'boards'), (r'backpack|bag\b|bags\b', 'backpacks')]

def get(url):
    for t in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en-US'}), timeout=60).read()
        except Exception:
            time.sleep(5 * (t + 1))
    raise RuntimeError('fetch failed ' + url)

def jstr(x): return json.loads('"' + x + '"')

def parse(iid, s):
    og = re.search(r'<meta property="og:title" content="([^"]*)"', s); title = html.unescape(og.group(1)) if og else ''
    ogi = re.search(r'<meta property="og:image" content="([^"]*)"', s); og_file = re.search(r'/(\d+_\d+_\d+_n\.jpg)', html.unescape(ogi.group(1))).group(1) if ogi else ''
    # main listing block = the marketplace_listing_title equal to og:title that carries listing_price
    price = sold = pending = None
    for m in re.finditer(r'"marketplace_listing_title":"((?:[^"\\]|\\.)*)"', s):
        if jstr(m.group(1)).strip() != title.strip(): continue
        seg = s[max(0, m.start() - 2500):m.start() + 400]
        p = re.findall(r'"listing_price":\{"formatted_amount_zeros_stripped":"([^"]*)"', seg)
        so = re.findall(r'"is_sold":(true|false)', seg); pe = re.findall(r'"is_pending":(true|false)', seg)
        if p: price = p[-1]
        if so: sold = so[-1] == 'true'
        if pe: pending = pe[-1] == 'true'
        if price and sold is not None: break
    desc = ''
    d = re.search(r'"redacted_description":\{"text":"((?:[^"\\]|\\.)*)"', s)
    if d: desc = jstr(d.group(1)).strip()
    photos = []
    for m in re.finditer(r'"listing_photos":\[', s):
        arr = s[m.end():m.end() + 60000]; arr = arr[:arr.find(']')] if ']' in arr else arr
        uris = [jstr(u) for u in re.findall(r'"uri":"((?:[^"\\]|\\.)*)"', arr)]
        if og_file and any(og_file in u for u in uris): photos = uris; break
    return dict(id=iid, title=title, price=price, sold=sold, pending=pending, desc=desc, photos=photos)

def slugify(t): return 'fb-' + re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')[:40].strip('-')

results = []
for iid in FB_IDS:
    raw = RAW / f'{iid}.html'
    if not raw.exists() or raw.stat().st_size < 200000: raw.write_bytes(get(f'https://www.facebook.com/marketplace/item/{iid}/')); time.sleep(2)
    info = parse(iid, raw.read_text(encoding='utf8', errors='replace'))
    info['slug'] = slugify(info['title']) if info['title'] else f'fb-{iid}'
    files = []
    if not (info['sold'] or info['pending']):
        for n, u in enumerate(info['photos'][:3], 1):  # first 3 photos ship with the main site
            f = OUT / f'{info["slug"]}-{n}.webp'
            if not f.exists():
                im = Image.open(io.BytesIO(get(u))).convert('RGB'); im.thumbnail((560, 560), Image.LANCZOS); im.save(f, 'WEBP', quality=55, method=6)
            files.append({'path': f.relative_to(P).as_posix(), 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()})
    info['files'] = files
    results.append(info)
    print(iid, '|', info['title'][:60], '|', info['price'], '| sold' if info['sold'] else '', '| pending' if info['pending'] else '', '|', len(files), 'photos')
(R / 'private/fb-import.json').write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding='utf8')
