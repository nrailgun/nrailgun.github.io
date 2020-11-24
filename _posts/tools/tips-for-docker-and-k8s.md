## 网络问题

如果网络访问出现问题，请参考[此处](https://github.com/AliyunContainerService/k8s-for-docker-desktop)。

首先删除 `C:\ProgramData\DockerDesktop\pki` 文件夹，随后在 Powershell 中执行命令：

```powersh
Set-ExecutionPolicy RemoteSigned
```

## 文件锁住导致 docker 启动、安装失败

可以可以参考[此处](https://gallery.technet.microsoft.com/How-to-find-out-which-c0d4e60e)看看是什么在搞破坏，但是一般是 Hyper-V 的虚拟机导致的。社区反馈删除 Hyper-V 虚拟机 即可，由于 Windows 10 的 bug，某些版本无法删除掉该虚拟机。我的方法是直接关闭 Hyper-V 特性，然后重启。

## 运行本地镜像

要么为本地镜像加上标签（而不是默认的 `latest`），要么设置 `image-pull-policy`。

```bash
kubectl run kubia --image=kubia --port=8080 --generator=run/v1 --image-pull-policy=Never
```

## 运行 BusyBox

BusyBox 主要是为了在集群中进行 debug 较为方便。

```bash
kubectl run -it busybox --image=busybox --restart=Never --rm -- sh
```

busybox 的镜像有时候更迭之后会出 bug，导致 `nslookup` 不可用。坑爹。

## 删除所有容器

```bash
docker container rm `docker ps -aq`
```

## Hyper-V Docker Desktop HostPath 定位错误

这似乎是 docker desktop 的 bug，无论是 unix 路径格式或者 win 路径格式都不对。

## Change kube-proxy Mode

```bash
kubectl -n kube-system edit configmap kube-proxy
kubectl -n kube-system get pod
kubectl -n kube-system delete pod kube-proxy-OOOOO
```

```bash
kubectl cluster-info # get kube-master
```

## 网络错误定位

查看路由规则：

```bash
route # unix
route print # windows
netsh int ipv4 show interfaces # 查看 ethernet interface index
```

查看 IP 包跳转：

```bash
traceroute www.google.com
```

## 更改 ConfigMap

```bash
kubectl create configmap game --from-file=etc
kubectl edit cm game # 不需要重启
```

## 从物理机访问容器

[在 windows 下并不能访问 linux 容器](https://docs.docker.com/docker-for-windows/networking/)，这是 windows 和 docker desktop 的实现决定的（靠北= =#！）。

> ### I cannot ping my containers
>
> Docker Desktop for Windows can’t route traffic to Linux containers.  However, you can ping the Windows containers.

在 Debian 9 下测试过，可以在 host ping 通 container。

## 开多一个 bash

```bash
docker run -it --rm -d bash
docker exec -it $ID bash
```

## 拷贝 container 文件到 host

```bash
docker cp <containerId>:/file/path/within/container /host/path/target
```

