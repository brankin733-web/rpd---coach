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
    '''if(recovered?.id){const ready=cloneBoard(recovered);if(new URLSearchParams(window.location.search).get("fit")==="full"){ready.pitch={...ready.pitch,view:"full",orientation:"landscape"};ready.viewport={zoom:1,panX:0,panY:0};}setHistory({past:[],present:ready,future:[]});if(requested)setSaveForm(current=>({...current,age:requested.age||"",players:requested.players||"",duration:requested.duration||10,area:requested.area||"",organisation:requested.organisation||"",coachingPoints:requested.coachingPoints||"",keyTriggers:requested.keyTriggers||"",progressions:requested.progressions||"",notes:requested.notes||""}));}else{const fresh=createBlankBoard();fresh.pitch.orientation="landscape";fresh.pitch.view="full";setHistory({past:[],present:fresh,future:[]});}setSavedBoards(boards);'''
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
    'import { useRouter } from "next/navigation";',
    'import { useRouter } from "next/navigation";\nimport { ScreenOrientation } from "@capacitor/screen-orientation";'
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '  const [animationPlaybackMode,setAnimationPlaybackMode]=useState(false);',
    '''  const [animationPlaybackMode,setAnimationPlaybackMode]=useState(false);
  useEffect(()=>{
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
)


replace(
    "components/app/AIDrillBuilderScreen.tsx",
    'router.push("/board/");',
    'router.push("/board/?fit=full");'
)
replace(
    "components/app/SessionsScreen.tsx",
    'href={\`/board/?open=\${encodeURIComponent(item.boardId)}\`}',
    'href={\`/board/?open=\${encodeURIComponent(item.boardId)}&fit=full\`}'
)

package = p("package.json")
package_text = package.read_text()
if '"@capacitor/screen-orientation"' not in package_text:
    package_text = package_text.replace('"@capacitor/core": "8.5.2",', '"@capacitor/core": "8.5.2",\n    "@capacitor/screen-orientation": "8.0.0",')
    package.write_text(package_text)

css = p("app/globals.css")
text = css.read_text()
marker = "/* RPD landscape board workspace */"
if marker not in text:
    text += r'''

/* RPD landscape board workspace */
.rpd-board-app{width:100%;max-width:none}
.board-stage-area{width:100%}
.board-canvas-shell{contain:layout paint}
@media (orientation:landscape){
  .rpd-board-app{height:100dvh;min-height:100dvh;padding:0;overflow:hidden}
  .board-topbar{height:50px;padding:5px max(8px,env(safe-area-inset-right)) 5px max(8px,env(safe-area-inset-left))}
  .board-stage-area{height:calc(100dvh - 50px);max-width:none;padding:6px 76px;display:grid;place-items:center}
  .board-canvas-shell.orientation-landscape{width:min(calc(100vw - 164px),calc((100dvh - 62px) * var(--board-aspect,1.53846)));max-width:calc(100vw - 164px);height:auto;max-height:calc(100dvh - 62px);margin:auto;border-radius:14px}
  .bottom-dock{position:fixed;z-index:45;inset:50% 0 auto 0;width:100%;height:auto;transform:translateY(-50%);display:grid;grid-template-columns:60px 60px;grid-template-rows:repeat(3,60px);justify-content:space-between;gap:8px 0;padding:0 8px;background:transparent;border:0;border-radius:0;box-shadow:none;backdrop-filter:none;pointer-events:none}
  .bottom-dock button{width:60px;height:60px;min-width:60px;min-height:60px;pointer-events:auto;border:1px solid rgba(255,255,255,.16);border-radius:14px;background:rgba(14,14,17,.94);box-shadow:0 10px 26px rgba(0,0,0,.34);backdrop-filter:blur(14px)}
  .bottom-dock button b{font-size:20px;line-height:20px}.bottom-dock button span{font-size:8px;letter-spacing:.45px}
  .bottom-dock button.active{background:#2a1c20;border-color:rgba(225,27,34,.72)}
  .bottom-dock button:nth-child(1){grid-column:1;grid-row:1}.bottom-dock button:nth-child(2){grid-column:2;grid-row:1}.bottom-dock button:nth-child(3){grid-column:1;grid-row:2}.bottom-dock button:nth-child(4){grid-column:2;grid-row:2}.bottom-dock button:nth-child(5){grid-column:1;grid-row:3}.bottom-dock button:nth-child(6){grid-column:2;grid-row:3}
  .animation-build-toolbar,.animation-playback-toolbar{max-width:calc(100vw - 164px)}
  .animation-playback-mode .board-stage-area{height:100dvh;padding:4px 12px}
  .animation-playback-mode .board-canvas-shell.orientation-landscape{width:min(calc(100vw - 24px),calc((100dvh - 8px) * var(--board-aspect,1.53846)));max-width:calc(100vw - 24px);max-height:calc(100dvh - 8px)}
}
@media (orientation:landscape) and (max-height:520px){
  .board-topbar{height:44px;padding-block:3px}
  .brand-lockup b{font-size:16px}.brand-lockup span{font-size:8px}
  .board-stage-area{height:calc(100dvh - 44px);padding:4px 66px}
  .board-canvas-shell.orientation-landscape{width:min(calc(100vw - 142px),calc((100dvh - 52px) * var(--board-aspect,1.53846)));max-width:calc(100vw - 142px);max-height:calc(100dvh - 52px)}
  .bottom-dock{grid-template-columns:52px 52px;grid-template-rows:repeat(3,52px);gap:6px 0;padding-inline:7px}
  .bottom-dock button{width:52px;height:52px;min-width:52px;min-height:52px;border-radius:12px}
  .bottom-dock button b{font-size:18px}.bottom-dock button span{font-size:7px}
}
@media (orientation:portrait){
  .rpd-board-app::before{content:"Rotate your phone to use the tactics board";position:fixed;z-index:9999;inset:0;display:grid;place-items:center;padding:32px;text-align:center;background:#0a0a0c;color:#fff;font-size:20px;font-weight:900}
}
'''
    css.write_text(text)

print("RPD landscape board patch applied")
