---
layout: post
title: "go get proxy"
categories: tools
date: 2020-05-10 00:00:00
---

在苏联无法获取 golang 的 包体，所以需要设置代理。

```bash
go env -w GO111MODULE=on
go env -w GOPROXY=https://goproxy.io,direct

# 设置不走 proxy 的私有仓库，多个用逗号相隔（可选）
go env -w GOPRIVATE=*.corp.example.com
```

具体参见 https://goproxy.io/zh/。

注意，`GO111MODULE` 会导致一些旧的 project layout 工作不正常。