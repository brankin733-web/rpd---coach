#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
target=ROOT/"components/billing/ProProvider.tsx"
text=target.read_text()

if 'getSupabase' not in text:
    text=text.replace(
        'import { useAuth } from "@/components/auth/AuthProvider";',
        'import { useAuth } from "@/components/auth/AuthProvider";\nimport { getSupabase } from "@/lib/cloud/client";'
    )

old='''    try{await configureBilling(user.id);const state=await getMembership();setPro(state.pro);setBillingAvailable(state.available);}catch{setPro(false);setBillingAvailable(false);}finally{setLoading(false);}'''
new='''    try{
      const cloud=getSupabase();
      let cloudPremium=false;
      if(cloud){
        const {data,error}=await cloud.from("entitlements").select("id").eq("owner_id",user.id).eq("entitlement","premium").is("revoked_at",null).limit(1);
        if(!error)cloudPremium=Boolean(data?.length);
      }
      await configureBilling(user.id);
      const state=await getMembership();
      setPro(cloudPremium||state.pro);
      setBillingAvailable(state.available);
    }catch{setPro(false);setBillingAvailable(false);}finally{setLoading(false);}'''
if new not in text:
    if old not in text: raise SystemExit("Could not patch ProProvider refresh")
    text=text.replace(old,new,1)

target.write_text(text)

ai_client=ROOT/"lib/ai/client.ts"
ai_text=ai_client.read_text()
old_endpoint='client.functions.invoke("ai-session-builder",{body:{request}})'
new_endpoint='client.functions.invoke("ai-complete-session",{body:{request}})'
if new_endpoint not in ai_text:
    if old_endpoint not in ai_text: raise SystemExit("Could not patch complete-session endpoint")
    ai_text=ai_text.replace(old_endpoint,new_endpoint,1)
ai_client.write_text(ai_text)

capacitor=ROOT/"capacitor.config.ts"
cap_text=capacitor.read_text()
cap_text=cap_text.replace('appId: "com.rpdfootball.coach"', 'appId: "com.rpdfootball.coach.v143"')
cap_text=cap_text.replace('appName: "RPD Coach"', 'appName: "RPD Coach NEW"')
capacitor.write_text(cap_text)

package=ROOT/"package.json"
package_text=package.read_text().replace('"version": "1.1.0"', '"version": "1.4.3"')
package.write_text(package_text)

doctor=ROOT/"scripts/release-doctor.mjs"
doctor_text=doctor.read_text().replace('const expectedId="com.rpdfootball.coach";', 'const expectedId="com.rpdfootball.coach.v143";')
doctor.write_text(doctor_text)

print("RPD production access patch applied")
