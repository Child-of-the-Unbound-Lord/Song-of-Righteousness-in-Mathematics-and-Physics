'use strict';
try{const value=localStorage.getItem('moonlit-theme');if(['mai','yukino','frieren','eru'].includes(value))document.body.dataset.theme=value}catch{}
const copy=document.getElementById('copy-link');
copy?.addEventListener('click',async()=>{
 try{await navigator.clipboard.writeText(location.href);copy.textContent='已复制链接'}catch{copy.textContent='请复制地址栏链接'}
});
document.getElementById('print')?.addEventListener('click',()=>window.print());
document.querySelectorAll('.article pre').forEach(pre=>{
 const btn=document.createElement('button');btn.className='code-copy';btn.textContent='复制代码';btn.type='button';
 btn.addEventListener('click',async()=>{
  try{await navigator.clipboard.writeText(pre.querySelector('code')?.innerText||pre.innerText);btn.textContent='已复制'}
  catch{btn.textContent='复制失败';}
 });
 pre.prepend(btn);
});
// A quiet reading progress line and active chapter indication help with long proofs.
const progress=document.createElement('div');
progress.className='reading-progress';
progress.setAttribute('aria-hidden','true');
document.body.appendChild(progress);
const tocLinks=[...document.querySelectorAll('.toc a[href^="#"]')];
const headings=[...document.querySelectorAll('.prose h2[id],.prose h3[id]')];
let scheduled=false;
function updateReadingPosition(){
 scheduled=false;
 const root=document.documentElement;
 const total=Math.max(0,root.scrollHeight-window.innerHeight);
 const fraction=total>0?Math.min(1,Math.max(0,window.scrollY/total)):1;
 progress.style.transform=`scaleX(${fraction})`;
 let current='';
 for(const heading of headings){
  if(heading.getBoundingClientRect().top<=140)current=heading.id;
  else break;
 }
 tocLinks.forEach(link=>{
  const active=decodeURIComponent(link.getAttribute('href').slice(1))===current;
  link.classList.toggle('toc-active',active);
  if(active)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');
 });
}
function schedulePosition(){if(!scheduled){scheduled=true;requestAnimationFrame(updateReadingPosition)}}
window.addEventListener('scroll',schedulePosition,{passive:true});
window.addEventListener('resize',schedulePosition);
window.addEventListener('load',schedulePosition);
schedulePosition();
