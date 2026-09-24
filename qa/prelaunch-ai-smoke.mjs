import { createClient } from "@supabase/supabase-js";

const url=process.env.NEXT_PUBLIC_SUPABASE_URL||process.env.SUPABASE_URL;
const key=process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY||process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY||process.env.SUPABASE_ANON_KEY;
if(!url||!key){console.error("AI_QA_CONFIG_MISSING: Supabase public URL/key missing");process.exit(2);}

const email="rpd.qa.launch@example.com";
const password="RPD-QA-Launch-2026!";
const client=createClient(url,key,{auth:{persistSession:false,autoRefreshToken:false}});

let auth=await client.auth.signInWithPassword({email,password});
if(auth.error){
  const signup=await client.auth.signUp({email,password});
  if(signup.error){console.error("AI_QA_SIGNUP_FAILED",signup.error.message);process.exit(3);}
  auth={data:signup.data,error:null};
}
if(!auth.data?.session){
  console.error("AI_QA_NEEDS_CONFIRMATION: QA account exists but has no session. Confirm rpd.qa.launch@example.com then rerun.");
  process.exit(4);
}
const user=auth.data.user;
console.log("AI_QA_AUTH_OK",user.id);

const {data:ents,error:entErr}=await client.from("entitlements").select("id,entitlement,revoked_at").eq("owner_id",user.id).eq("entitlement","premium").is("revoked_at",null);
if(entErr){console.error("AI_QA_ENTITLEMENT_READ_FAILED",entErr.message);process.exit(5);}
const premium=Boolean(ents?.length);
console.log("AI_QA_PREMIUM",premium);

const drillBody={action:"generate",request:{focus:"Passing",subFocus:"Breaking lines",ageGroup:"U12-U14",playerCount:8,duration:10,space:"small-area",difficulty:"simple",realism:"technical",goalkeepers:0,equipment:["Balls","Cones"],outcome:"Simple scan, receive and play forward practice.",constraints:"Keep it simple and practical."}};
const drill=await client.functions.invoke("ai-drill-builder",{body:drillBody});

if(!premium){
  const msg=String(drill.error?.message||drill.data?.error||"");
  if(!drill.error && drill.data?.ok===true){
    console.error("AI_QA_SECURITY_FAIL: free signed-in user generated an AI drill");
    process.exit(6);
  }
  if(!/premium|pro|upgrade|entitlement/i.test(msg)){
    console.error("AI_QA_FREE_GATE_WRONG_RESPONSE",msg);
    process.exit(7);
  }
  console.log("AI_QA_FREE_GATE_PASS",msg);
  process.exit(0);
}

if(drill.error||drill.data?.ok!==true||!drill.data?.drill){
  console.error("AI_QA_DRILL_FAILED",drill.error?.message||drill.data?.error||JSON.stringify(drill.data));
  process.exit(8);
}
const d=drill.data.drill;
if(d.playerCount!==8||!Array.isArray(d.layout?.players)||d.layout.players.length!==8||!Array.isArray(d.coachingPoints)||d.coachingPoints.length<3){
  console.error("AI_QA_DRILL_VALIDATION_FAIL",JSON.stringify({playerCount:d.playerCount,boardPlayers:d.layout?.players?.length,points:d.coachingPoints?.length}));
  process.exit(9);
}
console.log("AI_QA_DRILL_PASS",d.title);

const sessionReq={ageGroup:"U12-U14",playerCount:8,goalkeepers:0,duration:35,primaryFocus:"Passing",secondaryFocus:["Scanning","Movement off ball"],teamLevel:"developing",intensity:"moderate",context:"development",space:"half-pitch",equipment:["Footballs","Cones","Bibs","Mini goals"],teamNeed:"Connect simple passes through the thirds.",playingIdentity:["Connect the thirds"],developmentPriorities:["Confidence","Communication","Decision making"],constraints:"Keep explanations simple."};
const session=await client.functions.invoke("ai-session-builder",{body:{request:sessionReq}});
if(session.error||session.data?.ok!==true||!session.data?.session){
  console.error("AI_QA_SESSION_FAILED",session.error?.message||session.data?.error||JSON.stringify(session.data));
  process.exit(10);
}
const s=session.data.session;
const total=(s.blocks||[]).reduce((n,b)=>n+Number(b.duration||0),0);
if(s.totalDuration!==35||total!==35||(s.blocks||[]).length<6){
  console.error("AI_QA_SESSION_VALIDATION_FAIL",JSON.stringify({totalDuration:s.totalDuration,blockTotal:total,blocks:s.blocks?.length}));
  process.exit(11);
}
for(const [i,b] of (s.blocks||[]).entries()){
  if(!Array.isArray(b.layout?.players)||b.layout.players.length!==8){
    console.error("AI_QA_SESSION_BOARD_FAIL",i+1,b.layout?.players?.length);
    process.exit(12);
  }
}
console.log("AI_QA_SESSION_PASS",s.title,"blocks",s.blocks.length,"minutes",total);
