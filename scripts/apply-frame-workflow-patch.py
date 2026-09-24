#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

def path(rel):
    p = ROOT / rel
    if not p.exists():
        raise SystemExit(f"RPD patch missing expected file: {p}")
    return p

def replace(rel, old, new):
    p = path(rel)
    text = p.read_text()
    if new and new in text:
        return
    if old not in text:
        raise SystemExit(f"RPD patch could not find expected source in {rel}: {old[:100]}")
    p.write_text(text.replace(old, new, 1))

def regex(rel, pattern, repl, count=1, flags=0):
    p = path(rel)
    text = p.read_text()
    new, n = re.subn(pattern, repl, text, count=count, flags=flags)
    if n != count:
        raise SystemExit(f"RPD patch expected {count} match(es) in {rel}, found {n}: {pattern[:100]}")
    p.write_text(new)

# Direct frame-by-frame builder on the pitch.
replace(
    "components/board/TacticalBoardApp.tsx",
    '  const [animationPlaying,setAnimationPlaying]=useState(false);',
    '  const [animationPlaying,setAnimationPlaying]=useState(false);\n  const [animationBuildMode,setAnimationBuildMode]=useState(false);\n  const [animationPlaybackMode,setAnimationPlaybackMode]=useState(false);'
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '    setToast(`Frame ${index+1} captured`);\n  }',
    '    setToast(`Frame ${index+1} captured`);\n    setAnimationBuildMode(true);\n    setAnimationPlaybackMode(false);\n    setSheet(null);\n  }'
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '  function stopAnimation(){animationRun.current+=1;setAnimationPlaying(false);setAnimationPreview(null);}',
    '''  function stopAnimation(){animationRun.current+=1;setAnimationPlaying(false);setAnimationPreview(null);}
  function startAnimationPlayback(){
    if(board.animation.frames.length<2){setToast("Capture at least 2 frames to animate");return;}
    setSheet(null);
    setAnimationBuildMode(false);
    setSelectedIds([]);
    setTool("select");
    setAnimationPlaybackMode(true);
    void playAnimation();
  }
  function exitAnimationPlayback(){
    stopAnimation();
    setAnimationPlaybackMode(false);
    setAnimationBuildMode(true);
  }'''
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '<main className="rpd-board-app">',
    '<main className={`rpd-board-app ${animationPlaybackMode?"animation-playback-mode":""}`}>'
)
replace(
    "components/board/TacticalBoardApp.tsx",
    'onCommit={commit} onViewportCommit={viewport=>replacePresent({...board,viewport,updatedAt:now()})} onContextMenu={openContext}',
    'onCommit={commit} onContextMenu={openContext}'
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '''      <BoardCanvas board={displayBoard} selectedIds={selectedIds} multiSelect={multiSelect} tool={tool} drawConfig={drawConfig} onSelect={handleSelect} onSelectMany={setSelectedIds} onCommit={commit} onContextMenu={openContext}/>
''',
    '''      <BoardCanvas board={displayBoard} selectedIds={selectedIds} multiSelect={multiSelect} tool={tool} drawConfig={drawConfig} onSelect={handleSelect} onSelectMany={setSelectedIds} onCommit={commit} onContextMenu={openContext}/>
      {animationBuildMode&&!animationPlaybackMode&&<div className="animation-quick-controls" aria-label="Animation controls">
        <button className="next-frame-button" onClick={captureAnimationFrame}>＋ NEXT FRAME</button>
        <button className="play-animation-button" disabled={board.animation.frames.length<2} onClick={startAnimationPlayback}>▶ PLAY</button>
      </div>}
      {animationPlaybackMode&&<div className="animation-playback-controls">
        <button disabled={animationPlaying} onClick={()=>void playAnimation()}>↺ REPLAY</button>
        <button onClick={exitAnimationPlayback}>✕ EDIT</button>
      </div>}
'''
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '{tool==="select"&&<button className={`multi-select-toggle ${multiSelect?"active":""}`}',
    '{!animationPlaybackMode&&tool==="select"&&<button className={`multi-select-toggle ${multiSelect?"active":""}`}'
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '{selectedIds.length>0&&sheet!=="edit"&&sheet!=="context"&&<>',
    '{!animationPlaybackMode&&selectedIds.length>0&&sheet!=="edit"&&sheet!=="context"&&<>'
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '<nav className="bottom-dock" aria-label="Board controls">',
    '{!animationPlaybackMode&&<nav className="bottom-dock" aria-label="Board controls">'
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '<button className={sheet==="animate"?"active":""} onClick={()=>{setTool("select");setSelectedIds([]);setSheet(sheet==="animate"?null:"animate")}}><b>▶</b><span>PLAY</span></button>',
    '<button className={animationBuildMode?"active":""} onClick={()=>{stopAnimation();setAnimationBuildMode(v=>!v);setAnimationPlaybackMode(false);setTool("select");setSelectedIds([]);setSheet(null)}}><b>▶</b><span>ANIMATE</span></button>'
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '</nav>\n    {sheet&&<div className="sheet-scrim"',
    '</nav>}\n    {sheet&&!animationPlaybackMode&&<div className="sheet-scrim"'
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '{sheet==="pitch"&&<PitchSheet board={board} patchPitch={patchPitch} resetView={()=>replacePresent({...board,viewport:{zoom:1,panX:0,panY:0},updatedAt:now()})}/>}',
    '{sheet==="pitch"&&<PitchSheet board={board} patchPitch={patchPitch}/>}'
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '{sheet==="animate"&&<AnimationSheet board={board} playing={animationPlaying} capture={captureAnimationFrame} play={()=>void playAnimation()} stop={stopAnimation} preview={previewFrame} patch={patchAnimationFrame} remove={removeAnimationFrame}/>}',
    '{sheet==="animate"&&<AnimationSheet board={board} playing={animationPlaying} capture={captureAnimationFrame} play={startAnimationPlayback} stop={stopAnimation} preview={previewFrame} patch={patchAnimationFrame} remove={removeAnimationFrame}/>}'
)
regex(
    "components/board/TacticalBoardApp.tsx",
    r'function PitchSheet\(\{board,patchPitch,resetView\}:\{board:BoardState;patchPitch:\(p:Partial<BoardState\["pitch"\]>\)=>void;resetView:\(\)=>void\}\)\{(.*?)<div className="switch-row"><label><input type="checkbox" checked=\{board\.pitch\.snap\} onChange=\{e=>patchPitch\(\{snap:e\.target\.checked\}\)\}/><span>Smart snapping</span></label><button onClick=\{resetView\}>Reset zoom</button></div></>;\}',
    r'''function PitchSheet({board,patchPitch}:{board:BoardState;patchPitch:(p:Partial<BoardState["pitch"]>)=>void}){\1<div className="switch-row"><label><input type="checkbox" checked={board.pitch.snap} onChange={e=>patchPitch({snap:e.target.checked})}/><span>Smart snapping</span></label></div></>;}''',
)
replace(
    "components/board/TacticalBoardApp.tsx",
    '<div className="sheet-heading"><span>ANIMATE</span><h2>Show the movement.</h2><p>Capture the current picture, move the players, then capture the next frame. RPD Coach animates between them.</p></div><div className="animation-main-actions"><button className="primary" onClick={capture}>＋ Capture frame</button>{playing?<button onClick={stop}>■ Stop</button>:<button disabled={frames.length<2} onClick={play}>▶ Play animation</button>}</div>{frames.length===0?<div className="animation-empty"><b>Start with Frame 1</b><p>Set up the starting picture and tap Capture frame. Then close this sheet, move the objects and capture Frame 2.</p></div>',
    '<div className="sheet-heading"><span>FRAMES</span><h2>Animation frames.</h2><p>Build the movement directly on the pitch with NEXT FRAME. Use this panel only to rename frames, change timing or remove one.</p></div><div className="animation-main-actions"><button className="primary" onClick={capture}>＋ Capture current frame</button>{playing?<button onClick={stop}>■ Stop</button>:<button disabled={frames.length<2} onClick={play}>▶ Play clean animation</button>}</div>{frames.length===0?<div className="animation-empty"><b>Start with Frame 1</b><p>Close this panel, set the starting picture and use CAPTURE FRAME 1 directly below the pitch.</p></div>'
)

# Permanently fitted pitch: remove wheel, pinch, shift-pan and zoom controls.
replace("components/board/BoardCanvas.tsx", '  onViewportCommit: (viewport: BoardState["viewport"]) => void;\n', '')
replace("components/board/BoardCanvas.tsx", 'type PinchGesture = { ids: [number, number]; distance: number; midpoint: { x: number; y: number }; viewport: BoardState["viewport"] };\n', '')
replace(
    "components/board/BoardCanvas.tsx",
    'export default function BoardCanvas({ board, selectedIds, multiSelect, tool, drawConfig, onSelect, onSelectMany, onCommit, onViewportCommit, onContextMenu }: Props) {',
    'export default function BoardCanvas({ board, selectedIds, multiSelect, tool, drawConfig, onSelect, onSelectMany, onCommit, onContextMenu }: Props) {'
)
replace("components/board/BoardCanvas.tsx", '  const pinchRef = useRef<PinchGesture | null>(null);\n', '')
replace("components/board/BoardCanvas.tsx", '  const panRef = useRef<{ pointerId: number; x: number; y: number; viewport: BoardState["viewport"] } | null>(null);\n', '')
replace("components/board/BoardCanvas.tsx", '  const viewRef = useRef(board.viewport);\n', '')
replace(
    "components/board/BoardCanvas.tsx",
    '''  useEffect(() => {
    viewRef.current = board.viewport;
    applyViewport(board.viewport);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [board.viewport, board.pitch.view, board.pitch.orientation, width, height]);

  function viewBoxFor(viewport: BoardState["viewport"]) {
    const zoom = clamp(viewport.zoom, 1, 4);
    const baseX = crop.x * width, baseY = crop.y * height;
    const baseW = crop.width * width, baseH = crop.height * height;
    const w = baseW / zoom, h = baseH / zoom;
    const maxX = Math.max(0, (baseW - w) / 2), maxY = Math.max(0, (baseH - h) / 2);
    const cx = baseX + baseW / 2 + clamp(viewport.panX * baseW, -maxX, maxX);
    const cy = baseY + baseH / 2 + clamp(viewport.panY * baseH, -maxY, maxY);
    return { x: cx - w / 2, y: cy - h / 2, w, h, zoom };
  }

  function applyViewport(viewport: BoardState["viewport"]) {
    const svg = svgRef.current;
    if (!svg) return;
    const box = viewBoxFor(viewport);
    svg.setAttribute("viewBox", `${box.x} ${box.y} ${box.w} ${box.h}`);
    viewRef.current = { ...viewport, zoom: box.zoom };
  }
''',
    '''  useEffect(() => {
    applyViewport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [board.pitch.view, board.pitch.orientation, width, height]);

  function applyViewport() {
    const svg = svgRef.current;
    if (!svg) return;
    const x = crop.x * width, y = crop.y * height;
    const w = crop.width * width, h = crop.height * height;
    svg.setAttribute("viewBox", `${x} ${y} ${w} ${h}`);
  }
'''
)
regex(
    "components/board/BoardCanvas.tsx",
    r'  function registerPointer\(event: ReactPointerEvent<SVGSVGElement>\) \{\n    pointersRef\.current\.set\(event\.pointerId, \{ x: event\.clientX, y: event\.clientY \}\);\n    event\.currentTarget\.setPointerCapture\(event\.pointerId\);\n    if \(pointersRef\.current\.size === 2 && tool === "select"\) \{.*?\n    \}\n  \}',
    '''  function registerPointer(event: ReactPointerEvent<SVGSVGElement>) {
    pointersRef.current.set(event.pointerId, { x: event.clientX, y: event.clientY });
    event.currentTarget.setPointerCapture(event.pointerId);
    if (pointersRef.current.size >= 2) {
      if (dragRef.current) cancelDragVisual();
      marqueeGestureRef.current = null;
      hideMarquee();
    }
  }''',
    flags=re.S
)
replace(
    "components/board/BoardCanvas.tsx",
    '''    if (event.shiftKey && event.pointerType === "mouse" && !multiSelect) {
      panRef.current = { pointerId:event.pointerId,x:event.clientX,y:event.clientY,viewport:{...viewRef.current} }; return;
    }
''',
    ''
)
regex(
    "components/board/BoardCanvas.tsx",
    r'    if \(pinchRef\.current && pointersRef\.current\.size >= 2\) \{.*?\n    \}\n    if \(panRef\.current\?\.pointerId===event\.pointerId\) \{.*?\n    \}\n',
    '',
    flags=re.S
)
replace(
    "components/board/BoardCanvas.tsx",
    '    if (pinchRef.current) { if(pointersRef.current.size<2){pinchRef.current=null;onViewportCommit({...viewRef.current});} releaseCapture(event.pointerId); return; }\n    if (panRef.current?.pointerId===event.pointerId) { panRef.current=null;onViewportCommit({...viewRef.current});releaseCapture(event.pointerId);return; }\n',
    ''
)
replace(
    "components/board/BoardCanvas.tsx",
    'cancelDragVisual();drawRef.current=null;curveRef.current=null;marqueeGestureRef.current=null;pinchRef.current=null;panRef.current=null;hidePreview();hideMarquee();setGuides();',
    'cancelDragVisual();drawRef.current=null;curveRef.current=null;marqueeGestureRef.current=null;hidePreview();hideMarquee();setGuides();'
)
replace(
    "components/board/BoardCanvas.tsx",
    '  function wheelZoom(event:ReactWheelEvent<SVGSVGElement>){event.preventDefault();const delta=event.deltaY>0?.9:1.1;const next={...viewRef.current,zoom:clamp(viewRef.current.zoom*delta,1,4)};applyViewport(next);onViewportCommit(next);}\n\n',
    ''
)
replace("components/board/BoardCanvas.tsx", ' onWheel={wheelZoom}', '')
replace(
    "components/board/BoardCanvas.tsx",
    '    {board.viewport.zoom>1.01&&<button className="zoom-reset" type="button" onClick={()=>onViewportCommit({zoom:1,panX:0,panY:0})}>Fit view</button>}\n',
    ''
)

css = path("app/globals.css")
text = css.read_text()
marker = "/* RPD direct animation workflow */"
if marker not in text:
    text += r'''

/* RPD direct animation workflow */
.animation-quick-controls,.animation-playback-controls{position:fixed;z-index:70;right:14px;bottom:14px;display:flex;gap:7px;padding:6px;border:1px solid rgba(255,255,255,.13);border-radius:13px;background:rgba(14,14,17,.88);box-shadow:0 8px 24px rgba(0,0,0,.34);backdrop-filter:blur(12px)}
.animation-quick-controls button,.animation-playback-controls button{height:40px;border:1px solid #3a3a40;border-radius:9px;background:#25252a;color:#fff;padding:0 13px;font-size:10px;font-weight:950;letter-spacing:.45px;white-space:nowrap}
.animation-quick-controls .next-frame-button{background:#e11b22;border-color:#e11b22}.animation-quick-controls button:disabled,.animation-playback-controls button:disabled{opacity:.38}
.animation-playback-mode{padding-bottom:0}.animation-playback-mode .board-topbar{display:none}.animation-playback-mode .board-stage-area{padding:4px;min-height:100dvh;display:flex;flex-direction:column;justify-content:center}.animation-playback-mode .board-canvas{pointer-events:none}.animation-playback-controls{opacity:.72}.animation-playback-controls:hover,.animation-playback-controls:focus-within{opacity:1}
@media(max-width:680px){.animation-quick-controls,.animation-playback-controls{right:8px;bottom:8px;padding:5px}.animation-quick-controls button,.animation-playback-controls button{height:38px;padding:0 11px;font-size:9px}.animation-playback-mode .board-stage-area{padding:2px}}
'''
    css.write_text(text)

print("RPD direct animation workflow patch applied")
