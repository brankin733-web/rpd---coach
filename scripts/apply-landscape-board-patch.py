#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

def p(rel):
    target = ROOT / rel
    if not target.exists():
        raise SystemExit(f"Landscape patch missing: {target}")
    return target

def replace(rel, old, new):
    target = p(rel)
    text = target.read_text()
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"Landscape patch could not find expected source in {rel}: {old[:120]}")
    target.write_text(text.replace(old, new, 1))

replace(
    "components/board/TacticalBoardApp.tsx",
    '''if(recovered?.id){setHistory({past:[],present:cloneBoard(recovered),future:[]});if(requested)setSaveForm(current=>({...current,age:requested.age||"",players:requested.players||"",duration:requested.duration||10,area:requested.area||"",organisation:requested.organisation||"",coachingPoints:requested.coachingPoints||"",keyTriggers:requested.keyTriggers||"",progressions:requested.progressions||"",notes:requested.notes||""}));}else if(window.matchMedia("(max-width:680px)").matches){const fresh=createBlankBoard();fresh.pitch.orientation="portrait";setHistory({past:[],present:fresh,future:[]});}setSavedBoards(boards);''',
    '''if(recovered?.id){setHistory({past:[],present:cloneBoard(recovered),future:[]});if(requested)setSaveForm(current=>({...current,age:requested.age||"",players:requested.players||"",duration:requested.duration||10,area:requested.area||"",organisation:requested.organisation||"",coachingPoints:requested.coachingPoints||"",keyTriggers:requested.keyTriggers||"",progressions:requested.progressions||"",notes:requested.notes||""}));}else{const fresh=createBlankBoard();fresh.pitch.orientation="landscape";setHistory({past:[],present:fresh,future:[]});}setSavedBoards(boards);'''
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '''function newBoard(){const fresh=createBlankBoard();if(typeof window!=="undefined"&&window.matchMedia("(max-width:680px)").matches)fresh.pitch.orientation="portrait";setHistory({past:[],present:fresh,future:[]});''',
    '''function newBoard(){const fresh=createBlankBoard();fresh.pitch.orientation="landscape";setHistory({past:[],present:fresh,future:[]});'''
)

# Keep the app portrait-friendly outside the board. The board itself requests
# landscape while mounted and releases that request when the coach leaves it.
replace(
    "components/board/TacticalBoardApp.tsx",
    '  const [animationPlaybackMode,setAnimationPlaybackMode]=useState(false);',
    '''  const [animationPlaybackMode,setAnimationPlaybackMode]=useState(false);
  useEffect(()=>{
    const orientation=window.screen.orientation as ScreenOrientation&{
      lock?:(value:"landscape")=>Promise<void>;
      unlock?:()=>void;
    };
    void orientation?.lock?.("landscape").catch(()=>undefined);
    return()=>orientation?.unlock?.();
  },[]);'''
)

css = p("app/globals.css")
text = css.read_text()
marker = "/* RPD landscape board workspace */"
if marker not in text:
    text += r'''

/* RPD landscape board workspace */
@media (orientation:landscape){
  .rpd-board-app{min-height:100dvh;padding-bottom:0}
  .board-topbar{height:52px;padding:6px 10px}
  .board-stage-area{max-width:1500px;padding:8px 78px 14px}
  .board-canvas-shell.orientation-landscape{width:100%;max-width:min(1280px,calc(100vw - 172px));max-height:calc(100dvh - 72px);margin-inline:auto;border-radius:14px}
  .bottom-dock{
    position:fixed;
    z-index:45;
    top:50%;
    left:0;
    right:0;
    bottom:auto;
    width:100%;
    height:auto;
    transform:translateY(-50%);
    display:grid;
    grid-template-columns:60px 60px;
    grid-template-rows:repeat(3,60px);
    justify-content:space-between;
    gap:8px 0;
    padding:0 8px;
    background:transparent;
    border:0;
    border-radius:0;
    box-shadow:none;
    backdrop-filter:none;
    pointer-events:none;
  }
  .bottom-dock button{
    width:60px;
    height:60px;
    min-width:60px;
    min-height:60px;
    pointer-events:auto;
    border:1px solid rgba(255,255,255,.16);
    border-radius:14px;
    background:rgba(14,14,17,.94);
    box-shadow:0 10px 26px rgba(0,0,0,.34);
    backdrop-filter:blur(14px);
  }
  .bottom-dock button b{font-size:20px;line-height:20px}
  .bottom-dock button span{font-size:8px;letter-spacing:.45px}
  .bottom-dock button.active{background:#2a1c20;border-color:rgba(225,27,34,.72);box-shadow:0 0 0 1px rgba(225,27,34,.2),0 10px 26px rgba(0,0,0,.34)}
  .bottom-dock button:nth-child(1){grid-column:1;grid-row:1}
  .bottom-dock button:nth-child(2){grid-column:2;grid-row:1}
  .bottom-dock button:nth-child(3){grid-column:1;grid-row:2}
  .bottom-dock button:nth-child(4){grid-column:2;grid-row:2}
  .bottom-dock button:nth-child(5){grid-column:1;grid-row:3}
  .bottom-dock button:nth-child(6){grid-column:2;grid-row:3}
  .animation-build-toolbar{max-width:min(1280px,calc(100vw - 172px))}
  .animation-playback-toolbar{max-width:min(1280px,calc(100vw - 172px))}
  .animation-playback-mode .board-stage-area{padding-inline:12px}
  .animation-playback-mode .board-canvas-shell.orientation-landscape{max-width:min(1380px,calc(100vw - 24px));max-height:calc(100dvh - 86px)}
}

@media (orientation:landscape) and (max-height:520px){
  .board-topbar{height:44px;padding-block:4px}
  .brand-lockup b{font-size:17px}.brand-lockup span{font-size:8px}
  .board-stage-area{padding:6px 68px 8px}
  .board-canvas-shell.orientation-landscape{max-width:min(1180px,calc(100vw - 148px));max-height:calc(100dvh - 54px)}
  .bottom-dock{grid-template-columns:52px 52px;grid-template-rows:repeat(3,52px);gap:6px 0;padding-inline:7px}
  .bottom-dock button{width:52px;height:52px;min-width:52px;min-height:52px;border-radius:12px}
  .bottom-dock button b{font-size:18px}.bottom-dock button span{font-size:7px}
  .animation-build-toolbar{max-width:min(1180px,calc(100vw - 148px));padding:7px 9px;margin-top:6px}
  .animation-build-copy small{display:none}
}
'''
    css.write_text(text)

print("RPD landscape board patch applied")
