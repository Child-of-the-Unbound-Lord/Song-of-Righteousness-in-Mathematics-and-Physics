# 月下研究室 · Moonlit Lab

一个无构建依赖的静态个人学术主页，适合 GitHub Pages、Cloudflare Pages 或其他静态托管。默认四套月夜主题；包含真实 GitHub 账号链接、已核实的公开仓库、示例文章、全文检索、标签筛选、专注阅读、文章目录、代码复制和打印/PDF 功能。

## 本地预览

```bash
python3 -m http.server 8000
```

浏览器打开 http://localhost:8000 。也可以直接打开 `index.html`，但建议使用本地服务器以模拟部署环境。

## 内容维护

- `index.html`：主页文案、研究方向、项目列表及个人信息；所有待核实的论文、经历都明确留空。
- `assets/data.js`：文章目录数据、筛选关键词和 giscus 配置。
- `posts/*.html`：示例文章。**示例不是你的研究成果**，请替换为真实文章后再对外宣传。
- `assets/style.css`：全站配色与页面布局。
- `assets/app.js`：主题记忆、搜索筛选、阅读模式、评论挂载。

## GitHub 评论

1. 选定一个 **公开** 的 GitHub 仓库（可以使用专门的评论仓库），在 Settings → General → Features 中开启 Discussions。
2. 在 https://github.com/apps/giscus 安装 giscus 并授予对应仓库权限。
3. 打开 https://giscus.app/zh-CN ，选择仓库和 Discussions 分类。
4. 将配置生成器里的 `repo`、`repoId`、`category`、`categoryId` 填入 `assets/data.js` 中 `LAB_GISCUS`。不要填入 GitHub 密码或令牌。
5. 评论区会自动显示。注意：即使网页是私密预览，公开仓库里的 Discussions 仍可公开阅读。

## 发布

GitHub Pages：上传文件到仓库根目录，Settings → Pages 选择主分支（`main`）的根目录。若仓库发布在 `/repository-name/` 下，使用本站相对链接依旧可以正常导航。

## 账号与署名

GitHub 账号 `Child-of-the-Unbound-Lord` 来自已连接账号的资料。公开仓库只陈述仓库存在，不将仓库模板中的示例论文、身份、姓名或其他作者的资料冒充用户成果。四种主题是原创抽象月夜场景，借用了角色的气质与色彩，**没有使用官方番剧立绘**。

## 功能边界

- 当前未配置真实评论（尚未获取 giscus 仓库与分类 ID）。
- 当前没有个人论文/正式简历 PDF 文件，不能提供真实下载。
- 全文搜索目前索引 `assets/data.js` 的标题、摘要与关键词，不包含文章正文；如需正文检索，可后续生成统一索引。
- 本版本是独立可运行的源码升级包，没有覆盖之前私密部署的 Sites 仓库，也未推送到任何其他用途的 GitHub 仓库。
