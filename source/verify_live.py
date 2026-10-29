from pathlib import Path
import json,hashlib,time
import requests
R=Path(r'D:\AMH\DKAINSWORLD-PhotoUpdate');D=R/'private';m=json.loads((D/'release-manifest.json').read_text());assert (D/'apply.json').exists()
receipt=json.loads((D/'apply.json').read_text());assert receipt.get('state')!='pending' and not receipt.get('isError'),'Deployment has not returned success'
parts=[json.loads(x['text']) for x in receipt.get('content',[]) if x.get('type')=='text'];assert parts,'Missing deployment result'
results=[];session=requests.Session();blocked=False
for item in m['files']:
 if item['path']=='_headers':continue
 path=item['path'];url='https://dkainsworld.pages.dev/'+('' if path=='index.html' else path)
 try:
  response=session.get(url,timeout=25);entry={'path':path,'status':response.status_code,'hash_match':hashlib.sha256(response.content).hexdigest()==item['sha256']};results.append(entry)
  if response.status_code in [401,403]:blocked=True;break
 except requests.RequestException as e:results.append({'path':path,'error':type(e).__name__})
 time.sleep(.12)
if not blocked:
 for entry in results:
  if not entry.get('hash_match') and entry.get('status') in [200,404]:
   item=next(x for x in m['files'] if x['path']==entry['path']);url='https://dkainsworld.pages.dev/'+('' if item['path']=='index.html' else item['path'])
   try:
    response=session.get(url,timeout=25);entry.update(initial_status=entry['status'],bounded_propagation_recheck=True,status=response.status_code,hash_match=hashlib.sha256(response.content).hexdigest()==item['sha256'])
    if response.status_code in [401,403]:blocked=True;break
   except requests.RequestException as e:entry['recheck_error']=type(e).__name__
   time.sleep(.12)
failures=[x for x in results if not x.get('hash_match') or x.get('status') not in ([200,404] if x['path']=='404.html' else [200])]
report={'url':'https://dkainsworld.pages.dev/','expected_public_files':len(m['files'])-1,'checked_files':len(results),'all_verified':not blocked and not failures and len(results)==len(m['files'])-1,'access_blocked':blocked,'failures':failures,'files':results}
(D/'live-file-verification.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='files'}));raise SystemExit(0 if report['all_verified'] else 2)
