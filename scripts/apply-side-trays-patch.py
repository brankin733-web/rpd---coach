#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

def p(rel):
    target = ROOT / rel
    if not target.exists():
        raise SystemExit(f"Side tray patch missing: {target}")
    return target

def replace(rel, old, new):
    target=p(rel)
    text=target.read_text()
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"Side tray patch could not find expected source in {rel}: {old[:120]}")
    target.write_text(text.replace(old,new,1))

app=p("components/board/TacticalBoardApp.tsx")
text=app.read_text()

# Give the app a state class so wider screens can make room for the open left/right tray.
old='className={`rpd-board-app ${animationPlaybackMode?"animation-playback-mode":""}`}'
new='className={`rpd-board-app ${animationPlaybackMode?"animation-playback-mode":""} ${sheet==="add"?"side-tray-left-open":sheet==="draw"?"side-tray-right-open":""}`}'
if old in text:
    text=text.replace(old,new,1)
elif 'className="rpd-board-app"' in text:
    text=text.replace('className="rpd-board-app"', 'className={`rpd-board-app ${sheet==="add"?"side-tray-left-open":sheet==="draw"?"side-tray-right-open":""}`}',1)

# Tag the modal with its actual sheet type. Add becomes a left drawer, Draw a right drawer.
if 'className={`sheet-scrim sheet-scrim-${sheet}`}' not in text:
    text=text.replace('className="sheet-scrim"', 'className={`sheet-scrim sheet-scrim-${sheet}`}',1)
if 'className={`bottom-sheet sheet-panel-${sheet}`}' not in text:
    text=text.replace('className="bottom-sheet"', 'className={`bottom-sheet sheet-panel-${sheet}`}',1)

app.write_text(text)

css=p("app/globals.css")
text=css.read_text()
marker="/* RPD landscape side trays */"
if marker not in text:
    text += r'''

/* RPD landscape side trays */
@media (orientation:landscape){
  .sheet-scrim-add,.sheet-scrim-draw{
    top:52px;
    background:rgba(0,0,0,.18);
    align-items:stretch;
  }
  .sheet-scrim-add{justify-content:flex-start;padding:8px 0 8px 74px}
  .sheet-scrim-draw{justify-content:flex-end;padding:8px 74px 8px 0}
  .sheet-panel-add,.sheet-panel-draw{
    width:min(330px,31vw);
    max-height:none;
    height:100%;
    margin:0;
    border:1px solid #35353b;
    border-radius:16px;
    padding:13px 12px 18px;
    box-shadow:0 22px 60px rgba(0,0,0,.5);
    background:rgba(20,20,23,.98);
    backdrop-filter:blur(18px);
    overscroll-behavior:contain;
  }
  .sheet-panel-add .sheet-handle,.sheet-panel-draw .sheet-handle{display:none}
  .sheet-panel-add .sheet-heading,.sheet-panel-draw .sheet-heading{padding-top:2px}
  .sheet-panel-add .sheet-heading h2,.sheet-panel-draw .sheet-heading h2{font-size:19px}
  .sheet-panel-add .sheet-heading p,.sheet-panel-draw .sheet-heading p{font-size:11px}
  .sheet-panel-add .quick-row{grid-template-columns:repeat(2,1fr)}
  .sheet-panel-add .quick-row button{min-height:54px}
  .sheet-panel-add .player-grid{grid-template-columns:repeat(2,1fr)}
  .sheet-panel-add .equipment-grid{grid-template-columns:repeat(3,1fr)}
  .sheet-panel-add .asset-grid button{min-height:68px;padding:6px}
  .sheet-panel-add .equipment-palette{width:42px;height:38px}
  .sheet-panel-add .equipment-palette svg{width:40px;height:40px}
  .sheet-panel-add .player-palette{width:36px;height:36px}
  .sheet-panel-add .preset-scroll{grid-auto-columns:112px}
  .sheet-panel-draw .draw-tool-grid{grid-template-columns:repeat(3,1fr)}
  .sheet-panel-draw .draw-tool-grid button{height:58px}
  .sheet-panel-draw .draw-tool-grid button b{font-size:20px}
  .sheet-panel-draw .draw-options{gap:10px;margin-top:10px;padding-top:10px}
  .sheet-panel-draw .segment-control{grid-template-columns:repeat(2,1fr)}
}

@media (orientation:landscape) and (min-width:900px){
  .rpd-board-app .board-stage-area{transition:padding .18s ease}
  .side-tray-left-open .board-stage-area{padding-left:390px;padding-right:78px}
  .side-tray-right-open .board-stage-area{padding-left:78px;padding-right:390px}
  .side-tray-left-open .board-canvas-shell.orientation-landscape,
  .side-tray-right-open .board-canvas-shell.orientation-landscape{max-width:100%}
}

@media (orientation:landscape) and (max-width:899px){
  .sheet-scrim-add{padding-left:60px}
  .sheet-scrim-draw{padding-right:60px}
  .sheet-panel-add,.sheet-panel-draw{width:min(265px,42vw);border-radius:13px}
  .sheet-panel-add .sheet-heading p,.sheet-panel-draw .sheet-heading p{display:none}
  .sheet-panel-add .tray-label{margin-top:10px}
  .sheet-panel-add .equipment-grid{grid-template-columns:repeat(2,1fr)}
  .sheet-panel-draw .draw-tool-grid{grid-template-columns:repeat(2,1fr)}
}

@media (orientation:landscape) and (max-height:480px){
  .sheet-scrim-add,.sheet-scrim-draw{top:44px;padding-top:5px;padding-bottom:5px}
  .sheet-panel-add,.sheet-panel-draw{padding:10px 9px 12px}
  .sheet-panel-add .sheet-heading,.sheet-panel-draw .sheet-heading{padding-bottom:7px}
  .sheet-panel-add .sheet-heading h2,.sheet-panel-draw .sheet-heading h2{font-size:17px}
  .sheet-panel-add .quick-row button{min-height:48px}
  .sheet-panel-add .asset-grid button{min-height:60px}
  .sheet-panel-draw .draw-tool-grid button{height:52px}
}
'''
    css.write_text(text)

print("RPD landscape side tray patch applied")
