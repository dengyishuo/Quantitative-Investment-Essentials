# 构建脚本

运行：

```bash
python script/build_book.py
```

脚本从根目录 `README.md` 解析前言、正文各章和参考文献的顺序，调用Pandoc生成HTML和EPUB，并将结果写入 `dist/`。

构建GitHub Pages多页电子书：

```bash
python script/build_site.py
```

网站入口为 `dist/site/index.html`。GitHub Actions会自动执行EPUB和网站构建。

本地预览可以运行：

```bash
python -m http.server 8000 --directory dist/site
```

