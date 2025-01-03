你好，我是LMOS。

前面我们已经完成了Cosmos的驱动设备的建立，还写好了一个真实的设备驱动。

今天，我们就来看看Linux是如何管理设备的。我们将从Linux如何组织设备开始，然后研究设备驱动相关的数据结构，最后我们还是要一起写一个Linux设备驱动实例，这样才能真正理解它。

## 感受一下Linux下的设备信息

Linux的设计哲学就是一切皆文件，各种设备在Linux系统下自然也是一个个文件。不过这个文件并不对应磁盘上的数据文件，而是对应着存在内存当中的设备文件。实际上，我们对设备文件进行操作，就等同于操作具体的设备。

既然我们了解万事万物，都是从最直观的感受开始的，想要理解Linux对设备的管理，自然也是同样的道理。那么Linux设备文件在哪个目录下呢？其实现在我们在/sys/bus目录下，就可以查看所有的设备了。

Linux用BUS（总线）组织设备和驱动，我们在/sys/bus目录下输入tree命令，就可以看到所有总线下的所有设备了，如下图所示。

![](https://static001.geekbang.org/resource/image/56/28/567588d1ca461ed56c4cd3447d9dff28.jpg?wh=990x1047)

上图中，显示了部分Linux设备文件，有些设备文件是链接到其它目录下文件，这不是重点，重点是你要在心中有这个目录层次结构，即 **总线目录下有设备目录，设备目录下是设备文件**。

## 数据结构

我们接着刚才的图往下说，我们能感觉到Linux的驱动模型至少有三个核心数据结构，分别是总线、设备和驱动，但是要像上图那样有层次化地组织它们，只有总线、设备、驱动这三个数据结构是不够的，还得有两个数据结构来组织它们，那就是kobject和kset，下面我们就去研究它们。

### kobject与kset

kobject和kset是构成/sys目录下的目录节点和文件节点的核心，也是层次化组织总线、设备、驱动的核心数据结构，kobject、kset数据结构都能表示一个目录或者文件节点。下面我们先来研究一下kobject数据结构，代码如下所示。

```
struct kobject {
    const char      *name;           //名称，反映在sysfs中
    struct list_head    entry;       //挂入kset结构的链表
    struct kobject      *parent;     //指向父结构
    struct kset     *kset;           //指向所属的kset
    struct kobj_type    *ktype;
    struct kernfs_node  *sd;         //指向sysfs文件系统目录项
    struct kref     kref;            //引用计数器结构
    unsigned int state_initialized:1;//初始化状态
    unsigned int state_in_sysfs:1;   //是否在sysfs中
    unsigned int state_add_uevent_sent:1;
    unsigned int state_remove_uevent_sent:1;
    unsigned int uevent_suppress:1;
};

```

每一个 kobject，都对应着 /sys目录下（其实是sysfs文件系统挂载在/sys目录下） 的一个目录或者文件，目录或者文件的名字就是kobject结构中的name。

我们从kobject结构中可以看出，它挂载在kset下，并且指向了kset，那kset是什么呢？我们来分析分析，它是kobject结构的容器吗？

其实是也不是，因为kset结构中本身又包含一个kobject结构，所以它既是kobject的容器，同时本身还是一个kobject。kset结构代码如下所示。

```
struct kset {
    struct list_head list; //挂载kobject结构的链表
    spinlock_t list_lock; //自旋锁
    struct kobject kobj;//自身包含一个kobject结构
    const struct kset_uevent_ops *uevent_ops;//暂时不关注
} __randomize_layout;

```

看到这里你应该知道了，kset不仅仅自己是个kobject，还能挂载多个kobject，这说明kset是kobject的集合容器。在Linux内核中，至少有两个顶层kset，代码如下所示。

```
struct kset *devices_kset;//管理所有设备
static struct kset *bus_kset;//管理所有总线
static struct kset *system_kset;
int __init devices_init(void)
{
    devices_kset = kset_create_and_add("devices", &device_uevent_ops, NULL);//建立设备kset
    return 0;
}
int __init buses_init(void)
{
    bus_kset = kset_create_and_add("bus", &bus_uevent_ops, NULL);//建立总线kset
    if (!bus_kset)
        return -ENOMEM;
    system_kset = kset_create_and_add("system", NULL, &devices_kset->kobj);//在设备kset之下建立system的kset
    if (!system_kset)
        return -ENOMEM;
    return 0;
}

```

我知道，你可能很难想象许多个kset和kobject在逻辑上形成的层次结构，所以我为你画了一幅图，你可以结合这张示意图理解这个结构。

![](https://static001.geekbang.org/resource/image/bc/da/bcd9216d04b1f2ec6yy67ddf18052fda.jpg?wh=5039x4605)

上图中展示了一个类似文件目录的结构，这正是kset与kobject设计的目标之一。kset与kobject结构只是基础数据结构，但是仅仅只有它的话，也就只能实现这个层次结构，其它的什么也不能干，根据我们以往的经验可以猜出，kset与kobject结构肯定是嵌入到更高级的数据结构之中使用，下面我们继续探索。

### 总线

kset、kobject结构只是开胃菜，这个基础了解了，我们还要回到研究Linux设备与驱动的正题上。我们之前说过了，Linux用总线组织设备和驱动，由此可见总线是Linux设备的基础，它可以表示CPU与设备的连接，那么总线的数据结构是什么样呢？我们一起来看看。

Linux把总线抽象成bus\_type结构，代码如下所示。

```
struct bus_type {
    const char      *name;//总线名称
    const char      *dev_name;//用于列举设备，如（"foo%u", dev->id）
    struct device       *dev_root;//父设备
    const struct attribute_group **bus_groups;//总线的默认属性
    const struct attribute_group **dev_groups;//总线上设备的默认属性
    const struct attribute_group **drv_groups;//总线上驱动的默认属性
    //每当有新的设备或驱动程序被添加到这个总线上时调用
    int (*match)(struct device *dev, struct device_driver *drv);
    //当一个设备被添加、移除或其他一些事情时被调用产生uevent来添加环境变量。
    int (*uevent)(struct device *dev, struct kobj_uevent_env *env);
    //当一个新的设备或驱动程序添加到这个总线时被调用，并回调特定驱动程序探查函数，以初始化匹配的设备
    int (*probe)(struct device *dev);
    //将设备状态同步到软件状态时调用
    void (*sync_state)(struct device *dev);
    //当一个设备从这个总线上删除时被调用
    int (*remove)(struct device *dev);
    //当系统关闭时被调用
    void (*shutdown)(struct device *dev);
    //调用以使设备重新上线（在下线后）
    int (*online)(struct device *dev);
    //调用以使设备离线，以便热移除。可能会失败。
    int (*offline)(struct device *dev);
    //当这个总线上的设备想进入睡眠模式时调用
    int (*suspend)(struct device *dev, pm_message_t state);
    //调用以使该总线上的一个设备脱离睡眠模式
    int (*resume)(struct device *dev);
    //调用以找出该总线上的一个设备支持多少个虚拟设备功能
    int (*num_vf)(struct device *dev);
    //调用以在该总线上的设备配置DMA
    int (*dma_configure)(struct device *dev);
    //该总线的电源管理操作，回调特定的设备驱动的pm-ops
    const struct dev_pm_ops *pm;
    //此总线的IOMMU具体操作，用于将IOMMU驱动程序实现到总线上
    const struct iommu_ops *iommu_ops;
    //驱动核心的私有数据，只有驱动核心能够接触这个
    struct subsys_private *p;
    struct lock_class_key lock_key;
    //当探测或移除该总线上的一个设备时，设备驱动核心应该锁定该设备
    bool need_parent_lock;
};

```

可以看出，上面代码的bus\_type结构中，包括总线名字、总线属性，还有操作该总线下所有设备通用操作函数的指针，其各个函数的功能我在代码注释中已经写清楚了。

从这一点可以发现， **总线不仅仅是组织设备和驱动的容器，还是同类设备的共有功能的抽象层。** 下面我们来看看subsys\_private，它是总线的驱动核心的私有数据，其中有我们想知道的秘密，代码如下所示。

```
//通过kobject找到对应的subsys_private
#define to_subsys_private(obj) container_of(obj, struct subsys_private, subsys.kobj)
struct subsys_private {
    struct kset subsys;//定义这个子系统结构的kset
    struct kset *devices_kset;//该总线的"设备"目录，包含所有的设备
    struct list_head interfaces;//总线相关接口的列表
    struct mutex mutex;//保护设备，和接口列表
    struct kset *drivers_kset;//该总线的"驱动"目录，包含所有的驱动
    struct klist klist_devices;//挂载总线上所有设备的可迭代链表
    struct klist klist_drivers;//挂载总线上所有驱动的可迭代链表
    struct blocking_notifier_head bus_notifier;
    unsigned int drivers_autoprobe:1;
    struct bus_type *bus;   //指向所属总线
    struct kset glue_dirs;
    struct class *class;//指向这个结构所关联类结构的指针
};

```

看到这里，你应该明白kset的作用了，我们通过bus\_kset可以找到所有的kset，通过kset又能找到subsys\_private，再通过subsys\_private就可以找到总线了，也可以找到该总线上所有的设备与驱动。

### 设备

虽然Linux抽象出了总线结构，但是Linux还需要表示一个设备，下面我们来探索Linux是如何表示一个设备的。

其实，在Linux系统中设备也是一个数据结构，里面包含了一个设备的所有信息。代码如下所示。

```
struct device {
    struct kobject kobj;
    struct device       *parent;//指向父设备
    struct device_private   *p;//设备的私有数据
    const char      *init_name; //设备初始化名字
    const struct device_type *type;//设备类型
    struct bus_type *bus;  //指向设备所属总线
    struct device_driver *driver;//指向设备的驱动
    void        *platform_data;//设备平台数据
    void        *driver_data;//设备驱动的私有数据
    struct dev_links_info   links;//设备供应商链接
    struct dev_pm_info  power;//用于设备的电源管理
    struct dev_pm_domain    *pm_domain;//提供在系统暂停时执行调用
#ifdef CONFIG_GENERIC_MSI_IRQ
    struct list_head    msi_list;//主机的MSI描述符链表
#endif
    struct dev_archdata archdata;
    struct device_node  *of_node; //用访问设备树节点
    struct fwnode_handle    *fwnode; //设备固件节点
    dev_t           devt;   //用于创建sysfs "dev"
    u32         id; //设备实例id
    spinlock_t      devres_lock;//设备资源链表锁
    struct list_head    devres_head;//设备资源链表
    struct class        *class;//设备的类
    const struct attribute_group **groups;  //可选的属性组
    void    (*release)(struct device *dev);//在所有引用结束后释放设备
    struct iommu_group  *iommu_group;//该设备属于的IOMMU组
    struct dev_iommu    *iommu;//每个设备的通用IOMMU运行时数据
};

```

device结构很大，这里删除了我们不需要关心的内容。另外，我们看到device结构中同样包含了kobject结构，这使得设备可以加入kset和kobject组建的层次结构中。device结构中有总线和驱动指针，这能帮助设备找到自己的驱动程序和总线。

### 驱动

有了设备结构，还需要有设备对应的驱动，Linux是如何表示一个驱动的呢？同样也是一个数据结构，其中包含了驱动程序的相关信息。其实在device结构中我们就看到了，就是device\_driver结构，代码如下。

```
struct device_driver {
    const char      *name;//驱动名称
    struct bus_type     *bus;//指向总线
    struct module       *owner;//模块持有者
    const char      *mod_name;//用于内置模块
    bool suppress_bind_attrs;//禁用通过sysfs的绑定/解绑
    enum probe_type probe_type;//要使用的探查类型（同步或异步）
    const struct of_device_id   *of_match_table;//开放固件表
    const struct acpi_device_id *acpi_match_table;//ACPI匹配表
    //被调用来查询一个特定设备的存在
    int (*probe) (struct device *dev);
    //将设备状态同步到软件状态时调用
    void (*sync_state)(struct device *dev);
    //当设备被从系统中移除时被调用，以便解除设备与该驱动的绑定
    int (*remove) (struct device *dev);
    //关机时调用，使设备停止
    void (*shutdown) (struct device *dev);
    //调用以使设备进入睡眠模式，通常是进入一个低功率状态
    int (*suspend) (struct device *dev, pm_message_t state);
    //调用以使设备从睡眠模式中恢复
    int (*resume) (struct device *dev);
    //默认属性
    const struct attribute_group **groups;
    //绑定设备的属性
    const struct attribute_group **dev_groups;
    //设备电源操作
    const struct dev_pm_ops *pm;
    //当sysfs目录被写入时被调用
    void (*coredump) (struct device *dev);
    //驱动程序私有数据
    struct driver_private *p;
};
struct driver_private {
    struct kobject kobj;
    struct klist klist_devices;//驱动管理的所有设备的链表
    struct klist_node knode_bus;//加入bus链表的节点
    struct module_kobject *mkobj;//指向用kobject管理模块节点
    struct device_driver *driver;//指向驱动本身
};

```

在device\_driver结构中，包含了驱动程序的名字、驱动程序所在模块、设备探查和电源相关的回调函数的指针。在driver\_private结构中同样包含了kobject结构，用于组织所有的驱动，还指向了驱动本身，你发现没有，bus\_type中的subsys\_private结构的机制如出一辙。

### 文件操作函数

前面我们学习的都是Linux驱动程序的核心数据结构，我们很少用到，只是为了让你了解最基础的原理。

其实，在Linux系统中提供了更为高级的封装，Linux将设备分成几类分别是：字符设备、块设备、网络设备以及杂项设备。具体情况你可以参考我后面梳理的图表。

![](https://static001.geekbang.org/resource/image/a4/79/a4104a41c67d94f6c9a7de94a05c6a79.jpg?wh=1554x683)

这些类型的设备的数据结构，都会直接或者间接包含基础的device结构，我们以杂项设备为例子研究一下，Linux用miscdevice结构表示一个杂项设备，代码如下。

```
struct miscdevice  {
    int minor;//设备号
    const char *name;//设备名称
    const struct file_operations *fops;//文件操作函数结构
    struct list_head list;//链表
    struct device *parent;//指向父设备的device结构
    struct device *this_device;//指向本设备的device结构
    const struct attribute_group **groups;
    const char *nodename;//节点名字
    umode_t mode;//访问权限
};

```

miscdevice结构就是一个杂项设备，它一般在驱动程序代码文件中静态定义。我们清楚地看见有个this\_device指针，它指向下层的、属于这个杂项设备的device结构。

但是这里重点是 **file\_operations结构**，设备一经注册，就会在sys相关的目录下建立设备对应的文件结点，对这个文件结点打开、读写等操作，最终会调用到驱动程序对应的函数，而对应的函数指针就保存在file\_operations结构中，我们现在来看看这个结构。

```
struct file_operations {
    struct module *owner;//所在的模块
    loff_t (*llseek) (struct file *, loff_t, int);//调整读写偏移
    ssize_t (*read) (struct file *, char __user *, size_t, loff_t *);//读
    ssize_t (*write) (struct file *, const char __user *, size_t, loff_t *);//写
    int (*mmap) (struct file *, struct vm_area_struct *);//映射
    int (*open) (struct inode *, struct file *);//打开
    int (*flush) (struct file *, fl_owner_t id);//刷新
    int (*release) (struct inode *, struct file *);//关闭
} __randomize_layout;

```

file\_operations结构中的函数指针有31个，我删除了我们不熟悉的函数指针，我们了解原理，不需要搞清楚所有函数指针的功能。

那么，Linux如何调用到这个file\_operations结构中的函数呢？我以打开操作为例给你讲讲，Linux的打开系统调用接口会调用filp\_open函数，filp\_open函数的调用路径如下所示。

```
//filp_open
//file_open_name
//do_filp_open
//path_openat
static int do_o_path(struct nameidata *nd, unsigned flags, struct file *file)
{
    struct path path;
    int error = path_lookupat(nd, flags, &path);//解析文件路径得到文件inode节点
    if (!error) {
        audit_inode(nd->name, path.dentry, 0);
        error = vfs_open(&path, file);//vfs层打开文件接口
        path_put(&path);
    }
    return error;
}
int vfs_open(const struct path *path, struct file *file)
{
    file->f_path = *path;
    return do_dentry_open(file, d_backing_inode(path->dentry), NULL);
}
static int do_dentry_open(struct file *f, struct inode *inode,int (*open)(struct inode *, struct file *))
{
    //略过我们不想看的代码
    f->f_op = fops_get(inode->i_fop);//获取文件节点的file_operations
    if (!open)//如果open为空则调用file_operations结构中的open函数
        open = f->f_op->open;
    if (open) {
        error = open(inode, f);
    }
    //略过我们不想看的代码
    return 0;
}

```

看到这里，我们就知道了，file\_operations结构的地址存在一个文件的inode结构中。在Linux系统中，都是用inode结构表示一个文件，不管它是数据文件还是设备文件。

到这里，我们已经清楚了文件操作函数以及它的调用流程。

## 驱动程序实例

我们想要真正理解Linux设备驱动，最好的方案就是写一个真实的驱动程序实例。下面我们一起应用前面的基础，结合Linux提供的驱动程序开发接口，一起实现一个真实驱动程序。

这个驱动程序的主要工作，就是获取所有总线和其下所有设备的名字。为此我们需要先了解驱动程序的整体框架，接着建立我们总线和设备，然后实现驱动程序的打开、关闭，读写操作函数，最后我们写个应用程序，来测试我们的驱动程序。

### 驱动程序框架

Linux内核的驱动程序是在一个可加载的内核模块中实现，可加载的内核模块只需要两个函数和模块信息就行，但是我们要在模块中实现总线和设备驱动，所以需要更多的函数和数据结构，它们的代码如下。

```
#define DEV_NAME  "devicesinfo"
#define BUS_DEV_NAME  "devicesinfobus"

static int misc_find_match(struct device *dev, void *data)
{
    printk(KERN_EMERG "device name is:%s\n", dev->kobj.name);
    return 0;
}
//对应于设备文件的读操作函数
static ssize_t misc_read (struct file *pfile, char __user *buff, size_t size, loff_t *off)
{
    printk(KERN_EMERG "line:%d,%s is call\n",__LINE__,__FUNCTION__);
    return 0;
}
//对应于设备文件的写操作函数
static ssize_t misc_write(struct file *pfile, const char __user *buff, size_t size, loff_t *off)
{
    printk(KERN_EMERG "line:%d,%s is call\n",__LINE__,__FUNCTION__);
    return 0;
}
//对应于设备文件的打开操作函数
static int  misc_open(struct inode *pinode, struct file *pfile)
{
    printk(KERN_EMERG "line:%d,%s is call\n",__LINE__,__FUNCTION__);
    return 0;
}
//对应于设备文件的关闭操作函数
static int misc_release(struct inode *pinode, struct file *pfile)
{
    printk(KERN_EMERG "line:%d,%s is call\n",__LINE__,__FUNCTION__);
    return 0;
}

static int devicesinfo_bus_match(struct device *dev, struct device_driver *driver)
{
        return !strncmp(dev->kobj.name, driver->name, strlen(driver->name));
}
//对应于设备文件的操作函数结构
static const  struct file_operations misc_fops = {
    .read     = misc_read,
    .write    = misc_write,
    .release  = misc_release,
    .open     = misc_open,
};
//misc设备的结构
static struct miscdevice  misc_dev =  {
    .fops  =  &misc_fops,         //设备文件操作方法
    .minor =  255,                //次设备号
    .name  =  DEV_NAME,           //设备名/dev/下的设备节点名
};
//总线结构
struct bus_type devicesinfo_bus = {
        .name = BUS_DEV_NAME, //总线名字
        .match = devicesinfo_bus_match, //总线match函数指针
};
//内核模块入口函数
static int __init miscdrv_init(void)
{
    printk(KERN_EMERG "INIT misc\n")；
    return 0;
}
//内核模块退出函数
static void  __exit miscdrv_exit(void)
{
    printk(KERN_EMERG "EXIT,misc\n");
}
module_init(miscdrv_init);//申明内核模块入口函数
module_exit(miscdrv_exit);//申明内核模块退出函数
MODULE_LICENSE("GPL");//模块许可
MODULE_AUTHOR("LMOS");//模块开发者

```

一个最简单的驱动程序框架的内核模块就写好了，该有的函数和数据结构都有了，那些数据结构都是静态定义的，它们的内部字段我们在前面也已经了解了。这个模块一旦加载就会执行miscdrv\_init函数，卸载时就会执行miscdrv\_exit函数。

### 建立设备

Linux系统也提供了很多专用接口函数，用来建立总线和设备。下面我们先来建立一个总线，然后在总线下建立一个设备。

首先来说说建立一个总线，Linux系统提供了一个bus\_register函数向内核注册一个总线，相当于建立了一个总线，我们需要在miscdrv\_init函数中调用它，代码如下所示。

```
static int __init miscdrv_init(void)
{
    printk(KERN_EMERG "INIT misc\n");
    busok = bus_register(&devicesinfo_bus);//注册总线
    return 0;
}

```

bus\_register函数会在系统中注册一个总线，所需参数就是总线结构的地址(&devicesinfo\_bus)，返回非0表示注册失败。现在我们来看看，在bus\_register函数中都做了些什么事情，代码如下所示。

```
int bus_register(struct bus_type *bus)
{
    int retval;
    struct subsys_private *priv;
    //分配一个subsys_private结构
    priv = kzalloc(sizeof(struct subsys_private), GFP_KERNEL);
    //bus_type和subsys_private结构互相指向
    priv->bus = bus;
    bus->p = priv;
    //把总线的名称加入subsys_private的kobject中
    retval = kobject_set_name(&priv->subsys.kobj, "%s", bus->name);
    priv->subsys.kobj.kset = bus_kset;//指向bus_kset
    //把subsys_private中的kset注册到系统中
    retval = kset_register(&priv->subsys);
    //建立总线的文件结构在sysfs中
    retval = bus_create_file(bus, &bus_attr_uevent);
    //建立subsys_private中的devices和drivers的kset
    priv->devices_kset = kset_create_and_add("devices", NULL,
                         &priv->subsys.kobj);
    priv->drivers_kset = kset_create_and_add("drivers", NULL,
                         &priv->subsys.kobj);
    //建立subsys_private中的devices和drivers链表，用于属于总线的设备和驱动
    klist_init(&priv->klist_devices, klist_devices_get, klist_devices_put);
    klist_init(&priv->klist_drivers, NULL, NULL);
    return 0;
}

```

我删除了很多你不用关注的代码，看到这里，你应该知道总线是怎么通过subsys\_private把设备和驱动关联起来的（通过bus\_type和subsys\_private结构互相指向），下面我们看看怎么建立设备。我们这里建立一个misc杂项设备。misc杂项设备需要定一个数据结构，然后调用misc杂项设备注册接口函数，代码如下。

```
#define DEV_NAME  "devicesinfo"
static const  struct file_operations misc_fops = {
    .read     = misc_read,
    .write    = misc_write,
    .release  = misc_release,
    .open     = misc_open,
};
static struct miscdevice  misc_dev =  {
    .fops  =  &misc_fops,         //设备文件操作方法
    .minor =  255,                //次设备号
    .name  =  DEV_NAME,           //设备名/dev/下的设备节点名
};
static int __init miscdrv_init(void)
{
    misc_register(&misc_dev);//注册misc杂项设备
    printk(KERN_EMERG "INIT misc busok\n");
    busok = bus_register(&devicesinfo_bus);//注册总线
    return 0;
}

```

上面的代码中，静态定义了miscdevice结构的变量misc\_dev，miscdevice结构我们在前面已经了解过了，最后调用misc\_register函数注册了misc杂项设备。

misc\_register函数到底做了什么，我们一起来看看，代码如下所示。

```
int misc_register(struct miscdevice *misc)
{
    dev_t dev;
    int err = 0;
    bool is_dynamic = (misc->minor == MISC_DYNAMIC_MINOR);
    INIT_LIST_HEAD(&misc->list);
    mutex_lock(&misc_mtx);
    if (is_dynamic) {//minor次设备号如果等于255就自动分配次设备
        int i = find_first_zero_bit(misc_minors, DYNAMIC_MINORS);
        if (i >= DYNAMIC_MINORS) {
            err = -EBUSY;
            goto out;
        }
        misc->minor = DYNAMIC_MINORS - i - 1;
        set_bit(i, misc_minors);
    } else {//否则检查次设备号是否已经被占有
        struct miscdevice *c;
        list_for_each_entry(c, &misc_list, list) {
            if (c->minor == misc->minor) {
                err = -EBUSY;
                goto out;
            }
        }
    }
    dev = MKDEV(MISC_MAJOR, misc->minor);//合并主、次设备号
    //建立设备
    misc->this_device =
        device_create_with_groups(misc_class, misc->parent, dev,
                      misc, misc->groups, "%s", misc->name);
    //把这个misc加入到全局misc_list链表
    list_add(&misc->list, &misc_list);
 out:
    mutex_unlock(&misc_mtx);
    return err;
}

```

可以看出，misc\_register函数只是负责分配设备号，以及把miscdev加入链表，真正的核心工作由device\_create\_with\_groups函数来完成，代码如下所示。

```
struct device *device_create_with_groups(struct class *class,
                     struct device *parent, dev_t devt,void *drvdata,const struct attribute_group **groups,const char *fmt, ...)
{
    va_list vargs;
    struct device *dev;
    va_start(vargs, fmt);
    dev = device_create_groups_vargs(class, parent, devt, drvdata, groups,fmt, vargs);
    va_end(vargs);
    return dev;
}
struct device *device_create_groups_vargs(struct class *class, struct device *parent, dev_t devt, void *drvdata,const struct attribute_group **groups,const char *fmt, va_list args)
{
    struct device *dev = NULL;
    int retval = -ENODEV;
    dev = kzalloc(sizeof(*dev), GFP_KERNEL);//分配设备结构的内存空间
    device_initialize(dev);//初始化设备结构
    dev->devt = devt;//设置设备号
    dev->class = class;//设置设备类
    dev->parent = parent;//设置设备的父设备
    dev->groups = groups;////设置设备属性
    dev->release = device_create_release;
    dev_set_drvdata(dev, drvdata);//设置miscdev的地址到设备结构中
    retval = kobject_set_name_vargs(&dev->kobj, fmt, args);//把名称设置到设备的kobjext中去
    retval = device_add(dev);//把设备加入到系统中
    if (retval)
        goto error;
    return dev;//返回设备
error:
    put_device(dev);
    return ERR_PTR(retval);
}

```

到这里，misc设备的注册就搞清楚了，下面我们来测试一下看看结果，看看Linux系统是不是多了一个总线和设备。

你可以在本课程的代码目录中，执行make指令，就会产生一个miscdvrv.ko内核模块文件，我们把这个模块文件加载到Linux系统中就行了。

为了看到效果，我们还必须要做另一件事情。 在终端中用sudo cat /proc/kmsg 指令读取/proc/kmsg文件，该文件是内核prink函数输出信息的文件。指令如下所示。

```
#第一步在终端中执行如下指令
sudo cat /proc/kmsg
#第二步在另一个终端中执行如下指令
make
sudo insmod miscdrv.ko
#不用这个模块了可以用以下指令卸载
sudo rmmod miscdrv.ko

```

insmod指令是加载一个内核模块，一旦加载成功就会执行miscdrv\_init函数。如果不出意外，你在终端中会看到如下图所示的情况。

![](https://static001.geekbang.org/resource/image/93/3b/93a929ea1218c7f934713fbf03ba643b.jpg?wh=846x449)

这说明我们设备已经建立了，你应该可以在/dev目录看到一个devicesinfo文件，同时你在/sys/bus/目录下也可以看到一个devicesinfobus文件。这就是我们建立的设备和总线的文件节点的名称。

### 打开、关闭、读写函数

建立了设备和总线，有了设备文件节点，应用程序就可以打开、关闭以及读写这个设备文件了。

虽然现在确实可以操作设备文件了，只不过还不能完成任何实际功能，因为我们只是写好了框架函数，所以我们下面就去写好并填充这些框架函数，代码如下所示。

```
//打开
static int  misc_open(struct inode *pinode, struct file *pfile)
{
    printk(KERN_EMERG "line:%d,%s is call\n",__LINE__,__FUNCTION__);//打印这个函数所在文件的行号和名称
    return 0;
}
//关闭
static int misc_release(struct inode *pinode, struct file *pfile)
{
    printk(KERN_EMERG "line:%d,%s is call\n",__LINE__,__FUNCTION__);//打印这个函数所在文件的行号和名称
    return 0;
}
//写
static ssize_t misc_write(struct file *pfile, const char __user *buff, size_t size, loff_t *off)
{
    printk(KERN_EMERG "line:%d,%s is call\n",__LINE__,__FUNCTION__);//打印这个函数所在文件的行号和名称
    return 0;
}

```

以上三个函数，仍然没干什么实际工作，就是打印该函数所在文件的行号和名称，然后返回0就完事了。回到前面，我们的目的是要获取Linux中所有总线上的所有设备，所以在读函数中来实现是合理的。

具体实现的代码如下所示。

```
#define to_subsys_private(obj) container_of(obj, struct subsys_private, subsys.kobj)//从kobject上获取subsys_private的地址
struct kset *ret_buskset(void)
{
    struct subsys_private *p;
    if(busok)
        return NULL;
    if(!devicesinfo_bus.p)
        return NULL;
    p = devicesinfo_bus.p;
    if(!p->subsys.kobj.kset)
        return NULL;
    //返回devicesinfo_bus总线上的kset，正是bus_kset
    return p->subsys.kobj.kset;
}
static int misc_find_match(struct device *dev, void *data)
{
    struct bus_type* b = (struct bus_type*)data;
    printk(KERN_EMERG "%s---->device name is:%s\n", b->name, dev->kobj.name);//打印总线名称和设备名称
    return 0;
}
static ssize_t misc_read (struct file *pfile, char __user *buff, size_t size, loff_t *off)
{
    struct kobject* kobj;
    struct kset* kset;
    struct subsys_private* p;
    kset = ret_buskset();//获取bus_kset的地址
    if(!kset)
        return 0;
    printk(KERN_EMERG "line:%d,%s is call\n",__LINE__,__FUNCTION__);//打印这个函数所在文件的行号和名称
    //扫描所有总线的kobject
    list_for_each_entry(kobj, &kset->list, entry)
    {
        p = to_subsys_private(kobj);
        printk(KERN_EMERG "Bus name is:%s\n",p->bus->name);
        //遍历具体总线上的所有设备
        bus_for_each_dev(p->bus, NULL, p->bus, misc_find_match);
    }
    return 0;
}

```

正常情况下，我们是不能获取bus\_kset地址的，它是所有总线的根，包含了所有总线的kobject，Linux为了保护bus\_kset，并没有在bus\_type结构中直接包含kobject，而是让总线指向一个subsys\_private结构，在其中包含了kobject结构。

所以，我们要注册一个总线，这样就能拔出萝卜带出泥，得到bus\_kset，根据它又能找到所有subsys\_private结构中的kobject，接着找到subsys\_private结构，反向查询到bus\_type结构的地址。

然后调用Linux提供的bus\_for\_each\_dev函数，就可以遍历一个总线上的所有设备，它每遍历到一个设备，就调用一个函数，这个函数是用参数的方式传给它的，在我们代码中就是misc\_find\_match函数。

在调用misc\_find\_match函数时，会把一个设备结构的地址和另一个指针作为参数传递进来。最后就能打印每个设备的名称了。

### 测试驱动

驱动程序已经写好，加载之后会自动建立设备文件，但是驱动程序不会主动工作，我们还需要写一个应用程序，对设备文件进行读写，才能测试驱动。我们这里这个驱动对打开、关闭、写操作没有什么实际的响应，但是只要一读就会打印所有设备的信息了。

下面我们来写好这个应用，代码如下所示。

```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#define DEV_NAME "/dev/devicesinfo"
int main(void)
{
    char buf[] = {0, 0, 0, 0};
    int fd;
    //打开设备文件
    fd = open(DEV_NAME, O_RDWR);
    if (fd < 0) {
        printf("打开 :%s 失败!\n", DEV_NAME);
    }
    //写数据到内核空间
    write(fd, buf, 4);
    //从内核空间中读取数据
    read(fd, buf, 4);
    //关闭设备,也可以不调用，程序关闭时系统自动调用
    close(fd);
    return 0;
}

```

你可以这样操作：切换到本课程的代码目录make一下，然后加载miscdrv.ko模块，最后在终端中执行sudo ./app，就能在另一个已经执行了sudo cat /proc/kmsg的终端中，看到后面图片这样形式的数据。

![](https://static001.geekbang.org/resource/image/29/1c/29e4b5f1a05d114423b3e69b796ccc1c.jpg?wh=990x1047)

上图是我系统中总线名和设备名，你的计算机上可能略有差异，因为我们的计算机硬件可能不同，所以有差异是正常的，不必奇怪。

## 重点回顾

尽管Linux驱动模型异常复杂，我们还是以最小的成本，领会了Linux驱动模型设计的要点，还动手写了个小小的驱动程序。现在我来为你梳理一下这节课的重点。

首先，我们通过查看sys目录下的文件层次结构，直观感受了一下Linux系统的总线、设备、驱动是什么情况。

然后，我们了解一些重要的数据结构，它们分别是总线、驱动、设备、文件操作函数结构，还有非常关键的 **kset和kobject**，这两个结构一起组织了总线、设备、驱动，最终形成了类目录文件这样的层次结构。

最后，我们建立一个驱动程序实例，从驱动程序框架开始，我们了解如何建立一个总线和设备，编写了对应的文件操作函数，在读操作函数中实现扫描了所有总线上的所有设备，并打印总线名称和设备名称，还写了个应用程序进行了测试，检查有没有达到预期的功能。

如果你对Linux是怎么在总线上注册设备和驱动，又对驱动和设备怎么进行匹配感兴趣的话，也可以自己阅读Linux内核代码，其中有很多驱动实例，你可以研究和实验，动手和动脑相结合，我相信你一定可以搞清楚的。

## 思考题

为什么无论是我们加载miscdrv.ko内核模块，还是运行app测试，都要在前面加上sudo呢？

欢迎你在留言区记录你的学习收获，也欢迎你把这节课分享给你身边的小伙伴，一起拿下Linux设备驱动的内容。

我是LMOS，我们下节课见！