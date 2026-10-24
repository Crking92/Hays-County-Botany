#!/usr/bin/env python3
"""Archive only an individually rights-verified Forest & Kim Starr historical-variety habit JPEG."""
import io,json,pathlib,urllib.request,urllib.parse,hashlib
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Anatherum/anatherum-tenuispatheum")
card=root/"species.json";data=json.loads(card.read_text())
assert data["id"]=="anatherum-tenuispatheum"
name="Starr_080604-6308_Andropogon_virginicus.jpg"
commons="https://commons.wikimedia.org/wiki/File:"+name
api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:"+name})
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyLearner/1.0 (noncommercial species photo curation; contact: github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req,timeout=40) as res:return res.read(18000000)
result={"source":commons,"added":[],"holds":[]}
try:
 j=json.loads(fetch(api));page=next(iter(j["query"]["pages"].values()));info=page["imageinfo"][0]
 ext=info["extmetadata"];lic=ext.get("LicenseShortName",{}).get("value","")
 artist=ext.get("Artist",{}).get("value","")
 desc=ext.get("ImageDescription",{}).get("value","")
 # Require an explicit attributed Commons license and source describing historic var. pumilus.
 assert "CC BY 3.0" in lic, "license not confirmed: "+lic
 assert "Forest" in artist and "Starr" in artist, "attribution not verified"
 assert "pumilus" in desc, "historical var. pumilus source determination not verified"
 blob=fetch(info["url"])
 with Image.open(io.BytesIO(blob)) as im:im.verify()
 with Image.open(io.BytesIO(blob)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB");im.thumbnail((1800,1800))
  buf=io.BytesIO();im.save(buf,format="JPEG",quality=87,optimize=True);content=buf.getvalue()
 dest=root/"images"/"starr-080604-6308-historic-pumilus-ccby3.jpg"
 dest.write_bytes(content)
 rel="images/"+dest.name
 assert not any(z["file"]==rel for z in data["images"]), "Already archived"
 data["images"].append({"file":rel,"role":"Historical variety-labelled field habit only; species-specific microscopic ID unverified","creator":"Forest & Kim Starr","license":"CC BY 3.0","source_page":commons,"taxonomic_source":"https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:12855-2","source_determination":"Wikimedia Commons source identifies Andropogon glomeratus var. pumilus; mapped by Kew to Anatherum tenuispatheum","photo_status":"HISTORIC_SYNONYM_PROVISIONAL_ANATOMY_HOLD","sha256":hashlib.sha256(content).hexdigest(),"modifications":"Resized to 1800px maximum; EXIF stripped"})
 data.setdefault("visual_comparison",{}).setdefault("items",[]).append({"label":"Starr historical var. pumilus — source habit","scientific_name":"Anatherum tenuispatheum (historical-variety source)","image_url":str(root/rel),"image_fit":"contain","caption":"Source labelled var. pumilus; Kew treats name as a synonym, but the modern identification and microscopic details are not independently verified.","creator":"Forest & Kim Starr","license":"CC BY 3.0","source_page":commons,"markers":[]})
 data.setdefault("curation_status",{})["photo_files_present"]=len(data["images"])
 data["curation_status"]["photo_metadata_count"]=len(data["images"])
 data.setdefault("learner_visual_status",{})["image_count"]=len(data["images"])
 card.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
 result["added"].append({"file":str(dest),"size":len(content),"sha256":hashlib.sha256(content).hexdigest(),"license":lic})
except Exception as e:result["holds"].append(str(e))
pathlib.Path("reports/lane3-anatherum-starr-20261023.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))
