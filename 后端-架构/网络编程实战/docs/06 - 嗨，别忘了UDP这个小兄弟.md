你好，我是盛延敏，这里是网络编程实战第6讲，欢迎回来。

前面几讲我们讲述了TCP方面的编程知识，这一讲我们来讲讲UDP方面的编程知识。

如果说TCP是网络协议的“大哥”，那么UDP可以说是“小兄弟”。这个小兄弟和大哥比，有什么差异呢？

首先，UDP是一种“数据报”协议，而TCP是一种面向连接的“数据流”协议。

TCP可以用日常生活中打电话的场景打比方，前面也多次用到了这样的例子。在这个例子中，拨打号码、接通电话、开始交流，分别对应了TCP的三次握手和报文传送。一旦双方的连接建立，那么双方对话时，一定知道彼此是谁。这个时候我们就说，这种对话是有上下文的。

同样的，我们也可以给UDP找一个类似的例子，这个例子就是邮寄明信片。在这个例子中，发信方在明信片中填上了接收方的地址和邮编，投递到邮局的邮筒之后，就可以不管了。发信方也可以给这个接收方再邮寄第二张、第三张，甚至是第四张明信片，但是这几张明信片之间是没有任何关系的，他们的到达顺序也是不保证的，有可能最后寄出的第四张明信片最先到达接收者的手中，因为没有序号，接收者也不知道这是第四张寄出的明信片；而且，即使接收方没有收到明信片，也没有办法重新邮寄一遍该明信片。

这两个简单的例子，道出了UDP和TCP之间最大的区别。

TCP是一个面向连接的协议，TCP在IP报文的基础上，增加了诸如重传、确认、有序传输、拥塞控制等能力，通信的双方是在一个确定的上下文中工作的。

而UDP则不同，UDP没有这样一个确定的上下文，它是一个不可靠的通信协议，没有重传和确认，没有有序控制，也没有拥塞控制。我们可以简单地理解为，在IP报文的基础上，UDP增加的能力有限。

UDP不保证报文的有效传递，不保证报文的有序，也就是说使用UDP的时候，我们需要做好丢包、重传、报文组装等工作。

既然如此，为什么我们还要使用UDP协议呢？

答案很简单，因为UDP比较简单，适合的场景还是比较多的，我们常见的DNS服务，SNMP服务都是基于UDP协议的，这些场景对时延、丢包都不是特别敏感。另外多人通信的场景，如聊天室、多人游戏等，也都会使用到UDP协议。

## UDP编程

UDP和TCP编程非常不同，下面这张图是UDP程序设计时的主要过程。

![](https://static001.geekbang.org/resource/image/84/30/8416f0055bedce10a3c7d0416cc1f430.png?wh=4034*2631)

我们看到服务器端创建UDP 套接字之后，绑定到本地端口，调用recvfrom函数等待客户端的报文发送；客户端创建套接字之后，调用sendto函数往目标地址和端口发送UDP报文，然后客户端和服务器端进入互相应答过程。

recvfrom和sendto是UDP用来接收和发送报文的两个主要函数：

```
#include <sys/socket.h>

ssize_t recvfrom(int sockfd, void *buff, size_t nbytes, int flags,
　　　　　　　　　　struct sockaddr *from, socklen_t *addrlen);

ssize_t sendto(int sockfd, const void *buff, size_t nbytes, int flags,
                const struct sockaddr *to, socklen_t addrlen);

```

我们先来看一下recvfrom函数。

sockfd、buff和nbytes是前三个参数。sockfd是本地创建的套接字描述符，buff指向本地的缓存，nbytes表示最大接收数据字节。

第四个参数flags是和I/O相关的参数，这里我们还用不到，设置为0。

后面两个参数from和addrlen，实际上是返回对端发送方的地址和端口等信息，这和TCP非常不一样，TCP是通过accept函数拿到的描述字信息来决定对端的信息。另外UDP报文每次接收都会获取对端的信息，也就是说报文和报文之间是没有上下文的。

函数的返回值告诉我们实际接收的字节数。

接下来看一下sendto函数。

sendto函数中的前三个参数为sockfd、buff和nbytes。sockfd是本地创建的套接字描述符，buff指向发送的缓存，nbytes表示发送字节数。第四个参数flags依旧设置为0。

后面两个参数to和addrlen，表示发送的对端地址和端口等信息。

函数的返回值告诉我们实际发送的字节数。

我们知道， TCP的发送和接收每次都是在一个上下文中，类似这样的过程：

A连接上: 接收→发送→接收→发送→…

B连接上: 接收→发送→接收→发送→ …

而UDP的每次接收和发送都是一个独立的上下文，类似这样：

接收A→发送A→接收B→发送B →接收C→发送C→ …

## UDP服务端例子

我们先来看一个UDP服务器端的例子：

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
    count = 0;

    signal(SIGINT, recvfrom_int);

    struct sockaddr_in client_addr;
    client_len = sizeof(client_addr);
    for (;;) {
        int n = recvfrom(socket_fd, message, MAXLINE, 0, (struct sockaddr *) &client_addr, &client_len);
        message[n] = 0;
        printf("received %d bytes: %s\n", n, message);

        char send_line[MAXLINE];
        sprintf(send_line, "Hi, %s", message);

        sendto(socket_fd, send_line, strlen(send_line), 0, (struct sockaddr *) &client_addr, client_len);

        count++;
    }

}

```

程序的12～13行，首先创建一个套接字，注意这里的套接字类型是“SOCK\_DGRAM”，表示的是UDP数据报。

15～21行和TCP服务器端类似，绑定数据报套接字到本地的一个端口上。

27行为该服务器创建了一个信号处理函数，以便在响应“Ctrl+C”退出时，打印出收到的报文总数。

31～42行是该服务器端的主体，通过调用recvfrom函数获取客户端发送的报文，之后我们对收到的报文进行重新改造，加上“Hi”的前缀，再通过sendto函数发送给客户端对端。

## UDP客户端例子

接下来我们再来构建一个对应的UDP客户端。在这个例子中，从标准输入中读取输入的字符串后，发送给服务端，并且把服务端经过处理的报文打印到标准输出上。

```
#include "lib/common.h"

# define    MAXLINE     4096

int main(int argc, char **argv) {
    if (argc != 2) {
        error(1, 0, "usage: udpclient <IPaddress>");
    }

    int socket_fd;
    socket_fd = socket(AF_INET, SOCK_DGRAM, 0);

    struct sockaddr_in server_addr;
    bzero(&server_addr, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERV_PORT);
    inet_pton(AF_INET, argv[1], &server_addr.sin_addr);

    socklen_t server_len = sizeof(server_addr);

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
            error(1, errno, "send failed ");
        }
        printf("send bytes: %zu \n", rt);

        len = 0;
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

10～11行创建一个类型为“SOCK\_DGRAM”的套接字。

13～17行，初始化目标服务器的地址和端口。

28～51行为程序主体，从标准输入中读取的字符进行处理后，调用sendto函数发送给目标服务器端，然后再次调用recvfrom函数接收目标服务器发送过来的新报文，并将其打印到标准输出上。

为了让你更好地理解UDP和TCP之间的差别，我们模拟一下UDP的三种运行场景，你不妨思考一下这三种场景的结果和TCP的到底有什么不同？

## 场景一：只运行客户端

如果我们只运行客户端，程序会一直阻塞在recvfrom上。

```
$ ./udpclient 127.0.0.1
1
now sending g1
send bytes: 2
<阻塞在这里>

```

还记得TCP程序吗？如果不开启服务端，TCP客户端的connect函数会直接返回“Connection refused”报错信息。而在UDP程序里，则会一直阻塞在这里。

## 场景二：先开启服务端，再开启客户端

在这个场景里，我们先开启服务端在端口侦听，然后再开启客户端：

```
$./udpserver
received 2 bytes: g1
received 2 bytes: g2

```

```
$./udpclient 127.0.0.1
g1
now sending g1
send bytes: 2
Hi, g1
g2
now sending g2
send bytes: 2
Hi, g2

```

我们在客户端一次输入g1、g2，服务器端在屏幕上打印出收到的字符，并且可以看到，我们的客户端也收到了服务端的回应：“Hi,g1”和“Hi,g2”。

## 场景三: 开启服务端，再一次开启两个客户端

这个实验中，在服务端开启之后，依次开启两个客户端，并发送报文。

服务端：

```
$./udpserver
received 2 bytes: g1
received 2 bytes: g2
received 2 bytes: g3
received 2 bytes: g4

```

第一个客户端：

```
$./udpclient 127.0.0.1
now sending g1
send bytes: 2
Hi, g1
g3
now sending g3
send bytes: 2
Hi, g3

```

第二个客户端：

```
$./udpclient 127.0.0.1
now sending g2
send bytes: 2
Hi, g2
g4
now sending g4
send bytes: 2
Hi, g4

```

我们看到，两个客户端发送的报文，依次都被服务端收到，并且客户端也可以收到服务端处理之后的报文。

如果我们此时把服务器端进程杀死，就可以看到信号函数在进程退出之前，打印出服务器端接收到的报文个数。

```
$ ./udpserver
received 2 bytes: g1
received 2 bytes: g2
received 2 bytes: g3
received 2 bytes: g4
^C
received 4 datagrams

```

之后，我们再重启服务器端进程，并使用客户端1和客户端2继续发送新的报文，我们可以看到和TCP非常不同的结果。

以下就是服务器端的输出，服务器端重启后可以继续收到客户端的报文，这在TCP里是不可以的，TCP断联之后必须重新连接才可以发送报文信息。但是UDP报文的“无连接”的特点，可以在UDP服务器重启之后，继续进行报文的发送，这就是UDP报文“无上下文”的最好说明。

```
$ ./udpserver
received 2 bytes: g1
received 2 bytes: g2
received 2 bytes: g3
received 2 bytes: g4
^C
received 4 datagrams
$ ./udpserver
received 2 bytes: g5
received 2 bytes: g6

```

第一个客户端：

```
$./udpclient 127.0.0.1
now sending g1
send bytes: 2
Hi, g1
g3
now sending g3
send bytes: 2
Hi, g3
g5
now sending g5
send bytes: 2
Hi, g5

```

第二个客户端：

```
$./udpclient 127.0.0.1
now sending g2
send bytes: 2
Hi, g2
g4
now sending g4
send bytes: 2
Hi, g4
g6
now sending g6
send bytes: 2
Hi, g6

```

## 总结

在这一讲里，我介绍了UDP程序的例子，我们需要重点关注以下两点：

- UDP是无连接的数据报程序，和TCP不同，不需要三次握手建立一条连接。
- UDP程序通过recvfrom和sendto函数直接收发数据报报文。

## 思考题

最后给你留两个思考题吧。在第一个场景中，recvfrom一直处于阻塞状态中，这是非常不合理的，你觉得这种情形应该怎么处理呢？另外，既然UDP是请求-应答模式的，那么请求中的UDP报文最大可以是多大呢？

欢迎你在评论区写下你的思考，我会和你一起讨论。也欢迎把这篇文章分享给你的朋友或者同事，一起讨论一下UDP这个协议。