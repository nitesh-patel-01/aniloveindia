const CACHE='anilove-static-v2';
self.addEventListener('install',e=>{e.waitUntil(self.skipWaiting())});
self.addEventListener('activate',e=>e.waitUntil(Promise.all([self.clients.claim(),caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('anilove-')&&k!==CACHE).map(k=>caches.delete(k))))])));
self.addEventListener('fetch',e=>{
 const u=new URL(e.request.url);
 if(e.request.method!=='GET'||u.origin!==self.location.origin||!u.pathname.startsWith('/assets/'))return;
 e.respondWith(fetch(e.request).then(r=>{
  if(r.ok)caches.open(CACHE).then(cache=>cache.put(e.request,r.clone())).catch(()=>{});
  return r;
 }).catch(()=>caches.match(e.request).then(r=>r||Response.error())));
});
