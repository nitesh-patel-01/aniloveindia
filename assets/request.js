export function whatsappRequestUrl(subject,message,page){
  const text='[AniLove India] '+String(subject).trim()+'\n\n'+String(message).trim()+'\n\nPage: '+page;
  return 'https://wa.me/917974823298?text='+encodeURIComponent(text);
}
