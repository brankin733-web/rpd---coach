#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

def read(rel):
    return (ROOT / rel).read_text()

def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)

def replace(rel, old, new, marker=None):
    p = ROOT / rel
    text = p.read_text()
    if marker and marker in text:
        return
    if old not in text:
        raise SystemExit(f"RPD patch could not find expected source in {rel}")
    p.write_text(text.replace(old, new, 1))

# Animation timeline: one clean Play action, no inline playback behind editor chrome.
replace(
    "src/components/board/AnimationTimeline.tsx",
    'export function AnimationTimeline({ player }: { player: AnimationPlayer }) {',
    'export function AnimationTimeline({ player, onPlayRequest }: { player: AnimationPlayer; onPlayRequest: () => void }) {',
    "onPlayRequest"
)
replace(
    "src/components/board/AnimationTimeline.tsx",
    '<button type="button" className="play-button" disabled={board.frames.length < 2} onClick={player.isPlaying ? player.pause : player.play}>{player.isPlaying ? "Ⅱ Pause" : "▶ Play"}</button>',
    '<button type="button" className="play-button" disabled={board.frames.length < 2} onClick={onPlayRequest}>▶ Play Animation</button>',
    "▶ Play Animation"
)
replace(
    "src/components/board/AnimationTimeline.tsx",
    '<button type="button" onClick={player.restart}>↺</button>',
    '<button type="button" onClick={() => { player.restart(); player.clearPreview(); }}>↺</button>',
    "player.restart(); player.clearPreview();"
)
replace(
    "src/components/board/AnimationTimeline.tsx",
    '>+ Frame</button>',
    '>+ New Frame</button>',
    "+ New Frame"
)

# Dedicated clean playback overlay.
write("src/components/board/AnimationPlaybackOverlay.tsx", '''"use client";

import { PitchSurface } from "./PitchSurface";
import { useBoardStore } from "@/store/boardStore";
import type { BoardScene } from "@/types/board";

type AnimationPlayer = {
  isPlaying: boolean;
  scene: BoardScene | null;
  progress: number;
  play: () => void;
  pause: () => void;
  restart: () => void;
  seek: (ratio: number) => void;
  clearPreview: () => void;
};

export function AnimationPlaybackOverlay({ player, onClose }: { player: AnimationPlayer; onClose: () => void }) {
  const board = useBoardStore((s) => s.board);
  const firstFrame = board.frames[0];
  const scene = player.scene ?? (firstFrame ? { objects: firstFrame.objects, drawings: firstFrame.drawings } : null);

  return (
    <div className="animation-playback-overlay" role="dialog" aria-modal="true" aria-label="Animation playback">
      <div className="animation-playback-shell">
        <div className="animation-playback-head">
          <div>
            <span>RPD ANIMATION</span>
            <strong>{board.title || "Animated Drill"}</strong>
            <small>{board.frames.length} frame{board.frames.length === 1 ? "" : "s"} • clean playback</small>
          </div>
          <button type="button" onClick={onClose}>Back to edit</button>
        </div>

        <div className="animation-playback-pitch">
          <PitchSurface playbackScene={scene} interactionDisabled />
        </div>

        <div className="animation-playback-controls">
          <button type="button" className="primary" onClick={player.isPlaying ? player.pause : player.play}>
            {player.isPlaying ? "Ⅱ Pause" : "▶ Play"}
          </button>
          <button type="button" onClick={player.restart}>↺ Restart</button>
          <input
            aria-label="Animation progress"
            type="range"
            min="0"
            max="1000"
            value={Math.round(player.progress * 1000)}
            onChange={(event) => player.seek(Number(event.target.value) / 1000)}
          />
          <span>{Math.round(player.progress * 100)}%</span>
        </div>
      </div>
    </div>
  );
}
''')

# Board shell: Next Frame on the working screen, clean playback mode, and no zoom controls.
replace(
    "src/components/board/BoardShell.tsx",
    'import { AnimationTimeline } from "./AnimationTimeline";',
    'import { AnimationTimeline } from "./AnimationTimeline";\nimport { AnimationPlaybackOverlay } from "./AnimationPlaybackOverlay";',
    "AnimationPlaybackOverlay"
)
replace(
    "src/components/board/BoardShell.tsx",
    '  const [drillMessage, setDrillMessage] = useState<string | null>(null);',
    '  const [drillMessage, setDrillMessage] = useState<string | null>(null);\n  const [animationPlaybackOpen, setAnimationPlaybackOpen] = useState(false);',
    "animationPlaybackOpen"
)
replace(
    "src/components/board/BoardShell.tsx",
    '  const buildMode = useBoardStore((s) => s.buildMode);',
    '  const buildMode = useBoardStore((s) => s.buildMode);\n  const currentFrameId = useBoardStore((s) => s.currentFrameId);',
    "currentFrameId = useBoardStore"
)
replace(
    "src/components/board/BoardShell.tsx",
    '  const setPitchOverlay = useBoardStore((s) => s.setPitchOverlay);\n  const zoomBy = useBoardStore((s) => s.zoomBy);\n  const resetViewport = useBoardStore((s) => s.resetViewport);',
    '  const setPitchOverlay = useBoardStore((s) => s.setPitchOverlay);\n  const addFrame = useBoardStore((s) => s.addFrame);\n  const selectFrame = useBoardStore((s) => s.selectFrame);',
    "const addFrame = useBoardStore"
)
replace(
    "src/components/board/BoardShell.tsx",
    '  const selectionCount = selectedIds.length || (selectedId ? 1 : 0);',
    '  const selectionCount = selectedIds.length || (selectedId ? 1 : 0);\n  const currentFrameIndex = Math.max(0, board.frames.findIndex((frame) => frame.id === currentFrameId));',
    "currentFrameIndex"
)
replace(
    "src/components/board/BoardShell.tsx",
    '  const makeCheckpoint = async () => {',
    '''  const goToNextFrame = () => {
    if (previewLocked || buildMode !== "animate") return;
    player.clearPreview();
    const index = board.frames.findIndex((frame) => frame.id === currentFrameId);
    if (index >= 0 && index < board.frames.length - 1) {
      selectFrame(board.frames[index + 1].id);
      return;
    }
    addFrame();
  };

  const openAnimationPlayback = () => {
    if (board.frames.length < 2) return;
    setEquipmentOpen(false);
    setDrawingOpen(false);
    clearSelection();
    selectDrawingTool(null);
    player.restart();
    setAnimationPlaybackOpen(true);
    player.play();
  };

  const closeAnimationPlayback = () => {
    player.pause();
    player.clearPreview();
    setAnimationPlaybackOpen(false);
  };

  const makeCheckpoint = async () => {''',
    "const goToNextFrame"
)
replace(
    "src/components/board/BoardShell.tsx",
    '''        <div className="zoom-controls" aria-label="Zoom controls">
          <button type="button" aria-label="Zoom out" onClick={() => zoomBy(0.85)}>−</button>
          <span>{Math.round(board.viewport.scale * 100)}%</span>
          <button type="button" aria-label="Zoom in" onClick={() => zoomBy(1.18)}>+</button>
          <button type="button" className="fit-button" onClick={resetViewport}>Fit</button>
        </div>
''',
    '',
    'aria-label="Zoom controls"'
)
replace(
    "src/components/board/BoardShell.tsx",
    '''          <PitchSurface playbackScene={buildMode === "animate" ? player.scene : null} interactionDisabled={previewLocked || drillLoading} />

          <div className="board-toolbar board-toolbar-bottom" aria-label="Board tools">''',
    '''          <PitchSurface playbackScene={buildMode === "animate" ? player.scene : null} interactionDisabled={previewLocked || drillLoading} />

          {buildMode === "animate" && !animationPlaybackOpen && (
            <div className="animation-quick-next">
              <div>
                <span>FRAME {currentFrameIndex + 1} OF {Math.max(1, board.frames.length)}</span>
                <strong>Move the players, then go straight to the next frame.</strong>
                <small>Your current positions are captured automatically — no save menu needed.</small>
              </div>
              <button type="button" disabled={previewLocked || drillLoading} onClick={goToNextFrame}>NEXT FRAME →</button>
            </div>
          )}

          <div className="board-toolbar board-toolbar-bottom" aria-label="Board tools">''',
    "animation-quick-next"
)
replace(
    "src/components/board/BoardShell.tsx",
    '{buildMode === "animate" && <AnimationTimeline player={player} />}',
    '{buildMode === "animate" && <AnimationTimeline player={player} onPlayRequest={openAnimationPlayback} />}',
    "onPlayRequest={openAnimationPlayback}"
)
replace(
    "src/components/board/BoardShell.tsx",
    '      {drawerOpen && <button className="drawer-scrim" type="button" aria-label="Close tool drawer" onClick={() => { setEquipmentOpen(false); setDrawingOpen(false); }} />}',
    '''      {drawerOpen && <button className="drawer-scrim" type="button" aria-label="Close tool drawer" onClick={() => { setEquipmentOpen(false); setDrawingOpen(false); }} />}

      {animationPlaybackOpen && (
        <AnimationPlaybackOverlay player={player} onClose={closeAnimationPlayback} />
      )}''',
    "onClose={closeAnimationPlayback}"
)

# Pitch surface: permanently fit the whole pitch. No mouse-wheel zoom, pinch zoom, or pan.
pitch = ROOT / "src/components/board/PitchSurface.tsx"
text = pitch.read_text()
if "Pinch to zoom" in text or "const pinchRef" in text:
    text = text.replace('''function distance(a: Touch, b: Touch) {
  return Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
}

function center(a: Touch, b: Touch): Point {
  return { x: (a.clientX + b.clientX) / 2, y: (a.clientY + b.clientY) / 2 };
}

''', '')
    text = text.replace('  const pinchRef = useRef<{ distance: number; center: Point } | null>(null);\n', '')
    text = text.replace('  const viewport = board.viewport;\n', '')
    text = text.replace('  const setViewport = useBoardStore((s) => s.setViewport);\n', '')
    text = text.replace('  const groupScale = fitScale * viewport.scale;', '  const groupScale = fitScale;')
    start = text.find('  const updateViewportAtPoint = (point: Point, nextScale: number) => {')
    end = text.find('  const stageToNormalized = (point: Point): NormalizedPoint | null => {')
    if start < 0 or end < 0:
        raise SystemExit("RPD patch could not remove viewport zoom logic")
    text = text[:start] + text[end:]
    text = text.replace(
        '    const logicalX = (point.x - baseX - viewport.x) / groupScale;\n    const logicalY = (point.y - baseY - viewport.y) / groupScale;',
        '    const logicalX = (point.x - baseX) / groupScale;\n    const logicalY = (point.y - baseY) / groupScale;'
    )
    start = text.find('  const onWheel = (event: Konva.KonvaEventObject<WheelEvent>) => {')
    end = text.find('  const setDraft = (draft: BoardDrawing | null) => {')
    if start < 0 or end < 0:
        raise SystemExit("RPD patch could not remove pinch/wheel handlers")
    text = text[:start] + text[end:]
    text = text.replace('    if (!activeDrawingTool || interactionDisabled || pinchRef.current) return false;', '    if (!activeDrawingTool || interactionDisabled) return false;')
    text = text.replace('    if (!draft || pinchRef.current) return;', '    if (!draft) return;')
    for line in [
        '        onWheel={onWheel}\n',
        '        onTouchStart={onTouchStart}\n',
        '        onTouchMove={onTouchMove}\n',
        '        onTouchEnd={endTouch}\n',
        '        onTouchCancel={endTouch}\n',
    ]:
        text = text.replace(line, '')
    text = text.replace('            x={baseX + viewport.x}\n            y={baseY + viewport.y}', '            x={baseX}\n            y={baseY}')
    text = text.replace(
        '<><span>Drag to move</span><span>Pinch to zoom</span><span>2 fingers to pan</span><span>Drop equipment here</span></>',
        '<><span>Drag to move</span><span>Drop equipment here</span></>'
    )
    pitch.write_text(text)

# Player: produce a playback scene immediately when Play is pressed.
player = ROOT / "src/hooks/useAnimationPlayer.ts"
text = player.read_text()
if "renderElapsed(baseElapsedRef.current);" not in text:
    text = text.replace(
        '''    startRef.current = performance.now();
    playingRef.current = true;
    setIsPlaying(true);''',
        '''    renderElapsed(baseElapsedRef.current);
    startRef.current = performance.now();
    playingRef.current = true;
    setIsPlaying(true);''',
        1
    )
    text = text.replace('  }, [cancel, tick]);', '  }, [cancel, tick, renderElapsed]);', 1)
    player.write_text(text)

# Add focused styling without touching the large existing stylesheet.
css = ROOT / "src/app/globals.css"
text = css.read_text()
marker = "/* RPD frame workflow — direct next-frame + clean playback */"
if marker not in text:
    text += '''
/* RPD frame workflow — direct next-frame + clean playback */
.animation-quick-next { max-width:1080px; margin:10px auto 0; display:flex; align-items:center; justify-content:space-between; gap:14px; padding:11px 12px; border:1px solid rgba(226,27,45,.48); border-radius:13px; background:linear-gradient(135deg,rgba(226,27,45,.12),rgba(25,27,31,.92)); }
.animation-quick-next > div { min-width:0; display:grid; gap:2px; }
.animation-quick-next span { color:#ff6977; font-size:9px; font-weight:950; letter-spacing:.11em; }
.animation-quick-next strong { font-size:13px; line-height:1.25; }
.animation-quick-next small { color:var(--muted); font-size:10px; line-height:1.3; }
.animation-quick-next button { min-height:48px; flex:0 0 auto; border:0; border-radius:11px; background:var(--red); color:#fff; padding:0 18px; font-weight:950; letter-spacing:.04em; }
.animation-quick-next button:disabled { opacity:.4; }

.animation-playback-overlay { position:fixed; inset:0; z-index:1400; display:grid; place-items:center; padding:12px; background:rgba(5,6,7,.94); backdrop-filter:blur(14px); }
.animation-playback-shell { width:min(1200px,100%); height:min(96dvh,980px); display:grid; grid-template-rows:auto minmax(0,1fr) auto; overflow:hidden; border:1px solid #343941; border-radius:20px; background:#0f1113; box-shadow:0 30px 100px rgba(0,0,0,.72); }
.animation-playback-head { display:flex; align-items:center; justify-content:space-between; gap:16px; padding:14px 16px; border-bottom:1px solid var(--line); background:#16191d; }
.animation-playback-head > div { min-width:0; display:grid; gap:2px; }
.animation-playback-head span { color:#ff6574; font-size:9px; font-weight:950; letter-spacing:.12em; }
.animation-playback-head strong { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:17px; }
.animation-playback-head small { color:var(--muted); font-size:10px; }
.animation-playback-head button { min-height:42px; flex:0 0 auto; border:1px solid #3a3f46; border-radius:10px; background:#24282d; color:#fff; padding:0 13px; font-weight:850; }
.animation-playback-pitch { min-height:0; padding:12px; display:grid; }
.animation-playback-pitch .pitch-stage-shell { width:100%; max-width:none; height:100%; min-height:0; border-radius:13px; }
.animation-playback-pitch .pitch-gesture-hint { display:none; }
.animation-playback-controls { display:grid; grid-template-columns:auto auto minmax(120px,1fr) 46px; align-items:center; gap:8px; padding:12px 14px; border-top:1px solid var(--line); background:#15181b; }
.animation-playback-controls button { min-height:44px; border:1px solid #383d44; border-radius:10px; background:#24282d; color:#fff; padding:0 15px; font-weight:900; }
.animation-playback-controls button.primary { background:var(--red); border-color:var(--red); }
.animation-playback-controls input[type="range"] { width:100%; accent-color:var(--red); }
.animation-playback-controls > span { color:var(--muted); text-align:right; font-size:10px; font-weight:900; }

@media (max-width:620px) {
  .animation-quick-next { align-items:stretch; flex-direction:column; }
  .animation-quick-next button { width:100%; min-height:52px; }
  .animation-playback-overlay { padding:0; }
  .animation-playback-shell { height:100dvh; border:0; border-radius:0; }
  .animation-playback-head { padding:10px 11px; }
  .animation-playback-head small { display:none; }
  .animation-playback-pitch { padding:8px; }
  .animation-playback-controls { grid-template-columns:1fr 1fr; }
  .animation-playback-controls input[type="range"] { grid-column:1 / -1; grid-row:2; }
  .animation-playback-controls > span { display:none; }
}
'''
    css.write_text(text)

print("RPD frame workflow patch applied")
