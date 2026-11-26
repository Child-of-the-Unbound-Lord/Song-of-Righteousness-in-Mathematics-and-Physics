/* Moonlit Lab comments: opt-in third-party loading, one discussion per page. */
(() => {
  'use strict';
  const cfg = window.LAB_GISCUS || {};
  const host = document.getElementById('comment-box');
  if (!host) return;
  const ready = cfg.enabled === true && /^[\w-]+\/[\w.-]+$/.test(cfg.repo || '')
    && /^R_[\w-]+$/.test(cfg.repo_id || '') && /^DIC_[\w-]+$/.test(cfg.category_id || '');
  if (!ready) return; // The build supplies an accurate, accessible setup notice.

  host.replaceChildren();
  host.classList.remove('empty');
  host.classList.add('comment-shell');
  const text = (tag, value, className) => {
    const element = document.createElement(tag);
    element.textContent = value;
    if (className) element.className = className;
    return element;
  };
  host.appendChild(text('p', '本页的评论公开保存在 GitHub Discussions。点击载入后，浏览器会连接 giscus.app；发表评论需要 GitHub 登录。', 'comment-privacy'));
  const actions = document.createElement('div');
  actions.className = 'comment-actions';
  const loadButton = text('button', '载入本页评论', 'comment-load');
  loadButton.type = 'button';
  const discussionLink = text('a', '直接打开 GitHub Discussions ↗');
  discussionLink.href = `https://github.com/${cfg.repo}/discussions`;
  discussionLink.target = '_blank';
  discussionLink.rel = 'noopener noreferrer';
  actions.append(loadButton, discussionLink);
  host.append(actions);
  const status = text('p', '', 'comment-status');
  status.setAttribute('role', 'status');
  host.append(status);
  const embed = document.createElement('div');
  embed.className = 'comment-frame';
  embed.setAttribute('aria-label', 'GitHub Discussions 评论');
  host.append(embed);

  const resolveTheme = () => {
    const id = document.body.dataset.theme;
    return id === 'yukino' || id === 'eru' ? 'dark' : 'dark_dimmed';
  };
  const syncTheme = () => {
    const frame = embed.querySelector('iframe.giscus-frame');
    if (frame?.contentWindow) {
      frame.contentWindow.postMessage({giscus:{setConfig:{theme:resolveTheme()}}}, 'https://giscus.app');
    }
  };
  new MutationObserver(syncTheme).observe(document.body, {attributes:true, attributeFilter:['data-theme']});
  let loaded = false;
  const load = () => {
    if (loaded) return;
    loaded = true;
    loadButton.disabled = true;
    loadButton.textContent = '正在载入评论…';
    status.textContent = '正在连接 giscus 评论服务。';
    const script = document.createElement('script');
    script.src = 'https://giscus.app/client.js';
    script.crossOrigin = 'anonymous';
    script.async = true;
    const settings = {
      repo: cfg.repo,
      'repo-id': cfg.repo_id,
      category: cfg.category || 'General',
      'category-id': cfg.category_id,
      mapping: cfg.mapping || 'pathname',
      strict: '1',
      'reactions-enabled': cfg.reactions_enabled === false ? '0' : '1',
      'emit-metadata': '0',
      'input-position': cfg.input_position || 'top',
      theme: resolveTheme(),
      lang: cfg.lang || 'zh-CN',
      loading: 'lazy'
    };
    for (const [key,value] of Object.entries(settings)) script.setAttribute(`data-${key}`,String(value));
    script.addEventListener('load', () => {
      status.textContent = '评论已载入。如果没有显示，请核对仓库权限或通过 GitHub Discussions 打开。';
      loadButton.hidden = true;
      syncTheme();
    });
    script.addEventListener('error', () => {
      loaded = false;
      script.remove();
      loadButton.disabled = false;
      loadButton.textContent = '重新尝试载入评论';
      status.textContent = '评论服务暂时无法加载。你仍可前往 GitHub Discussions 参与讨论。';
    });
    embed.append(script);
  };
  loadButton.addEventListener('click', load);
  // Keep the external service unloaded until the reader explicitly chooses it.
})();
