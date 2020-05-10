---
layout: post
title: "Use SecCrt and FF as Proxy"
categories: tools
date: 2020-05-10 00:00:00
---

## SecureCrt

- Property
  - Portforwarding
    - Add
    - Local.Port = 8888
    - Dynamic forwarding using SOCKS 4
- Reconnect SSH

## Firefox

- 连接设置
  - 手动配置
    - SOCKS 主机
      - SOCKS V5
      - IP = 127.0.0.1
      - Port = 8888
  - 不使用代理 = localhost, 127.0.0.1
- about:config
  - network.proxy.socks_remote_dns = true