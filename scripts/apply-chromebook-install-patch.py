#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()

def p(rel):
    q=ROOT/rel
    if not q.exists():
        raise SystemExit(f"Chromebook install patch missing: {q}")
    return q

# Create a proper ChromeOS/PWA install control.
component=ROOT/"components/app/InstallRPDCoach.tsx"
component.parent.mkdir(parents=True,exist_ok=True)
component.write_text(r'''"use client";

import { useEffect, useState } from "react";

type InstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed"; platform: string }>;
};

export default function InstallRPDCoach(){
  const [promptEvent,setPromptEvent]=useState<InstallPromptEvent|null>(null);
  const [installed,setInstalled]=useState(false);
  const [message,setMessage]=useState("");

  useEffect(()=>{
    const standalone=window.matchMedia("(display-mode: standalone)").matches ||
      Boolean((navigator as Navigator & { standalone?: boolean }).standalone);
    setInstalled(standalone);

    const beforeInstall=(event:Event)=>{
      event.preventDefault();
      setPromptEvent(event as InstallPromptEvent);
    };
    const appInstalled=()=>{
      setInstalled(true);
      setPromptEvent(null);
      setMessage("RPD Coach is installed.");
    };

    window.addEventListener("beforeinstallprompt",beforeInstall);
    window.addEventListener("appinstalled",appInstalled);
    return()=>{
      window.removeEventListener("beforeinstallprompt",beforeInstall);
      window.removeEventListener("appinstalled",appInstalled);
    };
  },[]);

  if(installed) return null;

  async function install(){
    if(promptEvent){
      await promptEvent.prompt();
      const choice=await promptEvent.userChoice;
      if(choice.outcome==="accepted"){
        setMessage("Installing RPD Coach…");
      }else{
        setMessage("Install cancelled.");
      }
      setPromptEvent(null);
      return;
    }
    setMessage("In Chrome, open ⋮ → Cast, save and share → Install RPD Coach.");
  }

  return <section className="install-rpd-card" aria-label="Install RPD Coach">
    <div className="install-rpd-copy">
      <span>CHROMEBOOK APP</span>
      <b>Install the latest RPD Coach</b>
      <small>Installs from this live version and stays up to date automatically.</small>
      {message&&<em role="status">{message}</em>}
    </div>
    <button type="button" onClick={install}>Install RPD Coach</button>
  </section>;
}
''')

home=p("components/app/HomeScreen.tsx")
text=home.read_text()
if 'import InstallRPDCoach from "./InstallRPDCoach";' not in text:
    text=text.replace('import BoardThumb from "./BoardThumb";','import BoardThumb from "./BoardThumb";\nimport InstallRPDCoach from "./InstallRPDCoach";',1)
if '<InstallRPDCoach/>' not in text:
    text=text.replace('''    <section className="home-content">''','''    <section className="home-content">
      <InstallRPDCoach/>''',1)
home.write_text(text)

css=p("app/globals.css")
text=css.read_text()
marker="/* RPD Chromebook install card */"
if marker not in text:
    text += r'''

/* RPD Chromebook install card */
.install-rpd-card{margin:4px 0 18px;padding:14px 15px;border:1px solid rgba(225,27,34,.42);border-radius:16px;background:linear-gradient(135deg,rgba(225,27,34,.12),rgba(25,25,29,.96));display:flex;align-items:center;justify-content:space-between;gap:14px;box-shadow:0 12px 30px rgba(0,0,0,.22)}
.install-rpd-copy{display:grid;gap:3px;min-width:0}.install-rpd-copy>span{font-size:9px;letter-spacing:1.4px;font-weight:950;color:#ff5960}.install-rpd-copy>b{font-size:15px}.install-rpd-copy>small{font-size:10px;line-height:1.35;color:#a8a8b0}.install-rpd-copy>em{font-style:normal;font-size:10px;color:#e6e2dc;margin-top:2px}
.install-rpd-card button{flex:0 0 auto;min-height:44px;border:0;border-radius:11px;background:#e11b22;color:#fff;padding:0 15px;font-size:11px;font-weight:950}
@media(max-width:620px){.install-rpd-card{align-items:stretch;flex-direction:column}.install-rpd-card button{width:100%;min-height:48px}}
'''
    css.write_text(text)

print("RPD Chromebook install patch applied")
