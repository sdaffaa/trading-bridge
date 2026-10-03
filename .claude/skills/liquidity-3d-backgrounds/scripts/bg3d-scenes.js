'use strict';
/* bg3d-scenes.js — reusable library of 10 WebGL/Three.js 3D backgrounds for
 * Liquidity State designs (carousels, reels, covers, thumbnails). Brand palette
 * baked in (dark-teal #0A171C, teal-green #2ECC9A, mint #7BEBC8, soft-red).
 *
 *   const { SCENES, renderScene } = require('./bg3d-scenes');
 *   await renderScene('gem', { out:'bg.png', width:1080, height:1350, scale:2 });
 *   // CLI:  node bg3d-scenes.js --scene gem --out bg.png [--width 1080 --height 1350 --scale 2]
 *   //       node bg3d-scenes.js --all --outdir assets   (renders all 10)
 *
 * Requires: three.bundle.js (vendored here) + playwright-core + a Chromium with
 * WebGL (software swiftshader is fine). Launch flags are handled below.
 */
const fs = require('fs');
const path = require('path');

const HEAD = (W, H) => `
import * as THREE from 'three';
const W=${W},H=${H}, TEAL=0x2ECC9A, MINT=0x7BEBC8, RED=0xE15A5A, BG=0x0A171C;
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(2); renderer.setSize(W,H);
renderer.domElement.style.width=W+'px';renderer.domElement.style.height=H+'px';
document.body.appendChild(renderer.domElement);
const scene=new THREE.Scene(); scene.background=new THREE.Color(BG);
scene.fog=new THREE.Fog(BG,10,60);
const camera=new THREE.PerspectiveCamera(60,W/H,0.1,300);
camera.position.set(0,1.4,12); camera.lookAt(0,1.6,-20);
let S=99; const rnd=()=>{S=(S*1664525+1013904223)>>>0;return S/4294967296;};
function glow(stops){const c=document.createElement('canvas');c.width=c.height=256;const g=c.getContext('2d');
  const gr=g.createRadialGradient(128,128,0,128,128,128);stops.forEach(s=>gr.addColorStop(s[0],s[1]));
  g.fillStyle=gr;g.fillRect(0,0,256,256);const t=new THREE.CanvasTexture(c);t.needsUpdate=true;return t;}
function sprite(tex,sc,pos){const s=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,blending:THREE.AdditiveBlending,transparent:true,depthWrite:false}));s.scale.set(sc,sc,1);s.position.set(...pos);scene.add(s);return s;}
const TEALG=[[0,'rgba(46,204,154,0.9)'],[0.32,'rgba(46,204,154,0.32)'],[1,'rgba(46,204,154,0)']];
`;
const TAIL = `\nrenderer.render(scene,camera);window.__done=true;`;

const SCENES = {
'sun-grid': `
scene.fog=new THREE.Fog(BG,6,62);camera.position.set(0,0.85,9);camera.lookAt(0,1.7,-34);
const grid=new THREE.GridHelper(240,120,MINT,TEAL);grid.material.transparent=true;grid.material.opacity=0.82;grid.position.z=-30;scene.add(grid);
sprite(glow([[0,'rgba(224,255,246,1)'],[0.3,'rgba(123,235,200,0.9)'],[0.7,'rgba(46,204,154,0.5)'],[1,'rgba(46,204,154,0)']]),24,[0,5.2,-42]);
sprite(glow(TEALG),56,[0,5.2,-43]);`,

'vortex': `
scene.fog=new THREE.Fog(BG,8,70);camera.position.set(0,7,15);camera.lookAt(0,0,-6);
const P=6000,pos=[],col=[];const c1=new THREE.Color(TEAL),c2=new THREE.Color(MINT);
for(let i=0;i<P;i++){const t=i/P;const ang=t*Math.PI*14;const r=1+t*22;const y=-t*4+Math.sin(ang)*0.3;
 pos.push(Math.cos(ang)*r,y,Math.sin(ang)*r - 6);const cc=c1.clone().lerp(c2,1-t);col.push(cc.r,cc.g,cc.b);}
const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
scene.add(new THREE.Points(g,new THREE.PointsMaterial({size:0.12,vertexColors:true,transparent:true,opacity:0.9,blending:THREE.AdditiveBlending,depthWrite:false})));
sprite(glow([[0,'rgba(140,90,220,0.55)'],[0.4,'rgba(46,204,154,0.2)'],[1,'rgba(46,204,154,0)']]),20,[0,-2,-6]);`,

'tunnel': `
scene.fog=new THREE.Fog(BG,4,52);camera.position.set(0,0,10);camera.lookAt(0,0,-30);
const mat=new THREE.LineBasicMaterial({color:TEAL,transparent:true,opacity:0.7});
for(let i=0;i<40;i++){const z=-i*1.6+8;const s=5+Math.sin(i*0.3)*0.6;
 const pts=[[-s,-s],[s,-s],[s,s],[-s,s],[-s,-s]].map(p=>new THREE.Vector3(p[0],p[1],z));
 const g=new THREE.BufferGeometry().setFromPoints(pts);const l=new THREE.Line(g,mat.clone());l.material.opacity=0.75*(1-i/44);scene.add(l);}
sprite(glow(TEALG),22,[0,0,-30]);`,

'candles': `
scene.fog=new THREE.Fog(BG,10,64);camera.position.set(2,4,16);camera.lookAt(-2,1,-14);
scene.add(new THREE.AmbientLight(0x335,0.6));const dl=new THREE.DirectionalLight(0x9fe6d6,1.1);dl.position.set(4,10,8);scene.add(dl);
for(let i=0;i<70;i++){const up=rnd()>0.42;const h=0.6+rnd()*3;
 const m=new THREE.Mesh(new THREE.BoxGeometry(0.7,h,0.7),new THREE.MeshStandardMaterial({color:up?TEAL:RED,emissive:up?0x0c3a2a:0x3a0c12,roughness:0.4,metalness:0.2}));
 m.position.set((rnd()-0.5)*28,(rnd()-0.3)*8,-rnd()*40);scene.add(m);
 const w=new THREE.Mesh(new THREE.BoxGeometry(0.08,h+1.2,0.08),new THREE.MeshBasicMaterial({color:up?TEAL:RED}));w.position.copy(m.position);scene.add(w);}`,

'gem': `
scene.fog=new THREE.Fog(BG,8,60);camera.position.set(0,0,10);camera.lookAt(0,0,0);
const geo=new THREE.IcosahedronGeometry(4,1);
scene.add(new THREE.LineSegments(new THREE.WireframeGeometry(geo),new THREE.LineBasicMaterial({color:MINT,transparent:true,opacity:0.55})));
scene.add(new THREE.Mesh(geo,new THREE.MeshBasicMaterial({color:TEAL,transparent:true,opacity:0.05})));
sprite(glow(TEALG),24,[0,0,-4]);
const pos=[];for(let i=0;i<500;i++){const a=rnd()*7,b=rnd()*7,r=6+rnd()*10;pos.push(Math.cos(a)*Math.cos(b)*r,Math.sin(b)*r,Math.sin(a)*Math.cos(b)*r-3);}
const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
scene.add(new THREE.Points(g,new THREE.PointsMaterial({color:MINT,size:0.07,transparent:true,opacity:0.6})));`,

'terrain': `
scene.fog=new THREE.Fog(BG,6,55);camera.position.set(0,3.4,13);camera.lookAt(0,1,-24);
const geo=new THREE.PlaneGeometry(80,80,80,80);const p=geo.attributes.position;
for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i);const d=Math.hypot(x,y);
 let z=Math.sin(x*0.35)*Math.cos(y*0.35)*1.6 + Math.sin(d*0.5)*0.8;if(d<10)z*=(d/10);p.setZ(i,z);}
geo.computeVertexNormals();const m=new THREE.Mesh(geo,new THREE.MeshBasicMaterial({color:TEAL,wireframe:true,transparent:true,opacity:0.6}));
m.rotation.x=-Math.PI/2;m.position.set(0,-1.5,-16);scene.add(m);
sprite(glow([[0,'rgba(224,255,246,0.9)'],[0.35,'rgba(46,204,154,0.5)'],[1,'rgba(46,204,154,0)']]),22,[0,6,-40]);`,

'wavefield': `
scene.fog=new THREE.Fog(BG,8,60);camera.position.set(0,6,13);camera.lookAt(0,0,-16);
const pos=[];for(let x=-30;x<=30;x++)for(let z=0;z<=60;z++){const X=x*0.9,Z=-z*0.9;const Y=Math.sin(X*0.4+Z*0.15)*0.9+Math.cos(Z*0.3)*0.6;pos.push(X,Y,Z+6);}
const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
scene.add(new THREE.Points(g,new THREE.PointsMaterial({color:TEAL,size:0.075,transparent:true,opacity:0.85,blending:THREE.AdditiveBlending,depthWrite:false})));`,

'network': `
scene.fog=new THREE.Fog(BG,10,64);camera.position.set(0,0,16);camera.lookAt(0,0,0);
const N=90,nodes=[];for(let i=0;i<N;i++)nodes.push(new THREE.Vector3((rnd()-0.5)*26,(rnd()-0.5)*30,-rnd()*24));
const lp=[];for(let i=0;i<N;i++)for(let j=i+1;j<N;j++){if(nodes[i].distanceTo(nodes[j])<5.2){lp.push(nodes[i].x,nodes[i].y,nodes[i].z,nodes[j].x,nodes[j].y,nodes[j].z);}}
const lg=new THREE.BufferGeometry();lg.setAttribute('position',new THREE.Float32BufferAttribute(lp,3));
scene.add(new THREE.LineSegments(lg,new THREE.LineBasicMaterial({color:TEAL,transparent:true,opacity:0.28})));
const np=[];nodes.forEach(n=>np.push(n.x,n.y,n.z));const ng=new THREE.BufferGeometry();ng.setAttribute('position',new THREE.Float32BufferAttribute(np,3));
scene.add(new THREE.Points(ng,new THREE.PointsMaterial({color:MINT,size:0.32,transparent:true,opacity:0.95,blending:THREE.AdditiveBlending,depthWrite:false})));`,

'rings': `
scene.fog=new THREE.Fog(BG,7,58);camera.position.set(0,2.2,12);camera.lookAt(0,0.5,-22);
for(let i=0;i<16;i++){const r=2+i*1.7;const tg=new THREE.TorusGeometry(r,0.03,8,120);
 const t=new THREE.Mesh(tg,new THREE.MeshBasicMaterial({color:i%2?MINT:TEAL,transparent:true,opacity:0.5*(1-i/20),blending:THREE.AdditiveBlending}));
 t.rotation.x=Math.PI/2;t.position.set(0,-1,-i*2.2);scene.add(t);}
sprite(glow(TEALG),20,[0,0,-34]);`,

'nebula': `
scene.fog=new THREE.Fog(BG,12,80);camera.position.set(0,0,17);camera.lookAt(0,0,0);
const P=5000,pos=[],col=[];const c1=new THREE.Color(TEAL),c2=new THREE.Color(0x5aa0c8);
for(let i=0;i<P;i++){const u=rnd(),v=rnd();const th=u*2*Math.PI,ph=Math.acos(2*v-1);const r=5+rnd()*rnd()*7;
 pos.push(Math.sin(ph)*Math.cos(th)*r,Math.sin(ph)*Math.sin(th)*r*0.8,Math.cos(ph)*r-4);
 const cc=c1.clone().lerp(c2,rnd());col.push(cc.r,cc.g,cc.b);}
const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('color',new THREE.Float32BufferAttribute(col,3));
scene.add(new THREE.Points(g,new THREE.PointsMaterial({size:0.11,vertexColors:true,transparent:true,opacity:0.8,blending:THREE.AdditiveBlending,depthWrite:false})));
sprite(glow([[0,'rgba(123,235,200,0.5)'],[0.4,'rgba(46,204,154,0.16)'],[1,'rgba(46,204,154,0)']]),26,[0,0,-4]);`,
};

function findChromium(){const ok=p=>p&&fs.existsSync(p)?p:null;if(ok(process.env.CHROMIUM_PATH))return process.env.CHROMIUM_PATH;
  try{for(const d of fs.readdirSync('/opt/pw-browsers')){if(/^chromium-\d+$/.test(d)){for(const r of ['chrome-linux/chrome','chrome-linux64/chrome']){const c=ok(path.join('/opt/pw-browsers',d,r));if(c)return c;}}}}catch(_){}
  try{const p=require('playwright-core').chromium.executablePath();if(ok(p))return p;}catch(_){}return undefined;}

async function renderScene(name, { out='bg.png', width=1080, height=1350, scale=2, browser=null } = {}){
  if(!SCENES[name]) throw new Error(`unknown scene "${name}". options: ${Object.keys(SCENES).join(', ')}`);
  const threeB64 = fs.readFileSync(path.join(__dirname,'three.bundle.js')).toString('base64');
  const html = `<!doctype html><meta charset=utf8>
    <script type="importmap">{"imports":{"three":"data:text/javascript;base64,${threeB64}"}}<\/script>
    <style>*{margin:0;padding:0}body{background:#0A171C;overflow:hidden}</style>
    <script type="module">${HEAD(width,height)}${SCENES[name]}${TAIL}<\/script>`;
  const { chromium } = require('playwright-core');
  const b = browser || await chromium.launch({ executablePath:findChromium(),
    args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--force-color-profile=srgb'] });
  const p = await b.newPage({ viewport:{width,height}, deviceScaleFactor:scale });
  await p.setContent(html,{waitUntil:'load'});
  await p.waitForFunction('window.__done===true',{timeout:25000});
  await p.waitForTimeout(150);
  await p.locator('canvas').screenshot({ path: out });
  await p.close();
  if(!browser) await b.close();
  return out;
}

module.exports = { SCENES, renderScene };

if(require.main===module){
  const arg=(n,d)=>{const i=process.argv.indexOf('--'+n);return i<0?d:(process.argv[i+1]&&!process.argv[i+1].startsWith('--')?process.argv[i+1]:true);};
  (async()=>{
    const width=+arg('width',1080),height=+arg('height',1350),scale=+arg('scale',2);
    if(arg('all',false)){
      const dir=arg('outdir','.'); fs.mkdirSync(dir,{recursive:true});
      const { chromium }=require('playwright-core');
      const b=await chromium.launch({executablePath:findChromium(),args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--force-color-profile=srgb']});
      const names=Object.keys(SCENES); let i=0;
      for(const n of names){ i++; const num=String(i).padStart(2,'0');
        await renderScene(n,{out:path.join(dir,`bg-${num}-${n}.png`),width,height,scale,browser:b}); console.error('rendered',n); }
      await b.close();
    } else {
      const name=arg('scene','gem'), out=arg('out','bg.png');
      await renderScene(name,{out,width,height,scale}); console.error('rendered',name,'->',out);
    }
  })().catch(e=>{console.error('ERROR:',e.message);process.exit(1);});
}
