# 月下研究室 · Moonlit Lab

这是我的静态个人学术网站，集中整理数学、统计、物理、天文、文学与动画文本分析相关的学习记录和项目。

网站位于 [docs/index.html](docs/index.html)，所有 CSS、JavaScript 和文章均位于 `docs/`，与仓库原有的学术资料及 Jekyll 模板分开维护。

## GitHub Pages 发布
1. 打开本仓库 **Settings → Pages**
2. **Source** 选择 **Deploy from a branch**
3. Branch 选择 **main**，Folder 选择 **/docs**，点击 **Save**
4. GitHub Pages 完成部署后会提供公开网址：`https://child-of-the-unbound-lord.github.io/Song-of-Righteousness-in-Mathematics-and-Physics/`

上面的网址在 GitHub Pages 成功发布前不代表已经可访问。

## 内容与来源
- 所属 GitHub 用户： [Child-of-the-Unbound-Lord](https://github.com/Child-of-the-Unbound-Lord)
- 学术文章中的示例内容均标明为示例；尚未添加的论文、正式 CV、DOI 等不伪造
- 四套主题：樱岛麻衣、雪之下雪乃、芙莉莲、千反田爱瑠，使用原创抽象月夜视觉，不使用官方角色插画
- 评论采用 giscus，须先在公开仓库启用 GitHub Discussions 并授权 giscus，再在 `docs/assets/data.js` 填写 repo 与 category ID
- 代码为纯静态网页，无需构建步骤；本地预览 `cd docs && python3 -m http.server 8000`

## 注意
本仓库原有目录并未被替换。月下研究室网页文件集中在 `docs/`。个人身份和联系方式仅在确认后公开。
