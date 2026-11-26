# 月下研究室 · Moonlit Lab

公开网站：<https://child-of-the-unbound-lord.github.io/Song-of-Righteousness-in-Mathematics-and-Physics/>

**管理内容：** <https://child-of-the-unbound-lord.github.io/Song-of-Righteousness-in-Mathematics-and-Physics/admin/> → 点击「使用 GitHub 登录内容后台」。

本文档是网站子项目的维护说明；源文件放在 GitHub 仓库根目录的 `site-content/`、`site-tools/` 和 `docs/` 中。仓库原有的 al-folio 源码未删除。

## 每天怎样更新

打开 <https://app.pagescms.org/>，使用 GitHub 登录，并将 Pages CMS GitHub App 授权到 `Child-of-the-Unbound-Lord/Song-of-Righteousness-in-Mathematics-and-Physics`（只授权这个仓库即可）。选 `main` 分支，按栏目修改内容并保存。Pages CMS 将更新写入 GitHub，仓库工作流会重新生成并部署网站。不需要使用 Git 命令。

内容入口：

- **首页和关于我** — `site-content/site.yml`，可编辑标题、简介、研究室说明、栏目文案及 GitHub 用户名。
- **Markdown 文章** — `site-content/articles/*.md`，增加、删除、修改文章。支持 `draft: true` 草稿不公开；`sample: true` 表示排版示例。
- **研究方向 / 项目列表 / 论文与成果** — `site-content/research.yml`、`projects.yml`、`publications.yml`。
- **四套角色主题** — `site-content/themes.yml`，可修改主题文案与插画路径；上传媒体后更新 `image` 字段。CSS 的配色如要更改需修改 `docs/assets/style.css`，普通文本内容不用碰代码。
- **评论设置** — `site-content/comments.yml`。只有仓库开启 Discussions、安装 giscus 且 category_id 正确时才应设置 `enabled: true`。

**公式写法**：在 Pages CMS 正文编辑器中切换到 **Source（源码）** 模式；可用 `$E=mc^2$`、`$$...$$`、`\\(...\\)`、`\\[...\\]`。构建时 KaTeX 0.19.1 在服务器端直接渲染为 HTML + MathML，访客无需等待数学脚本加载，`docs/assets/katex` 字体与样式会一起发布。

````md
## 一个新标题

行内公式：$a^2+b^2=c^2$。

$$
\sum_{k=1}^{n} k = \frac{n(n+1)}{2}
$$

```python
print("hello")
```
````

## 评论启用

评论页使用“先确认、后加载”的设计：读者点击载入后才会连接 giscus；同一篇文章按路径关联独立 Discussion。管理员可在 **管理内容 → 评论设置助手** 粘贴 giscus 生成的脚本并得到完整 YAML，无需手写仓库 ID。

1. 仓库 **Settings → General → Features** 勾选 Discussions。
2. 在 <https://github.com/apps/giscus> 安装 giscus GitHub App，只授予此仓库访问权限。
3. 在 <https://giscus.app/zh-CN> 填入仓库，选择 `General` 分类，将生成的 `<script>` 复制到管理页的配置助手（或直接将 `data-category-id` 填入内容后台评论设置）。
4. 在后台打开「启用评论」并保存，等待工作流发布成功。

评论数据存放在公开的 GitHub Discussions，访客用 GitHub 登录，管理员在 Discussions 中审核和管理评论。打开以前保留「评论尚未开放」提示，不会伪装为已接入。

## 网站品质与阅读体验

- 每篇文章有阅读进度条、活动目录高亮、复制链接和代码复制。
- 网站自动生成 `feed.xml` 与 `sitemap.xml`，加入新文章无需另外手工维护订阅源。
- 评论默认手动载入，避免未同意时直接连接第三方 giscus；开启后可按文章路径对应独立 Discussion。

## 技术与自动部署

GitHub Actions：`.github/workflows/moonlit-pages.yml`，对 `site-content/**`、`site-tools/**` 和相关素材的变更自动部署。

流程：Python 读取 YAML 和 Markdown → markdown-it-py 解析正文 → Node KaTeX 服务端输出公式 HTML → 复制 KaTeX CSS / 字体 → `docs/` 打包成 GitHub Pages 静态网站 → 自动 HTTP 线上验收。

本地需要 Python 3.12、Node 22 和对应依赖：

```bash
python -m pip install -r site-tools/requirements.txt
npm install --prefix site-tools --no-save --no-package-lock katex@0.19.1
python site-tools/build_site.py
mkdir -p docs/assets/katex/fonts
cp site-tools/node_modules/katex/dist/katex.min.css docs/assets/katex/
cp site-tools/node_modules/katex/dist/fonts/*.woff2 docs/assets/katex/fonts/
python site-tools/check_build.py
python -m http.server 8000 -d docs
```

`site-tools/build_site.py --preview` 仅适合没有安装 KaTeX 的本地布局预览：**预览模式会保留 LaTeX 原文，不视为公式渲染成功**。正式工作流必须完整渲染，否则构建失败。

## 内容边界

当前三篇文章是明确标注的排版示例，不是作者的研究成果；论文列表默认为空，防止把演示文章冒充论文。主题素材是原创场景与角色气质的视觉设计，不复制番剧现有截图或官方立绘。
