你好，我是程远。今天我们聊一聊容器文件Quota。

上一讲，我们学习了容器文件系统OverlayFS，这个OverlayFS有两层，分别是lowerdir和upperdir。lowerdir里是容器镜像中的文件，对于容器来说是只读的；upperdir存放的是容器对文件系统里的所有改动，它是可读写的。

从宿主机的角度看，upperdir就是一个目录，如果容器不断往容器文件系统中写入数据，实际上就是往宿主机的磁盘上写数据，这些数据也就存在于宿主机的磁盘目录中。

当然对于容器来说，如果有大量的写操作是不建议写入容器文件系统的，一般是需要给容器挂载一个volume，用来满足大量的文件读写。

但是不能避免的是，用户在容器中运行的程序有错误，或者进行了错误的配置。

比如说，我们把log写在了容器文件系统上，并且没有做log rotation，那么时间一久，就会导致宿主机上的磁盘被写满。这样影响的就不止是容器本身了，而是整个宿主机了。

那对于这样的问题，我们该怎么解决呢？

## 问题再现

我们可以自己先启动一个容器，一起试试不断地往容器文件系统中写入数据，看看是一个什么样的情况。

用Docker启动一个容器后，我们看到容器的根目录(/)也就是容器文件系统OverlayFS，它的大小是160G，已经使用了100G。其实这个大小也是宿主机上的磁盘空间和使用情况。

![](https://static001.geekbang.org/resource/image/d3/3e/d32c83e404a81b301fbf8bdfd7a9c23e.png?wh=1264*586)

这时候，我们可以回到宿主机上验证一下，就会发现宿主机的根目录(/)的大小也是160G，同样是使用了100G。

![](https://static001.geekbang.org/resource/image/b5/0b/b54deb08e46ff1155303581e9d1c8f0b.png?wh=1242*366)

好，那现在我们再往容器的根目录里写入10GB的数据。

这里我们可以看到容器的根目录使用的大小增加了，从刚才的100G变成现在的110G。而多写入的10G大小的数据，对应的是test.log这个文件。

![](https://static001.geekbang.org/resource/image/c0/46/c04dcff3aa4773302495113dd2a8d546.png?wh=1704*472)

接下来，我们再回到宿主机上，可以看到宿主机上的根目录(/)里使用的大小也是110G了。

![](https://static001.geekbang.org/resource/image/15/9d/155d30bc20b72c0678d1948f25cbe29d.png?wh=1220*366)

我们还是继续看宿主机，看看OverlayFS里upperdir目录中有什么文件？

这里我们仍然可以通过/proc/mounts这个路径，找到容器OverlayFS对应的lowerdir和upperdir。因为写入的数据都在upperdir里，我们就只要看upperdir对应的那个目录就行了。果然，里面存放着容器写入的文件test.log，它的大小是10GB。

![](https://static001.geekbang.org/resource/image/4d/7d/4d32334dc0f1ba69881c686037f6577d.png?wh=1920*461)

通过这个例子，我们已经验证了在容器中对于OverlayFS中写入数据， **其实就是往宿主机的一个目录（upperdir）里写数据。** 我们现在已经写了10GB的数据，如果继续在容器中写入数据，结果估计你也知道了，就是会写满宿主机的磁盘。

那遇到这种情况，我们该怎么办呢？

## 知识详解

容器写自己的OverlayFS根目录，结果把宿主机的磁盘写满了。发生这个问题，我们首先就会想到需要对容器做限制，限制它写入自己OverlayFS的数据量，比如只允许一个容器写100MB的数据。

不过我们实际查看OverlayFS文件系统的特性，就会发现没有直接限制文件写入量的特性。别担心，在没有现成工具的情况下，我们只要搞懂了原理，就能想出解决办法。

所以我们再来分析一下OverlayFS，它是通过lowerdir和upperdir两层目录联合挂载来实现的，lowerdir是只读的，数据只会写在upperdir中。

那我们是不是可以通过限制upperdir目录容量的方式，来限制一个容器OverlayFS根目录的写入数据量呢？

沿着这个思路继续往下想，因为upperdir在宿主机上也是一个普通的目录，这样就要看 **宿主机上的文件系统是否可以支持对一个目录限制容量了。**

对于Linux上最常用的两个文件系统XFS和ext4，它们有一个特性Quota，那我们就以XFS文件系统为例，学习一下这个Quota概念，然后看看这个特性能不能限制一个目录的使用量。

### XFS Quota

在Linux系统里的XFS文件系统缺省都有Quota的特性，这个特性可以为Linux系统里的一个用户（user），一个用户组（group）或者一个项目（project）来限制它们使用文件系统的额度（quota），也就是限制它们可以写入文件系统的文件总量。

因为我们的目标是要限制一个目录中总体的写入文件数据量，那么显然给用户和用户组限制文件系统的写入数据量的模式，并不适合我们的这个需求。

因为同一个用户或者用户组可以操作多个目录，多个用户或者用户组也可以操作同一个目录，这样对一个用户或者用户组的限制，就很难用来限制一个目录。

那排除了限制用户或用户组的模式，我们再来看看Project模式。Project模式是怎么工作的呢？

我举一个例子你会更好理解，对Linux熟悉的同学可以一边操作，一边体会一下它的工作方式。不熟悉的同学也没关系，可以重点关注我后面的讲解思路。

首先我们要使用XFS Quota特性，必须在文件系统挂载的时候加上对应的Quota选项，比如我们目前需要配置Project Quota，那么这个挂载参数就是"pquota"。

对于根目录来说， **这个参数必须作为一个内核启动的参数"rootflags=pquota"，这样设置就可以保证根目录在启动挂载的时候，带上XFS Quota的特性并且支持Project模式。**

我们可以从/proc/mounts信息里，看看根目录是不是带"prjquota"字段。如果里面有这个字段，就可以确保文件系统已经带上了支持project模式的XFS quota特性。

![](https://static001.geekbang.org/resource/image/72/3d/72d653f67717fe047c98fce37156da3d.png?wh=1230*112)

下一步，我们还需要给一个指定的目录打上一个Project ID。这个步骤我们可以使用XFS文件系统自带的工具 [xfs\_quota](https://linux.die.net/man/8/xfs_quota) 来完成，然后执行下面的这个命令就可以了。

执行命令之前，我先对下面的命令和输出做两点解释，让你理解这个命令的含义。

第一点，新建的目录/tmp/xfs\_prjquota，我们想对它做Quota限制。所以在这里要对它打上一个Project ID。

第二点，通过xfs\_quota这条命令，我们给/tmp/xfs\_prjquota打上Project ID值101，这个101是我随便选的一个数字，就是个ID标识，你先有个印象。在后面针对Project进行Quota限制的时候，我们还会用到这个ID。

```shell
# mkdir -p  /tmp/xfs_prjquota
# xfs_quota -x -c 'project -s -p /tmp/xfs_prjquota 101' /
Setting up project 101 (path /tmp/xfs_prjquota)...
Processed 1 (/etc/projects and cmdline) paths for project 101 with recursion depth infinite (-1).

```

最后，我们还是使用xfs\_quota命令，对101（我们刚才建立的这个Project ID）做Quota限制。

你可以执行下面这条命令，里面的"-p bhard=10m 101"就代表限制101这个project ID，限制它的数据块写入量不能超过10MB。

```
# xfs_quota -x -c 'limit -p bhard=10m 101' /

```

做好限制之后，我们可以尝试往/tmp/xfs\_prjquota写数据，看看是否可以超过10MB。比如说，我们尝试写入20MB的数据到/tmp/xfs\_prjquota里。

我们可以看到，执行dd写入命令，就会有个出错返回信息"No space left on device"。这表示已经不能再往这个目录下写入数据了，而最后写入数据的文件test.file大小也停留在了10MB。

```shell
# dd if=/dev/zero of=/tmp/xfs_prjquota/test.file bs=1024 count=20000
dd: error writing '/tmp/xfs_prjquota/test.file': No space left on device
10241+0 records in
10240+0 records out
10485760 bytes (10 MB, 10 MiB) copied, 0.0357122 s, 294 MB/s

# ls -l /tmp/xfs_prjquota/test.file
-rw-r--r-- 1 root root 10485760 Oct 31 10:00 /tmp/xfs_prjquota/test.file

```

好了，做到这里，我们发现使用XFS Quota的Project模式，确实可以限制一个目录里的写入数据量，它实现的方式其实也不难，就是下面这两步。

第一步，给目标目录打上一个Project ID，这个ID最终是写到目录对应的inode上。

这里我解释一下，inode是文件系统中用来描述一个文件或者一个目录的元数据，里面包含文件大小，数据块的位置，文件所属用户/组，文件读写属性以及其他一些属性。

那么一旦目录打上这个ID之后，在这个目录下的新建的文件和目录也都会继承这个ID。

第二步，在XFS文件系统中，我们需要给这个project ID设置一个写入数据块的限制。

有了ID和限制值之后，文件系统就可以统计所有带这个ID文件的数据块大小总和，并且与限制值进行比较。一旦所有文件大小的总和达到限制值，文件系统就不再允许更多的数据写入了。

用一句话概括，XFS Quota就是通过前面这两步限制了一个目录里写入的数据量。

## 解决问题

我们理解了XFS Quota对目录限流的机制之后，再回到我们最开始的问题，如何确保容器不会写满宿主机上的磁盘。

你应该已经想到了，方法就是 **对OverlayFS的upperdir目录做XFS Quota的限流**，没错，就是这个解决办法！

其实Docker也已经实现了限流功能，也就是用XFS Quota来限制容器的OverlayFS大小。

我们在用 `docker run` 启动容器的时候，加上一个参数 `--storage-opt size= <SIZE>` ，就能限制住容器OverlayFS文件系统可写入的最大数据量了。

我们可以一起试一下，这里我们限制的size是10MB。

进入容器之后，先运行 `df -h` 命令，这时候你可以看到根目录(/)overlayfs文件系统的大小就10MB，而不是我们之前看到的160GB的大小了。这样容器在它的根目录下，最多只能写10MB数据，就不会把宿主机的磁盘给写满了。

![](https://static001.geekbang.org/resource/image/a7/8a/a7906f56d9d107f0a290e610b8cd6f8a.png?wh=1194*210)

完成了上面这个小试验之后，我们可以再看一下Docker的代码，看看它的实现是不是和我们想的一样。

Docker里 [SetQuota()](https://github.com/moby/moby/blob/19.03/daemon/graphdriver/quota/projectquota.go#L155) 函数就是用来实现XFS Quota 限制的，我们可以看到它里面最重要的两步，分别是 `setProjectID` 和 `setProjectQuota` 。

其实，这两步做的就是我们在基本概念中提到的那两步：

第一步，给目标目录打上一个Project ID；第二步，为这个Project ID在XFS文件系统中，设置一个写入数据块的限制。

```shell
// SetQuota - assign a unique project id to directory and set the quota limits
// for that project id

func (q *Control) SetQuota(targetPath string, quota Quota) error {
        q.RLock()
        projectID, ok := q.quotas[targetPath]
        q.RUnlock()

        if !ok {
                q.Lock()
                projectID = q.nextProjectID

                //
                // assign project id to new container directory
                //

                err := setProjectID(targetPath, projectID)
                if err != nil {
                        q.Unlock()
                        return err
                }

                q.quotas[targetPath] = projectID
                q.nextProjectID++
                q.Unlock()
        }



        //
        // set the quota limit for the container's project id
        //

        logrus.Debugf("SetQuota(%s, %d): projectID=%d", targetPath, quota.Size, projectID)
        return setProjectQuota(q.backingFsBlockDev, projectID, quota)
}

```

那 `setProjectID` 和 `setProjectQuota` 是如何实现的呢？

你可以进入到这两个函数里看一下， **它们分别调用了ioctl()和quotactl()这两个系统调用来修改内核中XFS的数据结构，从而完成project ID的设置和Quota值的设置。** 具体的细节，我不在这里展开了，如果你有兴趣，可以继续去查看内核中对应的代码。

好了，Docker里XFS Quota操作的步骤完全和我们先前设想的一样，那么还有最后一个问题要解决，XFS Quota限制的目录是哪一个？

这个我们可以根据/proc/mounts中容器的OverlayFS Mount信息，再结合Docker的 [代码](https://github.com/moby/moby/blob/19.03/daemon/graphdriver/overlay2/overlay.go#L335)，就可以知道限制的目录是"/var/lib/docker/overlay2/<docker\_id>"。那这个目录下有什么呢？果然upperdir目录中有对应的"diff"目录，就在里面！

![](https://static001.geekbang.org/resource/image/4d/9f/4d4d995f052c9a8e3ff3e413c0e1199f.png?wh=1920*646)

讲到这里，我想你已经清楚了对于使用OverlayFS的容器，我们应该如何去防止它把宿主机的磁盘给写满了吧？ **方法就是对OverlayFS的upperdir目录做XFS Quota的限流。**

## 重点总结

我们这一讲的问题是，容器写了大量数据到OverlayFS文件系统的根目录，在这个情况下，就会把宿主机的磁盘写满。

由于OverlayFS自己没有专门的特性，可以限制文件数据写入量。这时我们通过实际试验找到了解决思路：依靠底层文件系统的Quota特性来限制OverlayFS的upperdir目录的大小，这样就能实现限制容器写磁盘的目的。

底层文件系统XFS Quota的Project模式，能够限制一个目录的文件写入量，这个功能具体是通过这两个步骤实现：

第一步，给目标目录打上一个Project ID。

第二步，给这个Project ID在XFS文件系统中设置一个写入数据块的限制。

Docker正是使用了这个方法，也就是 **用XFS Quota来限制OverlayFS的upperdir目录**，通过这个方式控制容器OverlayFS的根目录大小。

当我们理解了这个方法后，对于不是用Docker启动的容器，比如直接由containerd启动起来的容器，也可以自己实现XFS Quota限制upperdir目录。这样就能有效控制容器对OverlayFS的写数据操作，避免宿主机的磁盘被写满。

## 思考题

在正文知识详解的部分，我们使用"xfs\_quota"给目录打了project ID并且限制了文件写入的数据量。那在做完这样的限制之后，我们是否能用xfs\_quota命令，查询到被限制目录的project ID和限制的数据量呢？

欢迎你在留言区分享你的思考或疑问。如果这篇文章让你有所收获，也欢迎转发给你的同事、朋友，一起交流和学习。