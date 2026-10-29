from urllib.parse import urlsplit
import re
FIELDS=['sourceUrl','platform','sourceStatus']
STORE_URL='https://www.facebook.com/marketplace/profile/100005788064086/?ref=permalink&mibextid=dXMIcH'
def verified_url(item):
    url=item.get('sourceUrl','')
    if not url:
        assert not item.get('platform') and not item.get('sourceStatus'), 'Incomplete source metadata'
        return None
    u=urlsplit(url)
    assert u.scheme=='https' and u.netloc=='www.facebook.com' and re.fullmatch(r'/marketplace/item/[0-9]+/?',u.path), 'Unexpected Marketplace destination'
    assert item.get('platform')=='facebook-marketplace', 'Unexpected source platform'
    assert item.get('sourceStatus') in ('pending','verified'), 'Unknown verification state'
    return url if item['sourceStatus']=='verified' else None

def store_link(soup):
    link=soup.new_tag('a',href=STORE_URL,target='_blank',rel='noopener noreferrer')
    link['class']='fb-store-link'
    icon=soup.new_tag('span');icon['class']='facebook-mark';icon['aria-hidden']='true';icon.string='f'
    label=soup.new_tag('span');label.string='FB Market Store'
    link.extend([icon,label]);return link

def decorate(soup,items):
    soup.select_one('#site-menu nav').insert(0,store_link(soup))
    note=soup.select_one('.hero-note');hint=soup.new_tag('span');hint['class']='hero-inquiry';hint.string=note.get_text(' ',strip=True);note.clear();note.extend([hint,store_link(soup)])
    soup.select_one('.section-heading').append(store_link(soup))
    soup.select_one('.footer-copy').append(store_link(soup))
    for item in items:
        if verified_url(item):
            card=soup.select_one('#item-'+item['id'])
            badge=soup.new_tag('button',type='button')
            badge['class']='marketplace-detail'
            badge['data-gallery']=item['id']
            badge.string='Facebook Marketplace · Item details'
            card.select_one('.card-body').insert(0,badge)
    dialog=soup.select_one('#gallery-dialog')
    details=soup.new_tag('div',id='gallery-details')
    for name in ['price','description']:
        node=soup.new_tag('p',id='gallery-'+name);details.append(node)
    link=soup.new_tag('a',id='gallery-source',target='_blank',rel='noopener noreferrer')
    link['class']='button button-dark marketplace-source';link['hidden']=''
    link.string='View on Facebook Marketplace';details.append(link)
    dialog.select_one('.gallery-controls').insert_after(details)

JS=r"""
function updateItemDetails(it){
 document.querySelector('#gallery-price').textContent=it.price_text;
 document.querySelector('#gallery-description').textContent=it.description;
 const link=document.querySelector('#gallery-source');
 const verified=it.platform==='facebook-marketplace'&&it.sourceStatus==='verified'&&/^https:\/\/www\.facebook\.com\/marketplace\/item\/[0-9]+\/?(?:\?[^#]*)?$/.test(it.sourceUrl||'');
 link.hidden=!verified;if(verified)link.href=it.sourceUrl;else link.removeAttribute('href');
 const note=galleryDialog.querySelector('.source-note');note.hidden=!it.photos.length;
 if(it.photoCredit){note.textContent='Ask Dylan for photos of what’s in stock right now.';}
 else if(it.platform==='facebook-marketplace'){note.textContent='Photo from Dylan’s Facebook Marketplace listing. Open the listing to see all photos.';}
 else{note.textContent='';note.hidden=true;}
}
"""
CSS="""
.marketplace-detail{align-self:flex-start;border:1px solid #c2d3ea;background:#edf4ff;color:#153b75;border-radius:6px;font-size:11px;font-weight:700;padding:10px 12px;min-height:44px;margin-bottom:14px;text-align:left}
#gallery-details{margin-bottom:18px}#gallery-price{font-size:19px;font-weight:800}#gallery-description{font-size:13px;margin:8px 0 14px}.marketplace-source{min-height:48px;white-space:normal;text-align:center}
"""

CSS += """
.fb-store-link{display:inline-flex;align-items:center;justify-content:flex-start;gap:9px;min-height:44px;padding:9px 12px;border:1px solid #90a8c2;border-radius:7px;background:#162d49;color:#f4f8ff;font-size:12px;font-weight:700;line-height:1.3;white-space:nowrap}
.facebook-mark{display:inline-grid;place-items:center;width:23px;height:23px;flex:0 0 23px;border-radius:5px;background:#1877f2;color:white;font:bold 25px/1 Arial,sans-serif;padding-top:4px;overflow:hidden}
.hero-note{display:flex;align-items:center;flex-wrap:wrap;gap:8px 14px}.hero-note .fb-store-link{font-size:11px;padding:7px 10px}.section-heading .fb-store-link{flex-shrink:0}.footer-copy .fb-store-link{display:flex;width:max-content;max-width:100%;margin-top:14px}.site-menu nav .fb-store-link{padding:10px 12px;color:#f4f8ff}
@media(max-width:800px){.hero .hero-actions{bottom:96px}.hero .hero-note{bottom:16px;display:flex;justify-content:space-between;gap:4px 8px}.hero .hero-note .fb-store-link{min-height:40px}.hero-art{top:50%}.section-heading .fb-store-link{align-self:flex-start}}
@media(max-width:360px){.hero .hero-note{font-size:9px}.hero .hero-note .fb-store-link{font-size:10px}.hero .hero-note{flex-wrap:nowrap}}
"""

CSS += '\n@media(max-width:800px){.hero .hero-note{bottom:32px;justify-content:center}.hero-inquiry{display:none}.hero .hero-note .fb-store-link{width:100%;min-height:44px;justify-content:center;font-size:12px}}\n'
