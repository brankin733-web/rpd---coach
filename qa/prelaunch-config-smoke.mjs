const vars=[
"NEXT_PUBLIC_SUPABASE_URL","NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY","NEXT_PUBLIC_SUPABASE_ANON_KEY",
"NEXT_PUBLIC_AI_ENABLED","NEXT_PUBLIC_BILLING_ENABLED","NEXT_PUBLIC_REVENUECAT_ANDROID_API_KEY",
"NEXT_PUBLIC_REVENUECAT_ENTITLEMENT_ID","NEXT_PUBLIC_INTERNAL_TEST_UNLOCK"
];
for(const k of vars) console.log(k, process.env[k] ? (k.includes("KEY")||k.includes("URL") ? "SET" : process.env[k]) : "MISSING");
const required=["NEXT_PUBLIC_SUPABASE_URL","NEXT_PUBLIC_AI_ENABLED"];
let fail=false;
for(const k of required) if(!process.env[k]){console.error("MISSING_REQUIRED",k);fail=true;}
if(process.env.NEXT_PUBLIC_INTERNAL_TEST_UNLOCK==="true"){console.error("PRODUCTION_BLOCKER: internal test unlock is enabled");fail=true;}
if(fail)process.exit(1);
