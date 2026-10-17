import { WebGLRenderer, Scene, PerspectiveCamera, Group, Mesh, MeshBasicMaterial, ExtrudeGeometry, Shape, TorusGeometry, CanvasTexture, PlaneGeometry } from 'three';
export function start(host) {
  const renderer = new WebGLRenderer({alpha:true,antialias:false,powerPreference:'low-power'});
  renderer.setPixelRatio(1);
  renderer.setSize(240,180);
  renderer.domElement.setAttribute('aria-hidden','true');
  renderer.domElement.style.cssText='position:absolute;inset:0;width:100%;height:100%;pointer-events:none';
  const scene = new Scene(), camera = new PerspectiveCamera(38,240/180,.1,20), group = new Group();
  camera.position.z=5;scene.add(group);
  const orange=new MeshBasicMaterial({color:0xff7427});
  const shape=new Shape();shape.moveTo(0,.65);shape.lineTo(.17,.17);shape.lineTo(.65,0);shape.lineTo(.17,-.17);shape.lineTo(0,-.65);shape.lineTo(-.17,-.17);shape.lineTo(-.65,0);shape.lineTo(-.17,.17);shape.closePath();
  const star=new Mesh(new ExtrudeGeometry(shape,{depth:.12,bevelEnabled:false}),orange);star.position.set(.68,.4,0);star.scale.setScalar(.5);group.add(star);
  const ring=new Mesh(new TorusGeometry(.78,.028,6,48),orange);ring.rotation.x=.35;group.add(ring);
  const surface=document.createElement('canvas');surface.width=128;surface.height=128;const ctx=surface.getContext('2d');ctx.fillStyle='#ff7427';ctx.font='bold 116px Arial';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText('a',64,61);
  const texture=new CanvasTexture(surface), material=new MeshBasicMaterial({map:texture,transparent:true});
  group.add(new Mesh(new PlaneGeometry(1.35,1.35),material));
  const fallback=host.querySelector('img');host.append(renderer.domElement);fallback.style.visibility='hidden';
  const motion=matchMedia('(prefers-reduced-motion: reduce)');let visible=true,closed=false,timer,last=0;
  const draw=(time)=>{if(time-last<50)return;last=time;group.rotation.y=Math.sin(time*.0005)*.3;group.rotation.z=Math.sin(time*.0003)*.06;renderer.render(scene,camera)};
  const sync=()=>{renderer.setAnimationLoop(null);if(!closed&&visible&&!document.hidden){renderer.render(scene,camera);if(!motion.matches)renderer.setAnimationLoop(draw)}};
  const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync()});observer.observe(host);
  document.addEventListener('visibilitychange',sync);motion.addEventListener('change',sync);
  const cleanup=()=>{if(closed)return;closed=true;clearTimeout(timer);observer.disconnect();document.removeEventListener('visibilitychange',sync);motion.removeEventListener('change',sync);window.removeEventListener('pagehide',cleanup);renderer.setAnimationLoop(null);group.traverse(o=>{if(o.isMesh)o.geometry.dispose()});orange.dispose();material.dispose();texture.dispose();renderer.dispose();renderer.forceContextLoss();renderer.domElement.remove();fallback.style.visibility='';};
  window.addEventListener('pagehide',cleanup,{once:true});sync();
  // Stop continuous motion after eight seconds; retain a static 3D logo until closed.
  timer=setTimeout(()=>{motion.removeEventListener('change',sync);document.removeEventListener('visibilitychange',sync);observer.disconnect();renderer.setAnimationLoop(null)},8000);
  return cleanup;
}
