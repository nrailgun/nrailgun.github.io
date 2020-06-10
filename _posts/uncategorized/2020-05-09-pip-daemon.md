---
layout: post
title: "Pip 镜像"
categories: uncategorized
date: 2020-05-09 00:00:00
---

临时处理：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package
```

配置：

```bash
pip install pip -U
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

