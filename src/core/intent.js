const allowed=new Set(['observe','rest','approach','micro']);
export function validateIntent(proposal,{epoch,now=Date.now(),budget=1}){
 if(budget<=0)return {accepted:false,reason:'BUDGET'};
 if(!proposal||typeof proposal!=='object'||Object.keys(proposal).some(k=>!['intent','memoryEpoch','expiresAt'].includes(k))||!allowed.has(proposal.intent))return {accepted:false,reason:'FORBIDDEN'};
 if(proposal.memoryEpoch!==epoch)return {accepted:false,reason:'STALE_EPOCH'};
 const expiry=Date.parse(proposal.expiresAt);if(!Number.isFinite(expiry)||expiry<=now||expiry>now+60000)return {accepted:false,reason:'EXPIRED'};
 return {accepted:true,intent:proposal.intent};
}
export async function proposeWithTimeout(adapter,context,timeout=2000){let timer;try{return await Promise.race([Promise.resolve().then(()=>adapter(context)).then(p=>validateIntent(p,context)),new Promise(resolve=>{timer=setTimeout(()=>resolve({accepted:false,reason:'TIMEOUT'}),timeout);})]);}catch{return {accepted:false,reason:'UNAVAILABLE'};}finally{clearTimeout(timer);}}
