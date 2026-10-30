// Search metadata once per catalogue; no dependencies or network calls per keystroke.
const indexes = new WeakMap();
export function normalizeSearch(value) {
  return String(value ?? '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
    .replace(/[’']/g, '').replace(/×/g, ' x ').replace(/[^\p{L}\p{N}\p{M}]+/gu, ' ').trim().replace(/\s+/g, ' ');
}
const compact = value => value.replace(/\s/g, '');
const noise = new Set(['watch','online','dub','dubbed','full','episode','episodes','in','with','subtitles','subbed']);
function fields(title) {
  const names = [title.title, title.original_title, ...(title.alternate_titles || [])].filter(Boolean).map(normalizeSearch);
  const editions = (title.seasons || []).map(s => [s.label, s.audio_language, ...(s.subtitle_languages || [])].join(' '));
  const meta = normalizeSearch([title.provider,title.audio_label,title.category,...(title.genre || []),...editions].join(' '));
  return {title,names,meta,words:new Set((names.join(' ')+' '+meta).split(' '))};
}
function near(a,b) {
  if (a.length < 5 || Math.abs(a.length-b.length)>1) return false;
  let i=0,j=0,errors=0;
  while(i<a.length && j<b.length) {
    if(a[i]===b[j]) {i++;j++;continue;}
    if(++errors>1)return false;
    if(a.length>=b.length)i++;
    if(b.length>=a.length)j++;
  }
  return errors+(a.length-i)+(b.length-j)<=1;
}
export function searchCatalogue(catalogue, query='', category='') {
  if(!indexes.has(catalogue))indexes.set(catalogue,catalogue.map(fields));
  const text=normalizeSearch(query), tokens=[...new Set(text.split(' ').filter(w=>w&&!noise.has(w)))];
  const meaningful=tokens.join(' '), joined=compact(meaningful);
  const ranked=[];
  for(const item of indexes.get(catalogue)) {
    const {title,names,meta,words}=item;
    if(category && title.category!==category)continue;
    let score=0;
    if(!text)score=1;
    else if(names.some(n=>n===text))score=1000;
    else if(joined && names.some(n=>compact(n)===joined))score=950;
    else if(joined && names.some(n=>compact(n).includes(joined)))score=850;
    else if(tokens.length && tokens.every(w=>names.some(n=>n.includes(w))||meta.includes(w))) {
      score=500+tokens.filter(w=>names.some(n=>n.includes(w))).length*20;
    } else if(tokens.length && tokens.every(w=>names.some(n=>n.includes(w))||meta.includes(w)||[...words].some(n=>near(w,n))))score=100;
    if(score)ranked.push({title,score});
  }
  return ranked.sort((a,b)=>b.score-a.score || ((a.title.category===b.title.category) ? (a.title.browse_priority??100)-(b.title.browse_priority??100) : 0)).map(r=>r.title);
}
