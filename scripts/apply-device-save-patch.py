#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()

def p(rel):
    q=ROOT/rel
    if not q.exists():
        raise SystemExit(f"Device save patch missing: {q}")
    return q

def replace(rel,old,new):
    q=p(rel)
    text=q.read_text()
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"Device save patch could not find expected source in {rel}: {old[:140]}")
    q.write_text(text.replace(old,new,1))

app=p("components/board/TacticalBoardApp.tsx")
text=app.read_text()

helper='''  async function saveDrillToDevice(){
    if(!pro){setSheet(null);setToast("Save to device is an RPD Coach Pro feature");router.push("/membership/?from=device-save");return;}
    const svg=document.querySelector(".board-canvas") as SVGSVGElement|null;
    if(!svg){setToast("Could not capture this drill");return;}
    try{
      const clone=svg.cloneNode(true) as SVGSVGElement;
      clone.setAttribute("xmlns","http://www.w3.org/2000/svg");
      clone.removeAttribute("style");
      const vb=svg.viewBox?.baseVal;
      const aspect=vb&&vb.width>0&&vb.height>0?vb.width/vb.height:(board.pitch.orientation==="landscape"?1.55:.65);
      const width=1800;
      const height=Math.max(900,Math.round(width/aspect));
      clone.setAttribute("width",String(width));
      clone.setAttribute("height",String(height));
      const source=new XMLSerializer().serializeToString(clone);
      const svgBlob=new Blob([source],{type:"image/svg+xml;charset=utf-8"});
      const imageUrl=URL.createObjectURL(svgBlob);
      const image=new Image();
      await new Promise<void>((resolve,reject)=>{image.onload=()=>resolve();image.onerror=()=>reject(new Error("image"));image.src=imageUrl;});
      const canvas=document.createElement("canvas");
      canvas.width=width;
      canvas.height=height;
      const ctx=canvas.getContext("2d");
      if(!ctx)throw new Error("canvas");
      ctx.fillStyle="#0a0a0c";
      ctx.fillRect(0,0,width,height);
      ctx.drawImage(image,0,0,width,height);
      URL.revokeObjectURL(imageUrl);
      const png=await new Promise<Blob>((resolve,reject)=>canvas.toBlob(blob=>blob?resolve(blob):reject(new Error("png")),"image/png",.96));
      const title=(board.title.trim()||"RPD-Coach-Drill").replace(/[^a-z0-9-_]+/gi,"-").replace(/^-+|-+$/g,"").slice(0,80)||"RPD-Coach-Drill";
      const filename=`${title}.png`;
      const file=new File([png],filename,{type:"image/png"});
      const nav=navigator as Navigator&{canShare?:(data:ShareData)=>boolean;share?:(data:ShareData)=>Promise<void>};
      if(nav.share&&nav.canShare?.({files:[file]})){
        await nav.share({title:board.title.trim()||"RPD Coach Drill",text:"Built with RPD Coach",files:[file]});
        setToast("Drill ready to save or share");
      }else{
        const url=URL.createObjectURL(png);
        const anchor=document.createElement("a");
        anchor.href=url;
        anchor.download=filename;
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        window.setTimeout(()=>URL.revokeObjectURL(url),1500);
        setToast("Drill saved to Downloads");
      }
    }catch(error){
      if(error instanceof DOMException&&error.name==="AbortError")return;
      setToast("Could not save drill to this device");
    }
  }
'''

if helper not in text:
    anchor='''  function save(type:"drill"|"tactic",addSession=false){'''
    idx=text.find(anchor)
    if idx<0: raise SystemExit("Could not find board save function")
    text=text[:idx]+helper+text[idx:]

old='{sheet==="save"&&<SaveSheet board={board} form={saveForm} setForm={setSaveForm} save={save}/>} '
new='{sheet==="save"&&<SaveSheet board={board} form={saveForm} setForm={setSaveForm} save={save} saveToDevice={()=>void saveDrillToDevice()}/>} '
if new not in text:
    if old not in text: raise SystemExit("Could not patch SaveSheet call")
    text=text.replace(old,new,1)

old_sig='''function SaveSheet({board,form,setForm,save}:{board:BoardState;form:SaveForm;setForm:(f:SaveForm)=>void;save:(t:"drill"|"tactic",s?:boolean)=>void})'''
new_sig='''function SaveSheet({board,form,setForm,save,saveToDevice}:{board:BoardState;form:SaveForm;setForm:(f:SaveForm)=>void;save:(t:"drill"|"tactic",s?:boolean)=>void;saveToDevice:()=>void})'''
if new_sig not in text:
    if old_sig not in text: raise SystemExit("Could not patch SaveSheet signature")
    text=text.replace(old_sig,new_sig,1)

old_actions='''<div className="save-actions"><button onClick={()=>save("drill")}>Save as Drill</button><button onClick={()=>save("tactic")}>Save as Tactic</button><button className="primary" onClick={()=>save("drill",true)}>Save + Add to Session</button></div>'''
new_actions='''<div className="save-device-card"><div><span>PRO • DEVICE EXPORT</span><b>Keep the drill on your phone</b><small>Saves a high-quality PNG of the full tactics board. On supported phones you can choose Files, Photos, WhatsApp or another app.</small></div><button type="button" onClick={saveToDevice}>↓ SAVE TO PHONE</button></div><div className="save-actions"><button onClick={()=>save("drill")}>Save as Drill</button><button onClick={()=>save("tactic")}>Save as Tactic</button><button className="primary" onClick={()=>save("drill",true)}>Save + Add to Session</button></div>'''
if new_actions not in text:
    if old_actions not in text: raise SystemExit("Could not patch save actions")
    text=text.replace(old_actions,new_actions,1)

app.write_text(text)

css=p("app/globals.css")
text=css.read_text()
if "/* RPD paid device save */" not in text:
    text += r'''

/* RPD paid device save */
.save-device-card{margin:12px 0;padding:12px;border:1px solid rgba(225,27,34,.48);border-radius:14px;background:linear-gradient(135deg,rgba(225,27,34,.12),rgba(22,22,26,.96));display:flex;align-items:center;justify-content:space-between;gap:12px}
.save-device-card>div{display:grid;gap:3px;min-width:0}.save-device-card span{font-size:8px;letter-spacing:1.25px;font-weight:950;color:#ff5e65}.save-device-card b{font-size:14px}.save-device-card small{max-width:520px;color:#a8a8b0;font-size:10px;line-height:1.35}
.save-device-card button{flex:0 0 auto;min-height:44px;border:1px solid #e11b22;border-radius:10px;background:#e11b22;color:#fff;padding:0 14px;font-size:10px;font-weight:950;letter-spacing:.4px}
@media(max-width:680px){.save-device-card{align-items:stretch;flex-direction:column}.save-device-card button{width:100%;min-height:48px}}
'''
    css.write_text(text)

print("RPD Pro save-to-device patch applied")
