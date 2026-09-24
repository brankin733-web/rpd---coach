import { chromium } from "playwright";

const base = process.env.QA_BASE_URL || "http://127.0.0.1:3100";
const failures = [];
const consoleErrors = [];

function fail(message){ failures.push(message); console.error("FAIL:", message); }
function pass(message){ console.log("PASS:", message); }

const browser = await chromium.launch({headless:true});
const context = await browser.newContext({viewport:{width:1365,height:768}});
const page = await context.newPage();
page.on("pageerror", err => consoleErrors.push("pageerror: "+err.message));
page.on("console", msg => { if(msg.type()==="error") consoleErrors.push("console: "+msg.text()); });

const routes = [
  "/","/board/","/library/","/sessions/","/planner/","/ai-drill/","/ai-session/",
  "/membership/","/settings/","/profile/","/help/","/privacy/","/terms/",
  "/delete-account/","/auth/sign-in/","/auth/sign-up/","/auth/forgot/"
];

for(const route of routes){
  try{
    const response = await page.goto(base+route,{waitUntil:"domcontentloaded",timeout:30000});
    await page.waitForTimeout(350);
    const status = response?.status() ?? 0;
    const body = await page.locator("body").innerText();
    if(status >= 400) fail(route+" returned HTTP "+status);
    else if(/Application error|Internal Server Error/i.test(body)) fail(route+" rendered a fatal error");
    else pass(route+" loaded");
  }catch(err){ fail(route+" navigation failed: "+err.message); }
}

try{
  await page.goto(base+"/onboarding/",{waitUntil:"domcontentloaded"});
  await page.evaluate(()=>localStorage.setItem("rpd-coach.v2.onboarding",JSON.stringify(true)));
  await page.goto(base+"/board/",{waitUntil:"domcontentloaded"});
  await page.waitForSelector(".board-canvas",{timeout:15000});
  pass("Board canvas renders");

  const dock = page.locator(".bottom-dock");
  const dockDisplay = await dock.evaluate(el => {
    const s=getComputedStyle(el);
    return {display:s.display,columns:s.gridTemplateColumns,position:s.position};
  });
  if(dockDisplay.position!=="fixed") fail("Landscape tool rails are not fixed");
  else pass("Landscape tool rail layout active");

  const addBtn = dock.locator("button").filter({hasText:"ADD"});
  await addBtn.click();
  await page.getByText("Build the picture faster.").waitFor({timeout:10000});
  await page.locator(".quick-row button").filter({hasText:"4v2"}).click();
  const players = page.locator(".player-object");
  if(await players.count() < 6) fail("Quick 4v2 did not add expected players");
  else pass("Equipment/player add workflow works");

  const drawBtn = dock.locator("button").filter({hasText:"DRAW"});
  await drawBtn.click();
  const passTool = page.locator(".draw-tool-grid button").filter({hasText:"Pass"}).first();
  await passTool.click();
  const canvas = page.locator(".board-canvas");
  const box = await canvas.boundingBox();
  if(!box) fail("Board canvas has no drawable area");
  else{
    await page.mouse.move(box.x+box.width*.3, box.y+box.height*.35);
    await page.mouse.down();
    await page.mouse.move(box.x+box.width*.65, box.y+box.height*.55,{steps:8});
    await page.mouse.up();
    if(await page.locator(".path-object").count() < 1) fail("Pass drawing did not create a path");
    else pass("Line/drawing workflow works");
  }

  const undo = dock.locator("button").filter({hasText:"UNDO"});
  const redo = dock.locator("button").filter({hasText:"REDO"});
  await undo.click(); await page.waitForTimeout(100);
  await redo.click(); await page.waitForTimeout(100);
  pass("Undo/redo controls respond");

  const animate = dock.locator("button").filter({hasText:"ANIMATE"});
  await animate.click();
  await page.getByRole("button",{name:/CAPTURE FRAME 1/i}).click();
  const firstPlayer = page.locator(".player-object").first();
  const pb = await firstPlayer.boundingBox();
  if(pb){
    await page.mouse.move(pb.x+pb.width/2,pb.y+pb.height/2);
    await page.mouse.down();
    await page.mouse.move(pb.x+pb.width/2+70,pb.y+pb.height/2+20,{steps:6});
    await page.mouse.up();
  }
  await page.getByRole("button",{name:/NEXT FRAME/i}).click();
  const captured = await page.locator(".animation-build-copy").innerText();
  if(!/2 frames captured/i.test(captured)) fail("NEXT FRAME did not capture Frame 2");
  else pass("Direct frame-by-frame capture works");
  await page.locator(".animation-build-actions button").filter({hasText:"Play"}).click();
  await page.getByText("RPD ANIMATION").waitFor({timeout:10000});
  pass("Clean animation playback opens");
  await page.getByRole("button",{name:/Back to edit/i}).click();

  const save = dock.locator("button").filter({hasText:/SAVE/});
  await save.click();
  await page.getByRole("button",{name:"Save as Drill"}).click();
  await page.waitForTimeout(200);
  await page.goto(base+"/library/",{waitUntil:"domcontentloaded"});
  const libraryBody=await page.locator("body").innerText();
  if(!/Untitled drill|My Drills|Drill/i.test(libraryBody)) fail("Saved drill was not visible in library");
  else pass("Save -> Drill Library flow works");

  await page.goto(base+"/board/",{waitUntil:"domcontentloaded"});
  if(await page.locator(".player-object").count() < 6) fail("Board autosave did not survive navigation/reload");
  else pass("Board local persistence works");
}catch(err){ fail("Board interaction suite crashed: "+err.message); }

try{
  await page.goto(base+"/ai-drill/",{waitUntil:"domcontentloaded"});
  const txt=await page.locator("body").innerText();
  if(!/AI DRILL BUILDER|What are we working on/i.test(txt)) fail("AI Drill Builder UI did not render");
  else pass("AI Drill Builder UI renders");
  await page.goto(base+"/ai-session/",{waitUntil:"domcontentloaded"});
  const txt2=await page.locator("body").innerText();
  if(!/AI SESSION BUILDER|Session basics/i.test(txt2)) fail("AI Session Builder UI did not render");
  else pass("AI Session Builder UI renders");
}catch(err){ fail("AI UI smoke failed: "+err.message); }

try{
  const manifest = await page.request.get(base+"/manifest.webmanifest");
  if(!manifest.ok()) fail("PWA manifest unavailable");
  else{
    const json=await manifest.json();
    if(json.orientation!=="landscape") fail("PWA manifest is not landscape");
    else pass("PWA landscape manifest correct");
  }
  const sw=await page.request.get(base+"/sw.js");
  if(!sw.ok()) fail("Service worker unavailable"); else pass("Service worker available");
}catch(err){ fail("PWA checks failed: "+err.message); }

await browser.close();

const relevantConsole = consoleErrors.filter(x => !/favicon|ResizeObserver loop/i.test(x));
if(relevantConsole.length){
  console.error("Browser console errors:");
  for(const e of relevantConsole.slice(0,30)) console.error(e);
  fail(relevantConsole.length+" browser console/page errors detected");
}

if(failures.length){
  console.error("\nPRELAUNCH UI FAILURES:");
  failures.forEach((x,i)=>console.error(`${i+1}. ${x}`));
  process.exit(1);
}
console.log("\nPRELAUNCH UI QA PASSED");
