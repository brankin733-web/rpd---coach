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
print("RPD production access patch applied")
