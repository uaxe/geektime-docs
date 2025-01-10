上一节，我们讲了一下虚拟化的基本原理，以及qemu、kvm之间的关系。这一节，我们就来看一下，用户态的qemu和内核态的kvm如何一起协作，来创建虚拟机，实现CPU和内存虚拟化。

这里是上一节我们讲的qemu启动时候的命令。

```
qemu-system-x86_64 -enable-kvm -name ubuntutest  -m 2048 -hda ubuntutest.qcow2 -vnc :19 -net nic,model=virtio -nettap,ifname=tap0,script=no,downscript=no

```

接下来，我们在 [这里下载](https://www.qemu.org/) qemu的代码。qemu的main函数在vl.c下面。这是一个非常非常长的函数，我们来慢慢地解析它。

## 1.初始化所有的Module

第一步，初始化所有的Module，调用下面的函数。

```
module_call_init(MODULE_INIT_QOM);

```

上一节我们讲过，qemu作为中间人其实挺累的，对上面的虚拟机需要模拟各种各样的外部设备。当虚拟机真的要使用物理资源的时候，对下面的物理机上的资源要进行请求，所以它的工作模式有点儿类似操作系统对接驱动。驱动要符合一定的格式，才能算操作系统的一个模块。同理，qemu为了模拟各种各样的设备，也需要管理各种各样的模块，这些模块也需要符合一定的格式。

定义一个qemu模块会调用type\_init。例如，kvm的模块要在accel/kvm/kvm-all.c文件里面实现。在这个文件里面，有一行下面的代码：

```
type_init(kvm_type_init);

#define type_init(function) module_init(function, MODULE_INIT_QOM)

#define module_init(function, type)                                         \
static void __attribute__((constructor)) do_qemu_init_ ## function(void)    \
{                                                                           \
    register_module_init(function, type);                                   \
}

void register_module_init(void (*fn)(void), module_init_type type)
{
    ModuleEntry *e;
    ModuleTypeList *l;

    e = g_malloc0(sizeof(*e));
    e->init = fn;
    e->type = type;

    l = find_type(type);

    QTAILQ_INSERT_TAIL(l, e, node);
}

```

从代码里面的定义我们可以看出来，type\_init后面的参数是一个函数，调用type\_init就相当于调用module\_init，在这里函数就是kvm\_type\_init，类型就是MODULE\_INIT\_QOM。是不是感觉和驱动有点儿像？

module\_init最终要调用register\_module\_init。属于MODULE\_INIT\_QOM这种类型的，有一个Module列表ModuleTypeList，列表里面是一项一项的ModuleEntry。KVM就是其中一项，并且会初始化每一项的init函数为参数表示的函数fn，也即KVM这个module的init函数就是kvm\_type\_init。

当然，MODULE\_INIT\_QOM这种类型会有很多很多的module，从后面的代码我们可以看到，所有调用type\_init的地方都注册了一个MODULE\_INIT\_QOM类型的Module。

了解了Module的注册机制，我们继续回到main函数中module\_call\_init的调用。

```
void module_call_init(module_init_type type)
{
    ModuleTypeList *l;
    ModuleEntry *e;
    l = find_type(type);
    QTAILQ_FOREACH(e, l, node) {
        e->init();
    }
}

```

在module\_call\_init中，我们会找到MODULE\_INIT\_QOM这种类型对应的ModuleTypeList，找出列表中所有的ModuleEntry，然后调用每个ModuleEntry的init函数。这里需要注意的是，在module\_call\_init调用的这一步，所有Module的init函数都已经被调用过了。

后面我们会看到很多的Module，当你看到它们的时候，你需要意识到，它的init函数在这里也被调用过了。这里我们还是以对于kvm这个module为例子，看看它的init函数都做了哪些事情。你会发现，其实它调用的是kvm\_type\_init。

```
static void kvm_type_init(void)
{
    type_register_static(&kvm_accel_type);
}

TypeImpl *type_register_static(const TypeInfo *info)
{
    return type_register(info);
}

TypeImpl *type_register(const TypeInfo *info)
{
    assert(info->parent);
    return type_register_internal(info);
}

static TypeImpl *type_register_internal(const TypeInfo *info)
{
    TypeImpl *ti;
    ti = type_new(info);

    type_table_add(ti);
    return ti;
}

static TypeImpl *type_new(const TypeInfo *info)
{
    TypeImpl *ti = g_malloc0(sizeof(*ti));
    int i;

    if (type_table_lookup(info->name) != NULL) {
    }

    ti->name = g_strdup(info->name);
    ti->parent = g_strdup(info->parent);

    ti->class_size = info->class_size;
    ti->instance_size = info->instance_size;

    ti->class_init = info->class_init;
    ti->class_base_init = info->class_base_init;
    ti->class_data = info->class_data;

    ti->instance_init = info->instance_init;
    ti->instance_post_init = info->instance_post_init;
    ti->instance_finalize = info->instance_finalize;

    ti->abstract = info->abstract;

    for (i = 0; info->interfaces && info->interfaces[i].type; i++) {
        ti->interfaces[i].typename = g_strdup(info->interfaces[i].type);
    }
    ti->num_interfaces = i;

    return ti;
}

static void type_table_add(TypeImpl *ti)
{
    assert(!enumerating_types);
    g_hash_table_insert(type_table_get(), (void *)ti->name, ti);
}

static GHashTable *type_table_get(void)
{
    static GHashTable *type_table;

    if (type_table == NULL) {
        type_table = g_hash_table_new(g_str_hash, g_str_equal);
    }

    return type_table;
}

static const TypeInfo kvm_accel_type = {
    .name = TYPE_KVM_ACCEL,
    .parent = TYPE_ACCEL,
    .class_init = kvm_accel_class_init,
    .instance_size = sizeof(KVMState),
};

```

每一个Module既然要模拟某种设备，那应该定义一种类型TypeImpl来表示这些设备，这其实是一种面向对象编程的思路，只不过这里用的是纯C语言的实现，所以需要变相实现一下类和对象。

kvm\_type\_init会注册kvm\_accel\_type，定义上面的代码，我们可以认为这样动态定义了一个类。这个类的名字是TYPE\_KVM\_ACCEL，这个类有父类TYPE\_ACCEL，这个类的初始化应该调用函数kvm\_accel\_class\_init（看，这里已经直接叫类class了）。如果用这个类声明一个对象，对象的大小应该是instance\_size。是不是有点儿Java语言反射的意思，根据一些名称的定义，一个类就定义好了。

这里的调用链为：kvm\_type\_init->type\_register\_static->type\_register->type\_register\_internal。

在type\_register\_internal中，我们会根据kvm\_accel\_type这个TypeInfo，创建一个TypeImpl来表示这个新注册的类，也就是说，TypeImpl才是我们想要声明的那个class。在qemu里面，有一个全局的哈希表type\_table，用来存放所有定义的类。在type\_new里面，我们先从全局表里面根据名字找这个类。如果找到，说明这个类曾经被注册过，就报错；如果没有找到，说明这是一个新的类，则将TypeInfo里面信息填到TypeImpl里面。type\_table\_add会将这个类注册到全局的表里面。到这里，我们注意，class\_init还没有被调用，也即这个类现在还处于纸面的状态。

这点更加像Java的反射机制了。在Java里面，对于一个类，首先我们写代码的时候要写一个class xxx的定义，编译好就放在.class文件中，这也是出于纸面的状态。然后，Java会有一个Class对象，用于读取和表示这个纸面上的class xxx，可以生成真正的对象。

相同的过程在后面的代码中我们也可以看到，class\_init会生成XXXClass，就相当于Java里面的Class对象，TypeImpl还会有一个instance\_init函数，相当于构造函数，用于根据XXXClass生成Object，这就相当于Java反射里面最终创建的对象。和构造函数对应的还有instance\_finalize，相当于析构函数。

这一套反射机制放在qom文件夹下面，全称QEMU Object Model，也即用C实现了一套面向对象的反射机制。

说完了初始化Module，我们还回到main函数接着分析。

## 2.解析qemu的命令行

第二步我们就要开始解析qemu的命令行了。qemu的命令行解析，就是下面这样一长串。还记得咱们自己写过一个解析命令行参数的程序吗？这里的opts是差不多的意思。

```
    qemu_add_opts(&qemu_drive_opts);
    qemu_add_opts(&qemu_chardev_opts);
    qemu_add_opts(&qemu_device_opts);
    qemu_add_opts(&qemu_netdev_opts);
    qemu_add_opts(&qemu_nic_opts);
    qemu_add_opts(&qemu_net_opts);
    qemu_add_opts(&qemu_rtc_opts);
    qemu_add_opts(&qemu_machine_opts);
    qemu_add_opts(&qemu_accel_opts);
    qemu_add_opts(&qemu_mem_opts);
    qemu_add_opts(&qemu_smp_opts);
    qemu_add_opts(&qemu_boot_opts);
    qemu_add_opts(&qemu_name_opts);
    qemu_add_opts(&qemu_numa_opts);

```

为什么有这么多的opts呢？这是因为，我们上一节给的参数都是简单的参数，实际运行中创建的kvm参数会复杂N倍。这里我们贴一个开源云平台软件OpenStack创建出来的KVM的参数，如下所示。不要被吓坏，你不需要全部看懂，只需要看懂一部分就行了。具体我来给你解析。

```
qemu-system-x86_64
-enable-kvm
-name instance-00000024
-machine pc-i440fx-trusty,accel=kvm,usb=off
-cpu SandyBridge,+erms,+smep,+fsgsbase,+pdpe1gb,+rdrand,+f16c,+osxsave,+dca,+pcid,+pdcm,+xtpr,+tm2,+est,+smx,+vmx,+ds_cpl,+monitor,+dtes64,+pbe,+tm,+ht,+ss,+acpi,+ds,+vme
-m 2048
-smp 1,sockets=1,cores=1,threads=1
......
-rtc base=utc,driftfix=slew
-drive file=/var/lib/nova/instances/1f8e6f7e-5a70-4780-89c1-464dc0e7f308/disk,if=none,id=drive-virtio-disk0,format=qcow2,cache=none
-device virtio-blk-pci,scsi=off,bus=pci.0,addr=0x4,drive=drive-virtio-disk0,id=virtio-disk0,bootindex=1
-netdev tap,fd=32,id=hostnet0,vhost=on,vhostfd=37
-device virtio-net-pci,netdev=hostnet0,id=net0,mac=fa:16:3e:d1:2d:99,bus=pci.0,addr=0x3
-chardev file,id=charserial0,path=/var/lib/nova/instances/1f8e6f7e-5a70-4780-89c1-464dc0e7f308/console.log
-vnc 0.0.0.0:12
-device cirrus-vga,id=video0,bus=pci.0,addr=0x2

```

- -enable-kvm：表示启用硬件辅助虚拟化。

- -name instance-00000024：表示虚拟机的名称。

- -machine pc-i440fx-trusty,accel=kvm,usb=off：machine是什么呢？其实就是计算机体系结构。不知道什么是体系结构的话，可以订阅极客时间的另一个专栏《深入浅出计算机组成原理》。


  qemu会模拟多种体系结构，常用的有普通PC机，也即x86的32位或者64位的体系结构、Mac电脑PowerPC的体系结构、Sun的体系结构、MIPS的体系结构，精简指令集。如果使用KVM hardware-assisted virtualization，也即BIOS中VD-T是打开的，则参数中accel=kvm。如果不使用hardware-assisted virtualization，用的是纯模拟，则有参数accel = tcg，-no-kvm。

- -cpu SandyBridge,+erms,+smep,+fsgsbase,+pdpe1gb,+rdrand,+f16c,+osxsave,+dca,+pcid,+pdcm,+xtpr,+tm2,+est,+smx,+vmx,+ds\_cpl,+monitor,+dtes64,+pbe,+tm,+ht,+ss,+acpi,+ds,+vme：表示设置CPU，SandyBridge是Intel处理器，后面的加号都是添加的CPU的参数，这些参数会显示在/proc/cpuinfo里面。

- -m 2048：表示内存。

- -smp 1,sockets=1,cores=1,threads=1：SMP我们解析过，叫对称多处理器，和NUMA对应。qemu仿真了一个具有1个vcpu，一个socket，一个core，一个threads的处理器。


  socket、core、threads是什么概念呢？socket就是主板上插cpu的槽的数目，也即常说的“路”，core就是我们平时说的“核”，即双核、4核等。thread就是每个core的硬件线程数，即超线程。举个具体的例子，某个服务器是：2路4核超线程（一般默认为2个线程），通过cat /proc/cpuinfo，我们看到的是2 _4_ 2=16个processor，很多人也习惯成为16核了。

- -rtc base=utc,driftfix=slew：表示系统时间由参数-rtc指定。

- -device cirrus-vga,id=video0,bus=pci.0,addr=0x2：表示显示器用参数-vga设置，默认为cirrus，它模拟了CL-GD5446PCI VGA card。

- 有关网卡，使用-net参数和-device。

- 从HOST角度：-netdev tap,fd=32,id=hostnet0,vhost=on,vhostfd=37。

- 从GUEST角度：-device virtio-net-pci,netdev=hostnet0,id=net0,mac=fa:16:3e:d1:2d:99,bus=pci.0,addr=0x3。

- 有关硬盘，使用-hda -hdb，或者使用-drive和-device。

- 从HOST角度：-drive file=/var/lib/nova/instances/1f8e6f7e-5a70-4780-89c1-464dc0e7f308/disk,if=none,id=drive-virtio-disk0,format=qcow2,cache=none

- 从GUEST角度：-device virtio-blk-pci,scsi=off,bus=pci.0,addr=0x4,drive=drive-virtio-disk0,id=virtio-disk0,bootindex=1

- -vnc 0.0.0.0:12：设置VNC。


在main函数中，接下来的for循环和大量的switch case语句，就是对于这些参数的解析，我们不一一解析，后面真的用到这些参数的时候，我们再仔细看。

## 3.初始化machine

回到main函数，接下来是初始化machine。

```
machine_class = select_machine();
current_machine = MACHINE(object_new(object_class_get_name(
                          OBJECT_CLASS(machine_class))));

```

这里面的machine\_class是什么呢？这还得从machine参数说起。

```
-machine pc-i440fx-trusty,accel=kvm,usb=off

```

这里的pc-i440fx是x86机器默认的体系结构。在hw/i386/pc\_piix.c中，它定义了对应的machine\_class。

```
DEFINE_I440FX_MACHINE(v4_0, "pc-i440fx-4.0", NULL,
                      pc_i440fx_4_0_machine_options);

#define DEFINE_I440FX_MACHINE(suffix, name, compatfn, optionfn) \
    static void pc_init_##suffix(MachineState *machine) \
    { \
......
        pc_init1(machine, TYPE_I440FX_PCI_HOST_BRIDGE, \
                 TYPE_I440FX_PCI_DEVICE); \
    } \
    DEFINE_PC_MACHINE(suffix, name, pc_init_##suffix, optionfn)

#define DEFINE_PC_MACHINE(suffix, namestr, initfn, optsfn) \
    static void pc_machine_##suffix##_class_init(ObjectClass *oc, void *data
) \
    { \
        MachineClass *mc = MACHINE_CLASS(oc); \
        optsfn(mc); \
        mc->init = initfn; \
    } \
    static const TypeInfo pc_machine_type_##suffix = { \
        .name       = namestr TYPE_MACHINE_SUFFIX, \
        .parent     = TYPE_PC_MACHINE, \
        .class_init = pc_machine_##suffix##_class_init, \
    }; \
    static void pc_machine_init_##suffix(void) \
    { \
        type_register(&pc_machine_type_##suffix); \
    } \
    type_init(pc_machine_init_##suffix)

```

为了定义machine\_class，这里有一系列的宏定义。入口是DEFINE\_I440FX\_MACHINE。这个宏有几个参数，v4\_0是后缀，"pc-i440fx-4.0"是名字，pc\_i440fx\_4\_0\_machine\_options是一个函数，用于定义machine\_class相关的选项。这个函数定义如下：

```
static void pc_i440fx_4_0_machine_options(MachineClass *m)
{
    pc_i440fx_machine_options(m);
    m->alias = "pc";
    m->is_default = 1;
}

static void pc_i440fx_machine_options(MachineClass *m)
{
    PCMachineClass *pcmc = PC_MACHINE_CLASS(m);
    pcmc->default_nic_model = "e1000";

    m->family = "pc_piix";
    m->desc = "Standard PC (i440FX + PIIX, 1996)";
    m->default_machine_opts = "firmware=bios-256k.bin";
    m->default_display = "std";
    machine_class_allow_dynamic_sysbus_dev(m, TYPE_RAMFB_DEVICE);
}

```

我们先不看pc\_i440fx\_4\_0\_machine\_options，先来看DEFINE\_I440FX\_MACHINE。

这里面定义了一个pc\_init\_##suffix，也就是pc\_init\_v4\_0。这里面转而调用pc\_init1。注意这里这个函数只是定义了一下，没有被调用。

接下来，DEFINE\_I440FX\_MACHINE里面又定义了DEFINE\_PC\_MACHINE。它有四个参数，除了DEFINE\_I440FX\_MACHINE传进来的三个参数以外，多了一个initfn，也即初始化函数，指向刚才定义的pc\_init\_##suffix。

在DEFINE\_PC\_MACHINE中，我们定义了一个函数pc\_machine\_##suffix## _class\_init。从函数的名字class\_init可以看出，这是machine\_class从纸面上的class初始化为Class对象的方法。在这个函数里面，我们可以看到，它创建了一个MachineClass对象，这个就是Class对象。MachineClass对象的init函数指向上面定义的pc\_init_##suffix，说明这个函数是machine这种类型初始化的一个函数，后面会被调用。

接着，我们看DEFINE\_PC\_MACHINE。它定义了一个pc\_machine\_type\_##suffix的TypeInfo。这是用于生成纸面上的class的原材料，果真后面调用了type\_init。

看到了type\_init，我们应该能够想到，既然它定义了一个纸面上的class，那上面的那句module\_call\_init，会和我们上面解析的type\_init是一样的，在全局的表里面注册了一个全局的名字是"pc-i440fx-4.0"的纸面上的class，也即TypeImpl。

现在全局表中有这个纸面上的class了。我们回到select\_machine。

```
static MachineClass *select_machine(void)
{
    MachineClass *machine_class = find_default_machine();
    const char *optarg;
    QemuOpts *opts;
......
    opts = qemu_get_machine_opts();
    qemu_opts_loc_restore(opts);

    optarg = qemu_opt_get(opts, "type");
    if (optarg) {
        machine_class = machine_parse(optarg);
    }
......
    return machine_class;
}

MachineClass *find_default_machine(void)
{
    GSList *el, *machines = object_class_get_list(TYPE_MACHINE, false);
    MachineClass *mc = NULL;
    for (el = machines; el; el = el->next) {
        MachineClass *temp = el->data;
        if (temp->is_default) {
            mc = temp;
            break;
        }
    }
    g_slist_free(machines);
    return mc;
}

static MachineClass *machine_parse(const char *name)
{
    MachineClass *mc = NULL;
    GSList *el, *machines = object_class_get_list(TYPE_MACHINE, false);

    if (name) {
        mc = find_machine(name);
    }
    if (mc) {
        g_slist_free(machines);
        return mc;
    }
......
}

```

在select\_machine中，有两种方式可以生成MachineClass。一种方式是find\_default\_machine，找一个默认的；另一种方式是machine\_parse，通过解析参数生成MachineClass。无论哪种方式，都会调用object\_class\_get\_list获得一个MachineClass的列表，然后在里面找。object\_class\_get\_list定义如下：

```
GSList *object_class_get_list(const char *implements_type,
                              bool include_abstract)
{
    GSList *list = NULL;

    object_class_foreach(object_class_get_list_tramp,
                         implements_type, include_abstract, &list);
    return list;
}

void object_class_foreach(void (*fn)(ObjectClass *klass, void *opaque), const char *implements_type, bool include_abstract,
                          void *opaque)
{
    OCFData data = { fn, implements_type, include_abstract, opaque };

    enumerating_types = true;
    g_hash_table_foreach(type_table_get(), object_class_foreach_tramp, &data);
    enumerating_types = false;
}

```

在全局表type\_table\_get()中，对于每一项TypeImpl，我们都执行object\_class\_foreach\_tramp。

```
static void object_class_foreach_tramp(gpointer key, gpointer value,
                                       gpointer opaque)
{
    OCFData *data = opaque;
    TypeImpl *type = value;
    ObjectClass *k;

    type_initialize(type);
    k = type->class;
......
    data->fn(k, data->opaque);
}

static void type_initialize(TypeImpl *ti)
{
    TypeImpl *parent;
......
    ti->class_size = type_class_get_size(ti);
    ti->instance_size = type_object_get_size(ti);
    if (ti->instance_size == 0) {
        ti->abstract = true;
    }
......
    ti->class = g_malloc0(ti->class_size);
......
    ti->class->type = ti;

    while (parent) {
        if (parent->class_base_init) {
            parent->class_base_init(ti->class, ti->class_data);
        }
        parent = type_get_parent(parent);
    }

    if (ti->class_init) {
        ti->class_init(ti->class, ti->class_data);
    }
}

```

在object\_class\_foreach\_tramp中，会调用将type\_initialize，这里面会调用class\_init将纸面上的class也即TypeImpl变为ObjectClass，ObjectClass是所有Class类的祖先，MachineClass是它的子类。

因为在machine的命令行里面，我们指定了名字为"pc-i440fx-4.0"，就肯定能够找到我们注册过了的TypeImpl，并调用它的class\_init函数。

因而pc\_machine\_##suffix## _class\_init会被调用，在这里面，pc\_i440fx\_machine\_options才真正被调用初始化MachineClass，并且将MachineClass的init函数设置为pc\_init_##suffix。也即，当select\_machine执行完毕后，就有一个MachineClass了。

接着，我们回到object\_new。这就很好理解了，MachineClass是一个Class类，接下来应该通过它生成一个Instance，也即对象，这就是object\_new的作用。

```
Object *object_new(const char *typename)
{
    TypeImpl *ti = type_get_by_name(typename);

    return object_new_with_type(ti);
}

static Object *object_new_with_type(Type type)
{
    Object *obj;
    type_initialize(type);
    obj = g_malloc(type->instance_size);
    object_initialize_with_type(obj, type->instance_size, type);
    obj->free = g_free;

    return obj;
}

```

object\_new中，TypeImpl的instance\_init会被调用，创建一个对象。current\_machine就是这个对象，它的类型是MachineState。

至此，绕了这么大一圈，有关体系结构的对象才创建完毕，接下来很多的设备的初始化，包括CPU和内存的初始化，都是围绕着体系结构的对象来的，后面我们会常常看到current\_machine。

## 总结时刻

这一节，我们学到，虚拟机对于设备的模拟是一件非常复杂的事情，需要用复杂的参数模拟各种各样的设备。为了能够适配这些设备，qemu定义了自己的模块管理机制，只有了解了这种机制，后面看每一种设备的虚拟化的时候，才有一个整体的思路。

这里的MachineClass是我们遇到的第一个，我们需要掌握它里面各种定义之间的关系。

![](https://static001.geekbang.org/resource/image/07/30/078dc698ef1b3df93ee9569e55ea2f30.png?wh=2308*2053)

每个模块都会有一个定义TypeInfo，会通过type\_init变为全局的TypeImpl。TypeInfo以及生成的TypeImpl有以下成员：

- name表示当前类型的名称
- parent表示父类的名称
- class\_init用于将TypeImpl初始化为MachineClass
- instance\_init用于将MachineClass初始化为MachineState

所以，以后遇到任何一个类型的时候，将父类和子类之间的关系，以及对应的初始化函数都要看好，这样就一目了然了。

## 课堂练习

你可能会问，这么复杂的qemu命令，我是怎么找到的，当然不是我一个字一个字打的，这是著名的云平台管理软件OpenStack创建虚拟机的时候自动生成的命令行。所以，给你留一道课堂练习题，请你看一下OpenStack的基本原理，看它是通过什么工具来管理如此复杂的命令行的。

欢迎留言和我分享你的疑惑和见解，也欢迎可以收藏本节内容，反复研读。你也可以把今天的内容分享给你的朋友，和他一起学习和进步。