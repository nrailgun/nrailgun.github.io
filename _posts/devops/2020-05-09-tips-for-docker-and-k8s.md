---
layout: post
title: "Tips for Docker and K8S"
categories: DevOps
date: 2020-05-09 15:37:07
---

## 网络问题

如果网络访问出现问题，请参考[此处](https://github.com/AliyunContainerService/k8s-for-docker-desktop)。

首先删除 `C:\ProgramData\DockerDesktop\pki` 文件夹，随后在 Powershell 中执行命令：

```powersh
Set-ExecutionPolicy RemoteSigned
```

即可。

## 运行本地镜像

要么为本地镜像加上标签（而不是默认的 `latest`），要么设置 `image-pull-policy`。

```
kubectl run kubia --image=kubia --port=8080 --generator=run/v1 --image-pull-policy=Never
```

