(()=>{'use strict';
const $=s=>document.querySelector(s);
const all=s=>[...document.querySelectorAll(s)];
const themes=Object.fromEntries((window.LAB_THEMES||[]).map(x=>[x.id,x]));
let mode='all';
let previous=null;
try{previous=localStorage.getItem('moonlit-theme')}catch{}
let current=themes[previous]?previous:'mai';
function theme(id){
  if(!themes[id])return;
  current=id;
  document.body.dataset.theme=id;
  try{localStorage.setItem('moonlit-theme',id)}catch{}
  const settings=themes[id];
  const caption=$('#theme-caption');if(caption)caption.textContent=settings.caption;
  const image=$('#theme-illustration');if(image){image.src=settings.image;image.alt=settings.description;}
  all('[data-settheme]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.settheme===id)));
}
all('[data-settheme]').forEach(button=>button.addEventListener('click',()=>theme(button.dataset.settheme)));
theme(current);
const read=$('#read-mode');if(read)read.addEventListener('click',()=>{
  const enabled=document.body.classList.toggle('reading');
  read.setAttribute('aria-pressed',String(enabled));read.textContent=enabled?'退出专注':'专注阅读';
});
const notes=window.LAB_NOTES||[];
let type='all';
function escapeHtml(value){return String(value||'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));}
function render(){
  const query=$('#query');const list=$('#note-list');if(!query||!list)return;
  const term=query.value.trim().toLocaleLowerCase();
  const found=notes.filter(note=>(type==='all'||note.tag===type)&&[note.title,note.type,note.excerpt,...(note.keywords||[])].join(' ').toLocaleLowerCase().includes(term));
  list.innerHTML=found.map(note=>`<a class="note" href="posts/${encodeURIComponent(note.slug)}.html"><div><small>${escapeHtml(note.date)} · ${escapeHtml(note.type)}</small><h3>${escapeHtml(note.title)}${note.demo?'<em>排版示例</em>':''}</h3><p>${escapeHtml(note.excerpt)}</p></div><span aria-hidden="true">↗</span></a>`).join('');
  const empty=$('#no-results');if(empty)empty.hidden=!!found.length;
}
$('#query')?.addEventListener('input',render);
all('[data-filter]').forEach(button=>button.addEventListener('click',()=>{
 type=button.dataset.filter;
 all('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
 render();
}));
render();
const year=$('#year');if(year)year.textContent=new Date().getFullYear();
all('.bibtex-copy').forEach(button=>button.addEventListener('click',async()=>{
 try{await navigator.clipboard.writeText(button.dataset.bibtex||'');button.textContent='已复制 BibTeX';}
 catch{button.textContent='复制失败';}
}));
})();
