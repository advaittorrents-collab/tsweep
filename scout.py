import json,re,datetime,urllib.request,os
S="state.txt"; LAST=int(open(S).read().strip()) if os.path.exists(S) else 0
today=datetime.datetime.utcnow().strftime("%Y-%m-%d")
def out(t): open("latest.md","w").write(t+"\n")
try:
    r=urllib.request.Request("https://www.tesla.com/cua-api/apps/careers/state",
        headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"})
    d=json.load(urllib.request.urlopen(r,timeout=90))
    locs=d["lookup"]["locations"]; jobs=d["listings"]
except Exception as e:
    out(f"{today}: ERROR {repr(e)[:200]}"); raise SystemExit
US="Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|District Of Columbia|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming"
CA="Alberta|British Columbia|Manitoba|New Brunswick|Newfoundland|Nova Scotia|Ontario|Prince Edward Island|Quebec|Saskatchewan"
LOC=re.compile(r",\s*("+US+"|"+CA+")\s*$",re.I)
INC=re.compile(r"mechanical|design|manufactur|equipment|test|validation|electromechanical|mechatronic|actuator|drive unit|gearbox|tooling|fixture|automation|reliability|hardware|battery|cell|pack|module|thermal|joining|npi|structur",re.I)
EXC=re.compile(r"production engineer|quality|technician|supervisor|process engineer|intern|co-op|software|firmware|associate|operator|manager|director",re.I)
HIGH=re.compile(r"mechanical design|design engineer|manufacturing engineer|equipment|test|validation|electromechanical|battery|cell",re.I)
ids=[int(j["id"]) for j in jobs if str(j.get("id","")).isdigit()]
NEW=max(ids+[LAST])
if LAST==0:
    out(f"{today}: Baseline set at {NEW}. New jobs start tomorrow.")
else:
    rows=[]
    for j in jobs:
        try: i=int(j["id"])
        except: continue
        t=str(j.get("t","")); l=locs.get(str(j.get("l","")),"")
        if i<=LAST or "engineer" not in t.lower() or not INC.search(t) or EXC.search(t) or not LOC.search(l): continue
        rows.append(("High" if HIGH.search(t) else "Med",t,l,i))
    rows.sort(key=lambda x:(x[0]!="High",-x[3]))
    if not rows: out(f"{today}: No new Tesla matches.")
    else:
        out(f"{today}: {len(rows)} new\n\n| Match | Title | Location | Req ID | Apply |\n|---|---|---|---|---|\n"+
            "\n".join(f"| {m} | {t} | {l} | {i} | https://www.tesla.com/careers/search/job/apply/{i} |" for m,t,l,i in rows))
open(S,"w").write(str(NEW))
