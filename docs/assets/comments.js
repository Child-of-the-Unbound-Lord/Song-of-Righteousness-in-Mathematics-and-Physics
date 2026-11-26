(()=>{'use strict';
const cfg=window.LAB_GISCUS||{};
const box=document.getElementById('comment-box');
if(!box||!cfg.enabled||!cfg.repo||!cfg.repo_id||!cfg.category_id)return;
box.innerHTML='';
box.classList.remove('empty');
const script=document.createElement('script');
script.src='https://giscus.app/client.js';
script.crossOrigin='anonymous';
script.async=true;
Object.entries({
  repo:cfg.repo,
  'repo-id':cfg.repo_id,
  category:cfg.category||'General',
  'category-id':cfg.category_id,
  mapping:'pathname',
  strict:'1',
  'reactions-enabled':'1',
  'emit-metadata':'0',
  'input-position':'top',
  theme:window.matchMedia('(prefers-color-scheme: light)').matches?'light':'dark_dimmed',
  lang:'zh-CN',
  loading:'lazy'
}).forEach(([key,value])=>script.setAttribute('data-'+key,String(value)));
box.appendChild(script);
})();
