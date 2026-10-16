import {whatsappRequestUrl} from './request.js';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
let catalogue=[],user=null,auth=null,installPrompt;
const read=(k,def=[])=>{try{return JSON.parse(localStorage.getItem(k))??def}catch{return def}};
const save=(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v));return true}catch{toast('Storage is unavailable in this browser.');return false}};
function toast(t){const el=$('#toast');el.textContent=t;el.style.display='block';clearTimeout(window.toastTimer);window.toastTimer=setTimeout(()=>el.style.display='none',4500)}
const safe=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function localCard(t){const count=t.seasons.reduce((n,s)=>n+s.episodes.length,0);const info=t.format==='Movie'?'Full movie':t.seasons.length>1?t.seasons.length+' seasons / editions':t.seasons[0].label;return `<article class="title-card"><a href="/title/${safe(t.id)}/" class="poster"><img class="youtube-cover" src="${safe(t.thumbnail)}" alt="${safe(t.title)} official YouTube thumbnail" loading="lazy" width="480" height="360"><span class="poster-type">${safe(t.audio_label||t.original_language)}</span><span class="poster-arrow">▶</span></a><div class="card-info"><h3><a href="/title/${safe(t.id)}/">${safe(t.title)}</a></h3><p>${safe(info)} <span>· ${count} uploads</span></p><small>${safe(t.provider)}</small></div></article>`}
function renderList(){if($('#watchlist-results')){const ep=read('anilove:episode',null);if(ep&&/^\/watch\/[a-z0-9-]+\/[a-z0-9-]+\/$/.test(ep)){const a=document.createElement('a');a.href=ep;a.className='btn primary';a.textContent='▶ Continue last episode';$('#recent-results').before(a)}const ids=read('anilove:watchlist');const ts=ids.map(id=>catalogue.find(t=>t.id===id)).filter(Boolean);$('#watchlist-results').innerHTML=ts.length?'<div class="cards">'+ts.map(t=>localCard(t)+`<button class="subtle remove-title" data-id="${safe(t.id)}">Remove ${safe(t.title)}</button>`).join('')+'</div>':'<p>No saved titles yet. Explore the catalogue and save a story.</p>';const recent=read('anilove:recent').map(id=>catalogue.find(t=>t.id===id)).filter(Boolean);$('#recent-results').innerHTML='<div class="cards">'+recent.map(localCard).join('')+'</div>'}}
function filter(){if(!$('#query'))return;const needle=$('#query').value.trim().toLowerCase();const category=$('.catalogue')?.dataset.category;const ts=catalogue.filter(t=>(!category||t.category===category)&&(!needle||[t.title,t.original_title,...t.alternate_titles].some(v=>v.toLowerCase().includes(needle))));if(category)ts.sort((a,b)=>Number(b.added_on==='2026-10-16')-Number(a.added_on==='2026-10-16'));$('#results').innerHTML='<div class="cards">'+ts.map(localCard).join('')+'</div>';$('#result-count').textContent=ts.length+' '+(ts.length===1?'title':'titles')+(needle?' found':' available');$('#empty').hidden=ts.length>0;const subject=$('#empty input[name="subject"]');if(subject)subject.value=$('#query').value.trim();const params=new URLSearchParams();if(needle)params.set('q',$('#query').value.trim());history.replaceState(null,'',location.pathname+(params.size?'?'+params:''));if(params.size)document.querySelector('meta[name="robots"]').content='noindex,follow'}
document.addEventListener('click',e=>{const add=e.target.closest('.save-title');if(add){const ids=read('anilove:watchlist');if(!ids.includes(add.dataset.id))ids.push(add.dataset.id);if(save('anilove:watchlist',ids))toast('Saved on this device.');add.textContent='✓ Saved to watchlist'}const remove=e.target.closest('.remove-title');if(remove){save('anilove:watchlist',read('anilove:watchlist').filter(id=>id!==remove.dataset.id));renderList()}const link=e.target.closest('.official-link');if(link){save('anilove:recent',[link.dataset.id,...read('anilove:recent').filter(id=>id!==link.dataset.id)].slice(0,10))}});
$$('.request-form').forEach(form=>form.addEventListener('submit',e=>{e.preventDefault();const d=new FormData(form);location.href=whatsappRequestUrl(d.get('subject'),d.get('message'),location.origin+location.pathname)}));
const report=new URLSearchParams(location.search).get('report');if(report&&$('.request-form [name="subject"]'))$('.request-form [name="subject"]').value='Source report: '+report;
$('#clear-data')?.addEventListener('click',()=>{for(const k of Object.keys(localStorage))if(k.startsWith('anilove:'))localStorage.removeItem(k);toast('Local lists and history cleared.');renderList()});
window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();installPrompt=e});$('#install')?.addEventListener('click',async()=>{if(installPrompt){await installPrompt.prompt();installPrompt=null}else toast('Use your browser menu: Install app / Add to Home Screen.')});
if('serviceWorker'in navigator)navigator.serviceWorker.register('/sw.js').catch(()=>{});
async function start(){try{const r=await fetch('/data/catalogue.json');if(!r.ok)throw Error();catalogue=await r.json();if($('#query')){const params=new URLSearchParams(location.search);$('#query').value=params.get('q')||'';$('#query').addEventListener('input',filter);$('.simple-search').addEventListener('submit',e=>{e.preventDefault();filter()});filter()}renderList()}catch{if($('#result-count'))$('#result-count').textContent='Interactive search could not load. The links below still work.';toast('Search could not load. Please refresh, or open a title below.')}if($('#job-status'))try{const r=await fetch('/data/status.json');const s=await r.json();$('#job-status').innerHTML=`<div class="status-grid"><div><strong>Schedule</strong><p>${safe(s.schedule)}</p></div><div><strong>State</strong><p>${safe(s.state)}</p></div><div><strong>Last run</strong><p>${safe(s.last_run||'Not run on a scheduler')}</p></div><div><strong>Next scheduled run</strong><p>${safe(s.next_scheduled_run||'Not active')}</p></div></div><h2>Latest check</h2><p>${safe(s.blog?.skipped||'No blog changes')}</p><ul>${(s.errors||[]).map(x=>'<li>'+safe(x)+'</li>').join('')}</ul>`}catch{$('#job-status').textContent='Status unavailable.'}}
start();

$$('.load-video').forEach(button=>button.addEventListener('click',()=>{if(!/^[A-Za-z0-9_-]{11}$/.test(button.dataset.video))return;const frame=document.createElement('iframe');frame.src='https://www.youtube-nocookie.com/embed/'+button.dataset.video+(button.dataset.playlist?'?list='+encodeURIComponent(button.dataset.playlist):'');frame.title=button.dataset.title+' official YouTube episode';save('anilove:episode',location.pathname);const titleId=catalogue.find(t=>t.seasons.some(s=>s.episodes.some(ep=>ep.video_id===button.dataset.video)))?.id;if(titleId)save('anilove:recent',[titleId,...read('anilove:recent').filter(id=>id!==titleId)].slice(0,10));frame.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';button.parentElement.replaceChildren(frame)}));

$$('.load-playlist').forEach(button=>button.addEventListener('click',()=>{if(!/^PL[A-Za-z0-9_-]{10,}$/.test(button.dataset.playlist))return;const frame=document.createElement('iframe');frame.src='https://www.youtube-nocookie.com/embed/videoseries?list='+encodeURIComponent(button.dataset.playlist);frame.title=button.dataset.title+' official playlist';frame.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';frame.allowFullscreen=true;frame.referrerPolicy='strict-origin-when-cross-origin';button.parentElement.replaceChildren(frame)}));

// Featured artwork rotates; embedded videos never autoplay.
const hero=$('.stream-hero');
if(hero){
 const slides=$$('[data-slide]'), controls=$$('[data-feature]');
 const motion=matchMedia('(prefers-reduced-motion: reduce)');
 let index=0,paused=motion.matches,hovered=false,timer,touchStart=null;
 const pause=$('[data-hero-pause]');
 function schedule(){clearTimeout(timer);if(!paused&&!hovered&&!document.hidden&&!hero.contains(document.activeElement))timer=setTimeout(()=>choose(index+1),6500)}
 function choose(next){index=(next+slides.length)%slides.length;slides.forEach((slide,i)=>slide.hidden=i!==index);controls.forEach((control,i)=>control.setAttribute('aria-pressed',String(i===index)));const count=$('[data-hero-count]');if(count)count.textContent=String(index+1).padStart(2,'0')+' / '+String(slides.length).padStart(2,'0');schedule()}
 function setPause(value){paused=value;pause.setAttribute('aria-pressed',String(paused));pause.setAttribute('aria-label',paused?'Start automatic slides':'Pause automatic slides');pause.textContent=paused?'▶':'Ⅱ';schedule()}
 controls.forEach((button,i)=>button.addEventListener('click',()=>choose(i)));
 $$('[data-hero-step]').forEach(button=>button.addEventListener('click',()=>choose(index+Number(button.dataset.heroStep))));
 pause.addEventListener('click',()=>setPause(!paused));
 hero.addEventListener('mouseenter',()=>{hovered=true;schedule()});hero.addEventListener('mouseleave',()=>{hovered=false;schedule()});
 hero.addEventListener('focusin',schedule);hero.addEventListener('focusout',()=>setTimeout(schedule,0));
 document.addEventListener('visibilitychange',schedule);
 motion.addEventListener('change',()=>setPause(motion.matches));
 hero.addEventListener('keydown',event=>{if(event.target.matches('input,textarea'))return;if(event.key==='ArrowLeft'||event.key==='ArrowRight'){event.preventDefault();choose(index+(event.key==='ArrowRight'?1:-1))}});
 hero.addEventListener('touchstart',event=>{if(event.touches.length===1)touchStart={x:event.touches[0].clientX,y:event.touches[0].clientY};else touchStart=null},{passive:true});
 hero.addEventListener('touchend',event=>{if(!touchStart)return;const touch=event.changedTouches[0],dx=touch.clientX-touchStart.x,dy=touch.clientY-touchStart.y;touchStart=null;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)*1.4)choose(index+(dx<0?1:-1))},{passive:true});
 hero.addEventListener('touchcancel',()=>touchStart=null,{passive:true});
 setPause(paused);
}
$$('[data-scroll]').forEach(button=>button.addEventListener('click',()=>{
  const row=button.closest('.rail-wrap')?.querySelector('.rail');
  if(row)row.scrollBy({left:row.clientWidth*.85*Number(button.dataset.scroll),behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
}));
const seasonNav=$('[data-season-tabs]');
if(seasonNav){
  const tabs=[...seasonNav.querySelectorAll('[data-season-target]')];
  const panels=$$('[data-season-panel]');
  if(tabs.length&&panels.length){
    seasonNav.setAttribute('role','tablist');
    tabs.forEach(tab=>{tab.setAttribute('role','tab');tab.id='tab-'+tab.dataset.seasonTarget;tab.setAttribute('aria-controls',tab.dataset.seasonTarget)});
    panels.forEach(panel=>{panel.setAttribute('role','tabpanel');panel.setAttribute('aria-labelledby','tab-'+panel.id)});
    function chooseSeason(id,update=false,focus=false){
      const chosen=tabs.find(tab=>tab.dataset.seasonTarget===id)||tabs[0];
      tabs.forEach(tab=>{const selected=tab===chosen;tab.setAttribute('aria-selected',String(selected));tab.tabIndex=selected?0:-1});
      panels.forEach(panel=>panel.hidden=panel.id!==chosen.dataset.seasonTarget);
      if(update)history.replaceState(null,'','#'+chosen.dataset.seasonTarget);
      if(focus)chosen.focus();
    }
    chooseSeason(location.hash.slice(1));
    window.addEventListener('hashchange',()=>chooseSeason(location.hash.slice(1)));
    tabs.forEach((tab,i)=>{
      tab.addEventListener('click',event=>{event.preventDefault();chooseSeason(tab.dataset.seasonTarget,true)});
      tab.addEventListener('keydown',event=>{
        let next;
        if(event.key==='ArrowRight')next=(i+1)%tabs.length;
        if(event.key==='ArrowLeft')next=(i-1+tabs.length)%tabs.length;
        if(event.key==='Home')next=0;
        if(event.key==='End')next=tabs.length-1;
        if(next!==undefined){event.preventDefault();chooseSeason(tabs[next].dataset.seasonTarget,true,true)}
      });
    });
  }
}
const requested=new URLSearchParams(location.search).get('request');
if(requested&&$('.request-form [name="subject"]')){
  $('.request-form [name="subject"]').value='Title request: '+requested.slice(0,130);
  $('.request-form [name="message"]').value='Please check the official full YouTube upload for '+requested.slice(0,180)+'.\nPreferred language: Hindi / English subtitles\nCountry: India';
}
$$('header nav a').forEach(link=>{if(link.pathname===location.pathname)link.setAttribute('aria-current','page')});
$$('[data-image-fallback]').forEach(img=>{const fallback=()=>{if(img.dataset.imageFallback){const path=img.dataset.imageFallback;delete img.dataset.imageFallback;img.src=path;img.alt='Original AniLove illustration of an anime-inspired world'}};img.addEventListener('error',fallback,{once:true});if(img.complete&&!img.naturalWidth)fallback()});
