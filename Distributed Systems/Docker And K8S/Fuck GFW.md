如果网络访问出现问题，请参考[此处](https://github.com/AliyunContainerService/k8s-for-docker-desktop)。

首先删除 `C:\ProgramData\DockerDesktop\pki` 文件夹，随后在 Powershell 中执行命令：

```powersh
Set-ExecutionPolicy RemoteSigned
```

即可。