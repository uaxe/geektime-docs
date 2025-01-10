你好，我是盛延敏，这里是网络编程实战的第14讲，欢迎回来。

在前面的基础篇中，我们已经接触到了UDP数据报协议相关的知识，在我们的脑海里，已经深深印上了“ **UDP 等于无连接协议**”的特性。那么看到这一讲的题目，你是不是觉得有点困惑？没关系，和我一起进入“已连接”的UDP的世界，回头再看这个标题，相信你就会恍然大悟。

## 从一个例子开始

我们先从一个客户端例子开始，在这个例子中，客户端在UDP套接字上调用connect函数，之后将标准输入的字符串发送到服务器端，并从服务器端接收处理后的报文。当然，向服务器端发送和接收报文是通过调用函数sendto和recvfrom来完成的。

```
#include "lib/common.h"
# define    MAXLINE     4096

int main(int argc, char **argv) {
    if (argc != 2) {
        error(1, 0, "usage: udpclient1 <IPaddress>");
    }

    int socket_fd;
    socket_fd = socket(AF_INET, SOCK_DGRAM, 0);

    struct sockaddr_in server_addr;
    bzero(&server_addr, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERV_PORT);
    inet_pton(AF_INET, argv[1], &server_addr.sin_addr);

    socklen_t server_len = sizeof(server_addr);

    if (connect(socket_fd, (struct sockaddr *) &server_addr, server_len)) {
        error(1, errno, "connect failed");
    }

    struct sockaddr *reply_addr;
    reply_addr = malloc(server_len);

    char send_line[MAXLINE], recv_line[MAXLINE + 1];
    socklen_t len;
    int n;

    while (fgets(send_line, MAXLINE, stdin) != NULL) {
        int i = strlen(send_line);
        if (send_line[i - 1] == '\n') {
            send_line[i - 1] = 0;
        }

        printf("now sending %s\n", send_line);
        size_t rt = sendto(socket_fd, send_line, strlen(send_line), 0, (struct sockaddr *) &server_addr, server_len);
        if (rt < 0) {
            error(1, errno, "sendto failed");
        }
        printf("send bytes: %zu \n", rt);

        len = 0;
        recv_line[0] = 0;
        n = recvfrom(socket_fd, recv_line, MAXLINE, 0, reply_addr, &len);
        if (n < 0)
            error(1, errno, "recvfrom failed");
        recv_line[n] = 0;
        fputs(recv_line, stdout);
        fputs("\n", stdout);
    }

    exit(0);
}

```

我对这个程序做一个简单的解释：

- 9-10行创建了一个UDP套接字；
- 12-16行创建了一个IPv4地址，绑定到指定端口和IP；
- **20-22行调用connect将UDP套接字和IPv4地址进行了“绑定”，这里connect函数的名称有点让人误解，其实可能更好的选择是叫做setpeername**；
- 31-55行是程序的主体，读取标准输入字符串后，调用sendto发送给对端；之后调用recvfrom等待对端的响应，并把对端响应信息打印到标准输出。

在没有开启服务端的情况下，我们运行一下这个程序：

```
$ ./udpconnectclient 127.0.0.1
g1
now sending g1
send bytes: 2
recvfrom failed: Connection refused (111)

```

看到这里你会不会觉得很奇怪？不是说好UDP是“无连接”的协议吗？不是说好UDP客户端只会阻塞在recvfrom这样的调用上吗？怎么这里冒出一个“Connection refused”的错误呢？

别着急，下面就跟着我的思路慢慢去解开这个谜团。

## UDP connect的作用

从前面的例子中，你会发现，我们可以对UDP套接字调用connect函数，但是和TCP connect调用引起TCP三次握手，建立TCP有效连接不同，UDP connect函数的调用，并不会引起和服务器目标端的网络交互，也就是说，并不会触发所谓的“握手”报文发送和应答。

那么对UDP套接字进行connect操作到底有什么意义呢？

其实上面的例子已经给出了答案，这主要是为了让应用程序能够接收“异步错误”的信息。

如果我们回想一下第6篇不调用connect操作的客户端程序，在服务器端不开启的情况下，客户端程序是不会报错的，程序只会阻塞在recvfrom上，等待返回（或者超时）。

在这里，我们通过对UDP套接字进行connect操作，将UDP套接字建立了“上下文”，该套接字和服务器端的地址和端口产生了联系，正是这种绑定关系给了操作系统内核必要的信息，能够将操作系统内核收到的信息和对应的套接字进行关联。

我们可以展开讨论一下。

事实上，当我们调用sendto或者send操作函数时，应用程序报文被发送，我们的应用程序返回，操作系统内核接管了该报文，之后操作系统开始尝试往对应的地址和端口发送，因为对应的地址和端口不可达，一个ICMP报文会返回给操作系统内核，该ICMP报文含有目的地址和端口等信息。

如果我们不进行connect操作，建立（UDP套接字——目的地址+端口）之间的映射关系，操作系统内核就没有办法把ICMP不可达的信息和UDP套接字进行关联，也就没有办法将ICMP信息通知给应用程序。

如果我们进行了connect操作，帮助操作系统内核从容建立了（UDP套接字——目的地址+端口）之间的映射关系，当收到一个ICMP不可达报文时，操作系统内核可以从映射表中找出是哪个UDP套接字拥有该目的地址和端口，别忘了套接字在操作系统内部是全局唯一的，当我们在该套接字上再次调用recvfrom或recv方法时，就可以收到操作系统内核返回的“Connection Refused”的信息。

## 收发函数

在对UDP进行connect之后，关于收发函数的使用，很多书籍是这样推荐的：

- 使用send或write函数来发送，如果使用sendto需要把相关的to地址信息置零；
- 使用recv或read函数来接收，如果使用recvfrom需要把对应的from地址信息置零。

其实不同的UNIX实现对此表现出来的行为不尽相同。

在我的Linux 4.4.0环境中，使用sendto和recvfrom，系统会自动忽略to和from信息。在我的macOS 10.13中，确实需要遵守这样的规定，使用sendto或recvfrom会得到一些奇怪的结果，切回send和recv后正常。

考虑到兼容性，我们也推荐这些常规做法。所以在接下来的程序中，我会使用这样的做法来实现。

## 服务器端connect的例子

一般来说，服务器端不会主动发起connect操作，因为一旦如此，服务器端就只能响应一个客户端了。不过，有时候也不排除这样的情形，一旦一个客户端和服务器端发送UDP报文之后，该服务器端就要服务于这个唯一的客户端。

一个类似的服务器端程序如下：

```
#include "lib/common.h"

static int count;

static void recvfrom_int(int signo) {
    printf("\nreceived %d datagrams\n", count);
    exit(0);
}

int main(int argc, char **argv) {
    int socket_fd;
    socket_fd = socket(AF_INET, SOCK_DGRAM, 0);

    struct sockaddr_in server_addr;
    bzero(&server_addr, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(SERV_PORT);

    bind(socket_fd, (struct sockaddr *) &server_addr, sizeof(server_addr));

    socklen_t client_len;
    char message[MAXLINE];
    message[0] = 0;
    count = 0;

    signal(SIGINT, recvfrom_int);

    struct sockaddr_in client_addr;
    client_len = sizeof(client_addr);

    int n = recvfrom(socket_fd, message, MAXLINE, 0, (struct sockaddr *) &client_addr, &client_len);
    if (n < 0) {
        error(1, errno, "recvfrom failed");
    }
    message[n] = 0;
    printf("received %d bytes: %s\n", n, message);

    if (connect(socket_fd, (struct sockaddr *) &client_addr, client_len)) {
        error(1, errno, "connect failed");
    }

    while (strncmp(message, "goodbye", 7) != 0) {
        char send_line[MAXLINE];
        sprintf(send_line, "Hi, %s", message);

        size_t rt = send(socket_fd, send_line, strlen(send_line), 0);
        if (rt < 0) {
            error(1, errno, "send failed ");
        }
        printf("send bytes: %zu \n", rt);

        size_t rc = recv(socket_fd, message, MAXLINE, 0);
        if (rc < 0) {
            error(1, errno, "recv failed");
        }

        count++;
    }

    exit(0);
}

```

我对这个程序做下解释：

- 11-12行创建UDP套接字；
- 14-18行创建IPv4地址，绑定到ANY和对应端口；
- 20行绑定UDP套接字和IPv4地址；
- 27行为该程序注册一个信号处理函数，以响应Ctrl+C信号量操作；
- 32-37行调用recvfrom等待客户端报文到达，并将客户端信息保持到client\_addr中；
- **39-41行调用connect操作，将UDP套接字和客户端client\_addr进行绑定**；
- 43-59行是程序的主体，对接收的信息进行重新处理，加上”Hi“前缀后发送给客户端，并持续不断地从客户端接收报文，该过程一直持续，直到客户端发送“goodbye”报文为止。

注意这里所有收发函数都使用了send和recv。

接下来我们实现一个connect的客户端程序：

```
#include "lib/common.h"
# define    MAXLINE     4096

int main(int argc, char **argv) {
    if (argc != 2) {
        error(1, 0, "usage: udpclient3 <IPaddress>");
    }

    int socket_fd;
    socket_fd = socket(AF_INET, SOCK_DGRAM, 0);

    struct sockaddr_in server_addr;
    bzero(&server_addr, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERV_PORT);
    inet_pton(AF_INET, argv[1], &server_addr.sin_addr);

    socklen_t server_len = sizeof(server_addr);

    if (connect(socket_fd, (struct sockaddr *) &server_addr, server_len)) {
        error(1, errno, "connect failed");
    }

    char send_line[MAXLINE], recv_line[MAXLINE + 1];
    int n;

    while (fgets(send_line, MAXLINE, stdin) != NULL) {
        int i = strlen(send_line);
        if (send_line[i - 1] == '\n') {
            send_line[i - 1] = 0;
        }

        printf("now sending %s\n", send_line);
        size_t rt = send(socket_fd, send_line, strlen(send_line), 0);
        if (rt < 0) {
            error(1, errno, "send failed ");
        }
        printf("send bytes: %zu \n", rt);

        recv_line[0] = 0;
        n = recv(socket_fd, recv_line, MAXLINE, 0);
        if (n < 0)
            error(1, errno, "recv failed");
        recv_line[n] = 0;
        fputs(recv_line, stdout);
        fputs("\n", stdout);
    }

    exit(0);
}

```

我对这个客户端程序做一下解读：

- 9-10行创建了一个UDP套接字；
- 12-16行创建了一个IPv4地址，绑定到指定端口和IP；
- **20-22行调用connect将UDP套接字和IPv4地址进行了“绑定”**；
- 27-46行是程序的主体，读取标准输入字符串后，调用send发送给对端；之后调用recv等待对端的响应，并把对端响应信息打印到标准输出。

注意这里所有收发函数也都使用了send和recv。

接下来，我们先启动服务器端程序，然后依次开启两个客户端，分别是客户端1、客户端2，并且让客户端1先发送UDP报文。

服务器端：

```
$ ./udpconnectserver
received 2 bytes: g1
send bytes: 6

```

客户端1：

```
 ./udpconnectclient2 127.0.0.1
g1
now sending g1
send bytes: 2
Hi, g1

```

客户端2：

```
./udpconnectclient2 127.0.0.1
g2
now sending g2
send bytes: 2
recv failed: Connection refused (111)

```

我们看到，客户端1先发送报文，服务端随之通过connect和客户端1进行了“绑定”，这样，客户端2从操作系统内核得到了ICMP的错误，该错误在recv函数中返回，显示了“Connection refused”的错误信息。

## 性能考虑

一般来说，客户端通过connect绑定服务端的地址和端口，对UDP而言，可以有一定程度的性能提升。

这是为什么呢？

因为如果不使用connect方式，每次发送报文都会需要这样的过程：

连接套接字→发送报文→断开套接字→连接套接字→发送报文→断开套接字 →………

而如果使用connect方式，就会变成下面这样：

连接套接字→发送报文→发送报文→……→最后断开套接字

我们知道，连接套接字是需要一定开销的，比如需要查找路由表信息。所以，UDP客户端程序通过connect可以获得一定的性能提升。

## 总结

在今天的内容里，我对UDP套接字调用connect方法进行了深入的分析。之所以对UDP使用connect，绑定本地地址和端口，是为了让我们的程序可以快速获取异步错误信息的通知，同时也可以获得一定性能上的提升。

## 思考题

在本讲的最后，按照惯例，给你留两个思考题：

1. 可以对一个UDP 套接字进行多次connect操作吗? 你不妨动手试试，看看结果。
2. 如果想使用多播或广播，我们应该怎么去使用connect呢？

欢迎你在评论区写下你的思考，也欢迎把这篇文章分享给你的朋友或者同事，一起交流一下。