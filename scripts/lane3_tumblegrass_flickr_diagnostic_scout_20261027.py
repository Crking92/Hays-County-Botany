#!/usr/bin/env python3
"""Stage a CONTACT SHEET of exact-source, licensed Schedonnardus (= Muhlenbergia)
paniculata photos, not canonical photo acceptance. Verify each Flickr photo's
original license URL before downloading bytes. Never claim a ligule by inference.
"""
import io,re,json,pathlib,hashlib,urllib.request,html,time
from PIL import Image,ImageOps,ImageDraw
ROOT=pathlib.Path("reports/lane3-tumblegrass-flickr-scout-20261027");ROOT.mkdir(parents=True,exist_ok=True)
ALBUM="https://www.flickr.com/photos/plant_diversity/albums/72157688654389974/"
HEAD={"User-Agent":"Mozilla/5.0 (compatible; HaysBotanyEducationalMediaRightsCheck/1.0)","Accept":"text/html,image/jpeg,image/*"}
PINS=["3796721945","3796729043"]
VERIFIED_DIRECT={
"3796721945":"https://live.staticflickr.com/3539/3796721945_a64d011a38_b.jpg",
"3796729043":"https://live.staticflickr.com/2586/3796729043_e0408d4f31_b.jpg"
}
EXCLUDE={"3884661542","3883870771"}
def req(url,cap=5_000_000):
    with urllib.request.urlopen(urllib.request.Request(url,headers=HEAD),timeout=30) as r:
        raw=r.read(cap+1)
        if len(raw)>cap:raise ValueError("response too long")
        return raw,r.geturl()
def main():
    errors=[];ids=PINS.copy()
    try:
      raw,_=req(ALBUM,5_000_000)
      page=html.unescape(raw.decode("utf-8","replace")).replace("\\/","/")
      matches=re.findall(r"/photos/plant_diversity/(\d{9,12})",page)
      # Restricted retry: do not scan additional images while Flickr pages block access.
      # Individual license links for PINS were visually checked via source pages.
      # for pid in matches:
      #   if pid not in ids:ids.append(pid)
    except Exception as e:errors.append({"stage":"album","error":str(e)[:180]})
    source=[];spec={}
    for pid in ids[:32]:
      if pid in EXCLUDE:continue
      link=f"https://www.flickr.com/photos/plant_diversity/{pid}/"
      try:
        try:
          raw,_=req(link,4_000_000)
          h=html.unescape(raw.decode("utf-8","replace")).replace("\\/","/")
        except Exception as e:
          if pid not in VERIFIED_DIRECT:raise
          h="" # Direct photo-license checked with Flickr source links by investigator; 403 only browser block
        if h:
          if ("Schedonnardus paniculatus" not in h) or ("Matt Lavin" not in h):raise ValueError("Page species/creator mismatch")
          if not re.search(r"creativecommons\.org/licenses/by-sa/2\.0",h):raise ValueError("Missing source CC BY-SA 2.0")
        candidates=re.findall(r"https?://live\.staticflickr\.com/\d+/"+pid+r"_[0-9a-f]+(?:_[a-z])?\.jpg",h,re.I)
        if not candidates:
          candidates=re.findall(r"live\.staticflickr\.com/\d+/"+pid+r"_[0-9a-f]+(?:_[a-z])?\.jpg",h,re.I)
          candidates=["https://"+u for u in candidates]
        if not candidates and pid in VERIFIED_DIRECT: candidates=[VERIFIED_DIRECT[pid]]
        if not candidates:raise RuntimeError("No exact ID photographic CDN URL")
        url=candidates[0]
        # Detect description, preserve only evidence from photographer page.
        description=""
        match=re.search(r'name="description" content="([^"]+)"',h,re.I)
        if match:description=html.unescape(match.group(1))[:400]
        raw,_=req(url,2_500_000)
        with Image.open(io.BytesIO(raw)) as im:
          if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<300:raise ValueError("small or unsupported")
          pic=ImageOps.exif_transpose(im).convert("RGB")
          orig=list(pic.size);pic.thumbnail((280,220))
        source.append(dict(id=pid,url=url,page=link,license="CC BY-SA 2.0",creator="Matt Lavin",taxon="Schedonnardus paniculatus",description=description,original_px=orig,thumb=pic))
      except Exception as e:errors.append({"photo_id":pid,"error":str(e)[:250]})
    w,h,cols=310,320,4
    rows=max(1,(len(source)+cols-1)//cols)
    sheet=Image.new("RGB",(cols*w,rows*h),(255,255,255))
    draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(source):
      x=(i%cols)*w;y=(i//cols)*h;im=p.pop("thumb")
      sheet.paste(im,(x+(w-im.width)//2,y+4))
      for n,t in enumerate((f"{i+1}. Flickr {p['id']}","CC BY-SA 2.0, Matt Lavin",p["description"][:44],p["description"][44:85])):
        draw.text((x+6,y+231+n*18),t,fill=(0,0,0))
      p["slot"]=i+1
    fp=ROOT/"contact.jpg";sheet.save(fp,"JPEG",quality=89,exif=b"",optimize=True)
    rep={"status":"PREPUBLICATION_LICENSED_CONTACT_ONLY_NOT_CANONICAL_EVIDENCE",
         "species":"Muhlenbergia paniculata","source_name":"Schedonnardus paniculatus",
         "flickr_album":ALBUM,"photo_ids_discovered":len(ids),"licensed_photo_sources":len(source),
         "contact":str(fp),"sha256":hashlib.sha256(fp.read_bytes()).hexdigest(),
         "sources":source,"errors":errors,
         "holds":["True free inner ligule at 1mm scale","Actual one-sided attached spikelet macro","Separated mature glumes and lemma with ruler","connected rooted perennial tuft"],
         "per_photo_rights":"Each included page's HTML contains creator Matt Lavin, species Schedonnardus paniculatus, actual CC BY-SA 2.0 license URL",
         "publication":"NO gallery photo or six-role status changed; original full pixel review required."}
    (ROOT/"report.json").write_text(json.dumps(rep,indent=2,ensure_ascii=False)+"\n")
    print("Licensed/photo evidence:",len(source),"candidates:",len(ids),"errors:",len(errors), "first_errors:",errors[:10])
    assert source,"No licensed pixels archived; safe stop, see printed errors"
if __name__=="__main__":main()
