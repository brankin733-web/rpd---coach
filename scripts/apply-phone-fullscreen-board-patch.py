#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()

def p(rel):
    q=ROOT/rel
    if not q.exists():
        raise SystemExit(f"Phone fullscreen patch missing: {q}")
    return q

def replace(rel,old,new):
    q=p(rel)
    text=q.read_text()
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"Phone fullscreen patch could not find expected source in {rel}: {old[:160]}")
    q.write_text(text.replace(old,new,1))

# Native phone board: hide Android status bar only while the board is open.
# Android back/home/navigation remain untouched.
app=p("components/board/TacticalBoardApp.tsx")
text=app.read_text()
if 'import { StatusBar } from "@capacitor/status-bar";' not in text:
    anchor='import { ScreenOrientation } from "@capacitor/screen-orientation";'
    if anchor not in text:
        raise SystemExit("ScreenOrientation import missing before phone fullscreen patch")
    text=text.replace(anchor,anchor+'\nimport { StatusBar } from "@capacitor/status-bar";',1)

orientation_effect='''  useEffect(()=>{
    void ScreenOrientation.lock({orientation:"landscape"}).catch(()=>{
      const orientation=window.screen.orientation as ScreenOrientation&{lock?:(value:"landscape")=>Promise<void>};
      void orientation?.lock?.("landscape").catch(()=>undefined);
    });
    return()=>{
      void ScreenOrientation.unlock().catch(()=>{
        const orientation=window.screen.orientation as ScreenOrientation&{unlock?:()=>void};
        orientation?.unlock?.();
      });
    };
  },[]);'''

fullscreen_effect=orientation_effect+'''
  useEffect(()=>{
    document.documentElement.classList.add("rpd-native-board-fullscreen");
    void StatusBar.hide().catch(()=>undefined);
    return()=>{
      document.documentElement.classList.remove("rpd-native-board-fullscreen");
      void StatusBar.show().catch(()=>undefined);
    };
  },[]);'''

if 'rpd-native-board-fullscreen' not in text:
    if orientation_effect not in text:
        raise SystemExit("Landscape orientation effect missing before phone fullscreen patch")
    text=text.replace(orientation_effect,fullscreen_effect,1)
app.write_text(text)

package=p("package.json")
text=package.read_text()
if '"@capacitor/status-bar"' not in text:
    anchor='"@capacitor/screen-orientation": "8.0.0",'
    if anchor not in text:
        raise SystemExit("screen-orientation dependency missing before phone fullscreen patch")
    text=text.replace(anchor,anchor+'\n    "@capacitor/status-bar": "8.0.0",',1)
    package.write_text(text)

css=p("app/globals.css")
text=css.read_text()
marker="/* RPD phone full-screen tactics board */"
if marker not in text:
    text += r'''

/* RPD phone full-screen tactics board */
/* Phone landscape only: the board owns the whole app viewport. The Android
   navigation/back/home area is left to the OS and safe-area padding keeps
   RPD controls clear of notches, gesture handles and 3-button navigation. */
@media (orientation:landscape) and (max-height:650px) and (max-width:1100px){
  :root{
    --rpd-safe-left:max(4px,env(safe-area-inset-left));
    --rpd-safe-right:max(4px,env(safe-area-inset-right));
    --rpd-safe-top:max(3px,env(safe-area-inset-top));
    --rpd-safe-bottom:max(3px,env(safe-area-inset-bottom));
    --rpd-phone-rail:54px;
  }

  html.rpd-native-board-fullscreen,
  html.rpd-native-board-fullscreen body{
    width:100%;
    height:100%;
    overflow:hidden;
    overscroll-behavior:none;
    background:#080a0c;
  }

  .rpd-board-app{
    position:fixed;
    inset:0;
    width:100vw;
    height:100dvh;
    min-height:0;
    overflow:hidden;
    padding:0;
    background:#080a0c;
  }

  .rpd-board-app .board-topbar{display:none}

  .rpd-board-app .board-stage-area{
    position:absolute;
    inset:0;
    width:100%;
    height:100%;
    min-height:0;
    max-width:none;
    padding:
      var(--rpd-safe-top)
      calc(var(--rpd-phone-rail) + var(--rpd-safe-right) + 4px)
      var(--rpd-safe-bottom)
      calc(var(--rpd-phone-rail) + var(--rpd-safe-left) + 4px);
    display:grid;
    place-items:center;
  }

  .rpd-board-app .board-canvas-shell.orientation-landscape{
    width:min(
      calc(100vw - (var(--rpd-phone-rail) * 2) - var(--rpd-safe-left) - var(--rpd-safe-right) - 12px),
      calc((100dvh - var(--rpd-safe-top) - var(--rpd-safe-bottom) - 6px) * var(--board-aspect,1.53846))
    );
    max-width:none;
    max-height:calc(100dvh - var(--rpd-safe-top) - var(--rpd-safe-bottom) - 6px);
    height:auto;
    margin:0;
    border-radius:9px;
    box-shadow:0 0 0 1px rgba(255,255,255,.08),0 10px 28px rgba(0,0,0,.38);
  }

  .rpd-board-app .bottom-dock{
    position:fixed;
    z-index:65;
    inset:
      var(--rpd-safe-top)
      var(--rpd-safe-right)
      var(--rpd-safe-bottom)
      var(--rpd-safe-left);
    width:auto;
    height:auto;
    transform:none;
    display:grid;
    grid-template-columns:50px 50px;
    grid-template-rows:repeat(3,50px);
    align-content:center;
    justify-content:space-between;
    gap:6px 0;
    padding:0;
    background:transparent;
    border:0;
    box-shadow:none;
    pointer-events:none;
  }

  .rpd-board-app .bottom-dock button{
    width:50px;
    height:50px;
    min-width:50px;
    min-height:50px;
    padding:0;
    pointer-events:auto;
    border-radius:11px;
    background:rgba(12,13,16,.94);
    border:1px solid rgba(255,255,255,.15);
    box-shadow:0 5px 16px rgba(0,0,0,.38);
    backdrop-filter:blur(12px);
  }

  .rpd-board-app .bottom-dock button b{font-size:17px;line-height:17px}
  .rpd-board-app .bottom-dock button span{font-size:6.5px;letter-spacing:.35px}

  .rpd-board-app .multi-select-toggle{
    top:calc(var(--rpd-safe-top) + 5px);
    right:calc(var(--rpd-phone-rail) + var(--rpd-safe-right) + 8px);
  }

  .rpd-board-app .selection-strip{
    max-width:calc(100vw - (var(--rpd-phone-rail) * 2) - var(--rpd-safe-left) - var(--rpd-safe-right) - 20px);
  }

  .rpd-board-app .animation-quick-controls,
  .rpd-board-app .animation-playback-controls{
    top:calc(var(--rpd-safe-top) + 4px);
    left:50%;
    right:auto;
    bottom:auto;
    transform:translateX(-50%);
    padding:4px;
  }

  .rpd-board-app .animation-quick-controls button,
  .rpd-board-app .animation-playback-controls button{
    height:34px;
    padding:0 10px;
    font-size:8px;
  }

  .rpd-board-app.animation-playback-mode .board-stage-area{
    inset:0;
    width:100%;
    height:100%;
    padding:
      var(--rpd-safe-top)
      var(--rpd-safe-right)
      var(--rpd-safe-bottom)
      var(--rpd-safe-left);
  }

  .rpd-board-app.animation-playback-mode .board-canvas-shell.orientation-landscape{
    width:min(
      calc(100vw - var(--rpd-safe-left) - var(--rpd-safe-right) - 4px),
      calc((100dvh - var(--rpd-safe-top) - var(--rpd-safe-bottom) - 4px) * var(--board-aspect,1.53846))
    );
    max-height:calc(100dvh - var(--rpd-safe-top) - var(--rpd-safe-bottom) - 4px);
  }

  /* The equipment and drawing trays also respect the phone's system-nav edge. */
  .rpd-board-app .sheet-scrim-add,
  .rpd-board-app .sheet-scrim-draw{
    top:var(--rpd-safe-top);
    bottom:var(--rpd-safe-bottom);
    height:auto;
  }
  .rpd-board-app .sheet-scrim-add{
    padding:4px 0 4px calc(var(--rpd-phone-rail) + var(--rpd-safe-left) + 3px);
  }
  .rpd-board-app .sheet-scrim-draw{
    padding:4px calc(var(--rpd-phone-rail) + var(--rpd-safe-right) + 3px) 4px 0;
  }
  .rpd-board-app .sheet-panel-add,
  .rpd-board-app .sheet-panel-draw{
    width:min(260px,39vw);
    height:100%;
    border-radius:11px;
  }

  .rpd-board-app .toast{
    bottom:calc(var(--rpd-safe-bottom) + 6px);
    max-width:calc(100vw - 130px);
  }
}
'''
    css.write_text(text)

print("RPD phone full-screen tactics board patch applied")
