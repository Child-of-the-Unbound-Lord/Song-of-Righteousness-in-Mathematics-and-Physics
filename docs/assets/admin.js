/* Admin helper: public status + no-credential giscus configuration. */
(() => {
  'use strict';
  const repo = 'Child-of-the-Unbound-Lord/Song-of-Righteousness-in-Mathematics-and-Physics';
  const repoId = 'R_kgDOSfTXGA';
  const $ = id => document.getElementById(id);
  const status = $('discussion-state');
  async function checkDiscussionStatus() {
    if (!status) return;
    status.textContent = '正在读取公开仓库状态…';
    try {
      const response = await fetch(`https://api.github.com/repos/${repo}`, {
        headers: {Accept:'application/vnd.github+json'}, cache:'no-store'
      });
      if (!response.ok) throw new Error('status ' + response.status);
      const data = await response.json();
      status.textContent = data.has_discussions
        ? 'Discussions 已开启。下一步授权 giscus App，并填写分类 ID。'
        : 'Discussions 尚未开启。请在仓库 Settings → General → Features 打开 Discussions。';
      status.dataset.ready = data.has_discussions ? 'yes' : 'no';
    } catch {
      status.textContent = '无法自动检查 GitHub 状态；请打开仓库设置手动确认。';
      status.dataset.ready = 'unknown';
    }
  }
  const output = $('comment-yaml-output');
  const categoryId = $('comment-category-id');
  const category = $('comment-category');
  const embedCode = $('giscus-embed-code');
  const feedback = $('admin-feedback');
  const escapeYaml = value => `'${String(value).replace(/'/g,"''")}'`;
  function generate() {
    const id = categoryId?.value.trim() || '';
    const name = category?.value.trim() || 'General';
    const valid = /^DIC_[\w-]{6,}$/.test(id);
    output.value = [
      `enabled: ${valid ? 'true' : 'false'}`,
      `repo: ${escapeYaml(repo)}`,
      `repo_id: ${escapeYaml(repoId)}`,
      `category: ${escapeYaml(name)}`,
      `category_id: ${escapeYaml(id)}`,
      "mapping: pathname",
      "lang: zh-CN",
      "input_position: top",
      "reactions_enabled: true",
      "notice: 评论尚未开放。管理员需先开启 Discussions、安装 giscus 并填写分类 ID。"
    ].join('\n') + '\n';
    feedback.textContent = valid ? '配置格式已准备好。只有确认 Discussions 和 App 授权后，才应保存并启用。'
      : '尚未填入有效的 Category ID，生成的配置会保持评论关闭。';
  }
  $('check-discussions')?.addEventListener('click', checkDiscussionStatus);
  $('read-giscus-code')?.addEventListener('click', () => {
    const content = embedCode.value;
    const get = key => {
      const re = new RegExp('data-' + key + '\\s*=\\s*["\\\']([^"\\\']+)["\\\']','i');
      return content.match(re)?.[1] || '';
    };
    const foundRepo = get('repo');
    if (foundRepo && foundRepo !== repo) {
      feedback.textContent = '检测到 giscus 代码的仓库不是当前网站仓库，请检查后再导入。';
      return;
    }
    if (get('category-id')) categoryId.value = get('category-id');
    if (get('category')) category.value = get('category');
    generate();
  });
  categoryId?.addEventListener('input', generate);
  category?.addEventListener('input', generate);
  $('copy-comment-yaml')?.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(output.value);
      feedback.textContent = '配置已复制。可直接粘贴到 GitHub 的 comments.yml 文件，或在 Pages CMS 逐项填写。';
    } catch {
      feedback.textContent = '浏览器未授权剪贴板，请手动选中下方配置并复制。';
      output.focus(); output.select();
    }
  });
  generate();
  checkDiscussionStatus();
})();
