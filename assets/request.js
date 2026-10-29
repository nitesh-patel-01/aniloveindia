export function whatsappRequestUrl(subject,message,page){
  const text='[AniLove India] '+String(subject).trim()+'\n\n'+String(message).trim()+'\n\nPage: '+page;
  return 'https://wa.me/917974823298?text='+encodeURIComponent(text);
}

export function whatsappWebsiteUrl(name,business,need,message,page){
  const lines=['Hi Nitesh, I want a website built.','','Name: '+String(name).trim()];
  if(String(business).trim()) lines.push('Business / project: '+String(business).trim());
  lines.push('What I need: '+String(need).trim(),'','Project details: '+String(message).trim(),'','Page: '+page);
  return 'https://wa.me/917974823298?text='+encodeURIComponent(lines.join('\n'));
}
