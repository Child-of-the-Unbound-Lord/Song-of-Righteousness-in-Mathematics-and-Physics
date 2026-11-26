'use strict';
try{const value=localStorage.getItem('moonlit-theme');if(['mai','yukino','frieren','eru'].includes(value))document.body.dataset.theme=value}catch{}
const copy=document.getElementById('copy-link');
copy?.addEventListener('click',async()=>{
 try{await navigator.clipboard.writeText(location.href);copy.textContent='已复制链接'}catch{copy.textContent='请复制地址栏链接'}
});
document.getElementById('print')?.addEventListener('click',()=>window.print());
document.querySelectorAll('.article pre').forEach(pre=>{
 const btn=document.createElement('button');btn.className='code-copy';btn.textContent='复制代码';
 btn.addEventListener('click',async()=>{
  try{await navigator.clipboard.writeText(pre.querySelector('code')?.innerText||pre.innerText);btn.textContent='已复制'}
  catch{btn.textContent='复制失败';}
 });
 pre.prepend(btn);
});
