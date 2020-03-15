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