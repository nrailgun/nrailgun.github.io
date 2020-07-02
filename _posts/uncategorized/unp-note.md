## IP v4 回声

1. tcp write 仅仅保证传递到 buffer，尽力完成，不保证 delivery。

2. read / write 要注意可能返回 EINTR。

```c++
// server
int main(int argc, char *argv[]) {
        constexpr int MAXLINE = 1024;

        int endp = socket(AF_INET, SOCK_STREAM, 0);
        if (endp < 0) {
                perror("socket");
                return EXIT_FAILURE;
        }
        sockaddr_in saddr;
        bzero(&saddr, sizeof(saddr));
        saddr.sin_family = AF_INET;
        saddr.sin_addr.s_addr = htonl(INADDR_ANY);
        saddr.sin_port = htons(8080);
        if (bind(endp, (sockaddr *) &saddr, sizeof(saddr)) < 0) {
                perror("bind");
                return EXIT_FAILURE;
        }
        if (listen(endp, 10) < 0) {
                perror("listen");
                return EXIT_FAILURE;
        }

        for (int i = 0; i < 1; i++) {
                sockaddr_in caddr;
                socklen_t cl = sizeof(caddr);
                int conn = accept(endp, (sockaddr *) &caddr, &cl);
                if (conn < 0) {
                        perror("accept");
                        return EXIT_FAILURE;
                }

                char buf[MAXLINE + 1];
                ssize_t il, ol;
                while ((il = read(conn, buf, MAXLINE)) > 0) {
                        ssize_t nw = 0;
                        while (nw < il) {
                                ssize_t n = write(conn, buf + nw, il - nw);
                                if (n < 0) {
                                        perror("write");
                                        break;
                                }
                                nw += n;
                        }
                        buf[il] = '\0';
                }
                close(conn);
        }
        close(endp);
        return EXIT_SUCCESS;
}
```

```c++
// client
int main(int argc, char *argv[]) {
        constexpr int MAXLINE = 1024;

        int sk = socket(AF_INET, SOCK_STREAM, 0);
        if (sk < 0) {
                perror("socket");
                return EXIT_FAILURE;
        }
        sockaddr_in saddr;
        bzero(&saddr, sizeof(saddr));
        saddr.sin_family = AF_INET;
        if (inet_pton(AF_INET, argv[1], &saddr.sin_addr) <= 0) {
                perror("inet_pton");
                return EXIT_FAILURE;
        }
        saddr.sin_port = htons(8080);
        if (connect(sk, (sockaddr *) &saddr, sizeof(saddr)) < 0) {
                perror("connect");
                return EXIT_FAILURE;
        }

        for (int i = 0; i < 10; i++) {
                char buf[MAXLINE];
                for (int i = 0; i < sizeof(buf); i++) {
                        buf[i] = rand() % 10 + '0';
                }

                auto t1 = chrono::steady_clock::now();
                ssize_t nw = 0;
                while (nw < MAXLINE) {
                        ssize_t n = write(sk, buf + nw, MAXLINE - nw);
                        if (n < 0) {
                                perror("write");
                                return EXIT_FAILURE;
                        }
                        nw += n;
                }

                ssize_t nr = 0;
                while (nr < MAXLINE) {
                        ssize_t n = read(sk, buf + nr, MAXLINE - nr);
                        if (n < 0) {
                                perror("read");
                                return EXIT_FAILURE;
                        }
                        nr += n;
                }
                auto t2 = chrono::steady_clock::now();
                cout << "round-trip time: " << chrono::duration_cast<chrono::microseconds>(t2 - t1).count() << endl;
        }

        close(sk);
        return EXIT_SUCCESS;
}
```

## Select

select 缺点：

1. 只支持 1024 个 fd，
2. 必须 for loop test fdset，
3. 内核实现一般是轮循，效率相对低。

```c++

```

## Epoll

对比 select：

1. 支持更多 fd，
2. 返回值就是有 io 事件的 fd，直接可用，
3. 实现是内核操作相关设备时调用 callback，效率更高，而且 events 数组被内核特殊映射，copy 效率也高。

缺点是 select 全平台，epoll 只有 linux 有。

epoll 支持 level & edge 两种触发，level 为默认，有数据就反复触发（过了水平线），edge 为仅触发一次。

```c++
void setnonblocking(int sock) {
        int opts;
        opts=fcntl(sock,F_GETFL);
        if(opts<0) {
                perror("fcntl(sock,GETFL)");
                exit(1);
        }
        opts = opts|O_NONBLOCK;
        if(fcntl(sock,F_SETFL,opts)<0) {
                perror("fcntl(sock,SETFL,opts)");
                exit(1);
        }  
}

int main(int argc, char *argv[]) {
#define MAX_EVENTS 10
        struct epoll_event ev, events[MAX_EVENTS];
        int listen_sock, conn_sock, nfds, epollfd;

        // 创建epoll实例
        epollfd = epoll_create1(0);
        if (epollfd == -1) {
                perror("epoll_create1");
                exit(EXIT_FAILURE);
        }

        // 将监听的端口的socket对应的文件描述符添加到epoll事件列表中
        ev.events = EPOLLIN;
        ev.data.fd = listen_sock;
        if (epoll_ctl(epollfd, EPOLL_CTL_ADD, listen_sock, &ev) == -1) {
                perror("epoll_ctl: listen_sock");
                exit(EXIT_FAILURE);
        }

        for (;;) {
                // epoll_wait 阻塞线程，等待事件发生
                nfds = epoll_wait(epollfd, events, MAX_EVENTS, -1);
                if (nfds == -1) {
                        perror("epoll_wait");
                        exit(EXIT_FAILURE);
                }

                for (int n = 0; n < nfds; ++n) {
                        if (events[n].data.fd == listen_sock) {
                                // 新建的连接
                                struct sockaddr_in addr;
                                socklen_t addrlen;
                                conn_sock = accept(listen_sock, (struct sockaddr *) &addr, &addrlen);
                                // accept 返回新建连接的文件描述符
                                if (conn_sock == -1) {
                                        perror("accept");
                                        exit(EXIT_FAILURE);
                                }

                                // 将该文件描述符置为非阻塞状态
                                setnonblocking(conn_sock);

                                ev.events = EPOLLIN | EPOLLET;
                                ev.data.fd = conn_sock;
                                // 将该文件描述符添加到epoll事件监听的列表中，使用ET模式
                                if (epoll_ctl(epollfd, EPOLL_CTL_ADD, conn_sock,
                                                &ev) == -1)
                                        perror("epoll_ctl: conn_sock");
                                exit(EXIT_FAILURE);
                        } else {
                                // 使用已监听的文件描述符中的数据
                                // do_use_fd(events[n].data.fd);
                        }
                }
        }
        return EXIT_SUCCESS;
}
```

## Socket Options