你好，我是郭朝斌。

作为RISC-V开发板动手实践的第一讲，我们从智能灯的嵌入式开发开始吧。

智能灯硬件最重要的功能是控制LED灯的颜色和开关，这就涉及到PWM信号的生成和继电器的控制。之前我们是使用Python语言在NodeMCU开发板上实现的。那么，这些功能如何在RISC-V芯片上，使用C语言实现呢？

别着急，我来一步一步地讲解一下。

## 开发板介绍

[上一讲](https://time.geekbang.org/column/article/506337) 已经提到，我们使用的开发板是平头哥（T-Head）公司设计开发的RVB2601 开发板。主控芯片代号是CH2601，它基于平头哥开源的玄铁E906处理器内核IP设计开发，具体的指令集架构是RV32IMACX。

根据上节学到的RISC-V指令集知识，你可以知道这代表它采用 RISC-V 32bit 基本整数指令子集，并且包含整数乘法与除法指令子集，不可中断指令（也称作存储器原子操作指令）子集，压缩指令子集，这些标准扩展指令集。

其中，压缩指令子集对于嵌入式芯片非常重要，它可用于提高代码密度，节省存储成本。最后的代号"X"表示玄铁E906自定义的一些扩展指令集，这也是RISC-V指令集架构可扩展性的体现。

说了这么多，我们来看一下RVB2601开发板的实物图。

![](https://static001.geekbang.org/resource/image/d2/54/d29e903c981408b36f8785da9a3acf54.jpg?wh=1144x605)

作为一款嵌入式系统开发板，RVB2601在用户交互体验上下了一番功夫，提供了一块OLED屏幕，两个MIC输入，一个扬声器，一个三色LED灯，还有两个实体按键。基于这些器件，你可以直接动手实验很多有趣的应用。

更重要的是，这些外围器件都是通过跳线帽与主控芯片CH2601的I/O接口相连的，这就是说我们可以把跳线帽去掉，将我们自己的传感器、继电器等器件与芯片的I/O接口连接，开发我们的特定的应用。

当然，在这之前，我们需要先了解一下 RVB2601 开发板的I/O接口分布及功能。我绘制了一张I/O接口功能图，供你参考。 [官方文档](https://occ.t-head.cn/vendor/detail/index?id=3886757103532519424&key=download&module=4&vendorId=3706716635429273600) 中也有相关的描述，你也可以参考，但是介绍比较分散，你可能经常需要查看文档的多个位置来确认一个接口的功能。

![](https://static001.geekbang.org/resource/image/78/d8/788e31d927eea0a781d496c0d760ccd8.png?wh=1080x1440)

## 开发环境初体验

了解完硬件的基本情况，我们来看一下软件的开发工具和流程。

### 第一步 安装集成开发环境

平头哥提供了一个集成开发环境，名称是剑池CDK。在这个软件开发环境里，图形化的操作界面更利于我们使用。

不过，CDK只支持 Windows操作系统，如果你使用Mac电脑的话，可以像我一样使用 [VirtualBox](https://www.virtualbox.org/wiki/Downloads) 虚拟机软件，在Mac电脑上运行一个Windows虚拟机。VirtualBox是完全免费的，当然其他商用的虚拟机软件也可以使用。

### 第二步 程序开发

安装好IDE（集成开发环境）后，我们来创建一个工程项目。为了简便、快速地帮你理解，我们直接基于 IDE 提供的模版工程创建一个示例程序。

在IDE的欢迎页面中，点击右上角的“新建工程”

![](https://static001.geekbang.org/resource/image/4d/fd/4d83e3a12d9604750b8a582c69e003fd.png?wh=2458x110)

接着，你可以在新页面中找到顶部的搜索框，然后输入"ch2601"。

如果IDE没有显示欢迎页面，你可以点击工具栏右侧的平头哥Logo图标，重新打开欢迎页面。

![](https://static001.geekbang.org/resource/image/08/0f/08yy844c38f63afed903289305cff40f.png?wh=376x83)

点击搜索，你可以看到所有关于芯片CH2601的工程项目。

![](https://static001.geekbang.org/resource/image/81/df/81b4629c289e6c785d98d207f685a5df.png?wh=2478x1122)

我们选择与智能灯最接近的跑马灯项目作为模板。点击“ch2601\_marquee\_demo”条目右侧的“创建工程”。在弹出的“新建工程”窗口中，输入一个工程名称，比如“Led”，然后点击“确认”。

![](https://static001.geekbang.org/resource/image/30/06/30bdbc036c5ef4bc05f871c330d1be06.png?wh=444x324)

在IDE左侧，我们可以看到新建工程“Led”的工程结构：

- “app”目录中的文件是工程的应用代码。
- “.gdbinit”文件是GDB调试程序的初始化参数。
- “SConstruct”文件是 [Scons](https://scons.org) 软件构建工具的配置文件。
- “sdk\_chip\_ch2601”节点中是YOC平台相关的基础库。

### 第三步 编译

现在我们新建的Led工程中是跑马灯应用的完整代码。我们先不做任何修改，直接编译、运行一下。你可以点击工具栏中的编译图标，启动工程编译。

![](https://static001.geekbang.org/resource/image/93/76/93b5284be8646c42b6c93419fac6a376.png?wh=235x85)

或者从“Project”菜单中选择“Build Active Project”。

![](https://static001.geekbang.org/resource/image/ae/e8/aeda012d7f0c46d5ac66444e2f66f7e8.png?wh=486x486)

从这里我们也可以看出C语言和Python语言的不同， **C语言开发的代码在运行之前必须先进行编译，生成机器指令，而在这个过程中，编译器可以提前发现语法错误等。**

### 第四步 烧录

接着，我们需要将编译生成的固件文件烧录到开发板中。RVB开发板是通过JTAG接口来完成固件烧录的。你需要使用USB连接线把电脑与开发板的JTAG接口相连，然后点击工具栏中的烧录图标。

![](https://static001.geekbang.org/resource/image/99/55/9989201a40eb9db047bea7803080e155.png?wh=372x136)

### 第五步 运行

烧录完成后，你需要按一下开发板上的RST按键，重置RVB2601开发板。这时就可以看到开发板上的LED灯开始三种颜色交替点亮、熄灭。

这里提醒一下，如果LED灯的闪烁不正确，你需要查看一下开发板上PA7、PA25和PA4的跳线帽安装位置是否正确。我收到的开发板上，PA7一开始没有安装跳线帽，就导致了LED灯的红色状态不工作。

## 智能灯的开发

接下来，我们开始智能灯的开发。

LED模块和继电器仍然使用我们之前实验中使用的器件。如果你是第一次接触这个实验，或者之前的器件已经不知道跑到哪里去了，也可以参考 [这份文档](https://shimo.im/sheets/D3VVPdwcYRhhQRXh/MODOC) 自行采购相关硬件。

至于电路连接图，你可以参考下图。

![](https://static001.geekbang.org/resource/image/4d/1f/4d9d6cb1004d2b262efae194901ae11f.png?wh=1920x1080)

这里需要注意的是，最初，开发板上的J1扩展接口的15和16位、J3扩展接口的3和4位、J3扩展接口的5和6位、J3扩展接口的7和8位，还有J4扩展接口的15和16位是安装着跳线帽的，你在接线时需要把这些跳线帽去掉。

### PWM信号生成

在本实验中，LED模块的发光原理依然是PWM，忘记的同学可以回去 [第17节](https://time.geekbang.org/column/article/322528) 复习一下。LED灯的代码如下，供你参考。

```c++

/*********************
 *      INCLUDES
 *********************/
#define _DEFAULT_SOURCE /* needed for usleep() */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <aos/aos.h>
#include "app_config.h"
#include "app_init.h"
#include "csi_config.h"
#include "hw_config.h"

#include "board_config.h"
#include "drv/gpio_pin.h"
#include <drv/pin.h>
#include <drv/pwm.h>

#ifdef CONFIG_PWM_MODE

static uint32_t g_ctr = 0;
static csi_pwm_t  r;

void led_pinmux_init()
{
        //7
    csi_error_t ret;
    csi_pin_set_mux(PA7, PA7_PWM_CH7);
    csi_pin_set_mux(PA25, PA25_PWM_CH2);
    csi_pin_set_mux(PA4, PA4_PWM_CH4);

    ret = csi_pwm_init(&r, 0);
    if (ret != CSI_OK) {
            printf("===%s, %d\n", __FUNCTION__, __LINE__);
            return ;
    }
}

void rgb_light(uint32_t red, uint32_t green, uint32_t blue)
{
	csi_error_t ret;
	ret = csi_pwm_out_config(&r, 7 / 2, 300, red*300/255, PWM_POLARITY_HIGH);
    if (ret != CSI_OK) {
            printf("===%s, %d\n", __FUNCTION__, __LINE__);
            return ;
    }
    ret = csi_pwm_out_start(&r, 7 / 2);
    if (ret != CSI_OK) {
            printf("===%s, %d\n", __FUNCTION__, __LINE__);
            return ;
    }
        //25
    ret = csi_pwm_out_config(&r, 2 / 2, 300, green*300/255, PWM_POLARITY_HIGH);
    if (ret != CSI_OK) {
            printf("===%s, %d\n", __FUNCTION__, __LINE__);
            return ;
    }
    ret = csi_pwm_out_start(&r, 2 / 2);
    if (ret != CSI_OK) {
            printf("===%s, %d\n", __FUNCTION__, __LINE__);
            return ;
    }
        //4
    ret = csi_pwm_out_config(&r, 4 / 2, 300, blue*300/255, PWM_POLARITY_HIGH);
    if (ret != CSI_OK) {
            printf("===%s, %d\n", __FUNCTION__, __LINE__);
            return ;
    }
    ret = csi_pwm_out_start(&r, 4 / 2);
    if (ret != CSI_OK) {
            printf("===%s, %d\n", __FUNCTION__, __LINE__);
            return ;
    }
}
#endif

#ifdef CONFIG_GPIO_MODE
static uint32_t g_ctr = 0;
static csi_gpio_pin_t r;
static csi_gpio_pin_t g;
static csi_gpio_pin_t b;
void led_pinmux_init()
{
    csi_pin_set_mux(PA7, PIN_FUNC_GPIO);
    csi_pin_set_mux(PA25, PIN_FUNC_GPIO);
    csi_pin_set_mux(PA4, PIN_FUNC_GPIO);
    csi_gpio_pin_init(&r, PA7);
    csi_gpio_pin_dir(&r, GPIO_DIRECTION_OUTPUT);
	csi_gpio_pin_mode(&r, GPIO_MODE_PUSH_PULL);
    csi_gpio_pin_init(&g, PA25);
    csi_gpio_pin_dir(&g, GPIO_DIRECTION_OUTPUT);
	csi_gpio_pin_mode(&g, GPIO_MODE_PUSH_PULL);
    csi_gpio_pin_init(&b, PA4);
    csi_gpio_pin_dir(&b, GPIO_DIRECTION_OUTPUT);
	csi_gpio_pin_mode(&b, GPIO_MODE_PUSH_PULL);
    g_ctr = 0;
}

//fake rgb, because of only high or low state of gpio
void rgb_light(uint32_t red, uint32_t green, uint32_t blue)
{
	(red < 50)?csi_gpio_pin_write(&r, GPIO_PIN_LOW):csi_gpio_pin_write(&r, GPIO_PIN_HIGH);
	(green < 50)?csi_gpio_pin_write(&r, GPIO_PIN_LOW):csi_gpio_pin_write(&g, GPIO_PIN_HIGH);
	(blue < 50)?csi_gpio_pin_write(&r, GPIO_PIN_LOW):csi_gpio_pin_write(&b, GPIO_PIN_HIGH);
}
#endif

```

在代码中，我们主要使用了 CSI 接口规范中的相关接口函数，你可以参考 [接口规范文档](https://yoc.docs.t-head.cn/yocbook/Chapter3-AliOS/CSI%E8%AE%BE%E5%A4%87%E9%A9%B1%E5%8A%A8%E6%8E%A5%E5%8F%A3/CSI2/PWM.html) 进一步了解具体细节。

比对规范文档，你可能会有一个疑问：接口PA7、PA25和PA4对应的PWM输出接口编号分别是CH7、CH2和CH4，为什么接口函数csi\_pwm\_out\_config和csi\_pwm\_out\_start的channel（通道号）入参中填写的是编号除以2的得数取整，而不是编号本身呢？

这涉及到CH2601芯片对于PWM的内部具体设计。

CH2601芯片内部有6个PWM发生器，对应着编号0～5的通道。每个PWM发生器对应2个输出接口，这两个接口的PWM信号波形是完全一致的。通道编号与输出接口的具体关系如下表。

![](https://static001.geekbang.org/resource/image/f8/de/f87bfc6865170163f964c9740937c2de.jpg?wh=1280x534)

从表格中，你可以直观地看到PWM输出接口编号数字需要除以2，并取整，才可以得到PWM的通道编号。这就是上面代码处理方式的来源。

另外，在上面表格中，我还列出了PWM通道对应的GPIO接口。这是为了方便你在以后的应用中选择合适的PWM接口。比如，在本实验的智能灯应用中，我们需要三个独立的PWM通道来控制LED模块的R、G、B接口，那么我们就不能选择表格里面同一格的多个GPIO接口。显然，我们选择的PA7、PA25和PA4是满足这个原则的。

同时，我也使用GPIO的高低电平模式实现了LED模块的控制逻辑，便于你对比两种方式的异同。

### 继电器的控制

接下来我们看继电器控制的部分是怎么实现的。继电器的驱动同样是通过GPIO口，通过输出高低电平，实现它的通断控制。代码如下。

```c++
/*********************
 *      INCLUDES
 *********************/
#define _DEFAULT_SOURCE /* needed for usleep() */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <aos/aos.h>
#include "app_config.h"
#include "app_init.h"
#include "csi_config.h"
#include "hw_config.h"

#include "board_config.h"
#include "drv/gpio_pin.h"
#include <drv/pin.h>

static csi_gpio_pin_t relay;

void relay_pinmux_init()
{
	csi_error_t ret;
	csi_pin_set_mux(PA26, PIN_FUNC_GPIO);
	csi_gpio_pin_init(&relay, PA26);
    csi_gpio_pin_dir(&relay, GPIO_DIRECTION_OUTPUT);
}

void relay_toggle(bool on)
{
	if(on)
	{
		csi_gpio_pin_write(&relay, GPIO_PIN_HIGH);
	}
	else
	{
		csi_gpio_pin_write(&relay, GPIO_PIN_LOW);
	}
}

```

### 主逻辑编写

最后是程序的主逻辑。我们需要先初始化LED模块和继电器使用的I/O接口，然后调用LED代码的接口，点亮LED灯。在主循环中，我们周期性地打开、关闭继电器，实现LED灯闪烁的效果。

注：其中lv和oled开头的函数，是显示屏相关的代码。你暂时不需要关心它们，我会在后面的实验中详细讲解。

```c++

/*********************
 *      INCLUDES
 *********************/
#define _DEFAULT_SOURCE /* needed for usleep() */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <aos/aos.h>
#include "aos/cli.h"

#include "app_config.h"
#include "app_init.h"
#include "csi_config.h"
#include "hw_config.h"
#include "lvgl.h"
#include "lv_label.h"
#include "oled.h"

#include "board_config.h"
#include "drv/gpio_pin.h"
#include <drv/pin.h>
#include <drv/pwm.h>

/*********************
 *      DEFINES
 *********************/
#define TAG "app"

/**********************
 *      TYPEDEFS
 **********************/

/**********************
 *  STATIC PROTOTYPES
 **********************/
static void led_task(void *arg);

/**********************
 *  STATIC VARIABLES
 **********************/

/**********************
 *      MACROS
 **********************/

/**********************
 *   GLOBAL FUNCTIONS
 **********************/

volatile uint32_t g_debug = 0;
volatile uint32_t g_debug_v = 0;

#include "csi_core.h"
/**
 * main
 */
int main(void)
{
    board_yoc_init();

    printf("===%s, %d\n", __FUNCTION__, __LINE__);
    printf("===%s, %d\n", __FUNCTION__, __LINE__);
    aos_task_new("demo", led_task, NULL, 10 * 1024);
    return 0;
}

static void lable_test(void)
{
    lv_obj_t *p = lv_label_create(lv_scr_act(), NULL);
    lv_label_set_long_mode(p, LV_LABEL_LONG_BREAK);
    lv_label_set_align(p, LV_LABEL_ALIGN_CENTER);
    lv_obj_set_pos(p, 0, 4);
    lv_obj_set_size(p, 128, 60);
    lv_label_set_text(p, "THEAD\nMARQUEE\nDEMO");
}

static void led_task(void *arg)
{
    lv_init();
    oled_init();
    lable_test();
    led_pinmux_init();
	relay_pinmux_init();
	rgb_light(255,255,0);

    while (1)
    {
		relay_toggle(true);
        lv_task_handler();
        udelay(1000 * 1000);
        lv_tick_inc(1);
        relay_toggle(false);
		udelay(1000 * 1000);
    }
}

```

## 云上实验室

如果你暂时没有RVB2601开发板，是不是就只能干看了呢？我发现有一个备选方案可以让你体验一下RVB2601开发板，甚至其他型号的RISC-V芯片的开发板：你可以访问平头哥开发者社区提供的 [“云上实验室”](https://occ.t-head.cn/community/cloudlab/home) 服务。

具体怎么做呢？

首先，在云上实验室页面的筛选条件区域中，直接选择“开发板型号”为 RVB2601，如图所示，你可以看到可供申请的所有开发板。然后点击“申请评估”，可以看到这个开发板可供选择的空闲日期。你可以根据自己的需求，选择一个合适的时间区间进行申请。

![](https://static001.geekbang.org/resource/image/95/33/9575a76093f380d38620b290dd878233.png?wh=2448x1246)

当申请通过后，你会收到一条短信提醒。这时，打开云上实验室页面中“我的设备”标签，就可以看到可以使用的开发板了。

![](https://static001.geekbang.org/resource/image/f0/fb/f0199d684b8a89e371472df0c2a9f6fb.png?wh=834x636)

点击“进入云评估”，你会进入评估控制台，页面中有详细的使用介绍。

除了体验平台提供的几个demo程序，我们也可以尝试修改一下代码来运行。比如在ch2601\_gui\_demo 的程序，尝试修改一下屏幕显示的文字。命令可参考图片。

![](https://static001.geekbang.org/resource/image/41/a2/41f6294796420f35aee97455f4f354a2.png?wh=1614x96)

我改为了下图的内容：

![](https://static001.geekbang.org/resource/image/ea/96/ea1523b3e3319d6f64d3b4224b0b3f96.png?wh=1376x1084)

然后，在 Host Terminal 命令行输入 make all 编译固件。

![](https://static001.geekbang.org/resource/image/6f/d3/6fd2c9188f1842yy5b1d1637d76dbcd3.png?wh=1620x56)

接着，输入 make flashall 烧录固件文件到开发板中。

![](https://static001.geekbang.org/resource/image/c7/a2/c7ed4ea4e8e470d1ac8d84016e70b6a2.png?wh=1690x54)

最终的运行情况，我们可以通过摄像头来查看。

![](https://static001.geekbang.org/resource/image/c3/c5/c34a27b31d1277fbbbc0d2b55f2e38c5.png?wh=1006x792)

## 小结

到这里，我们已经熟悉了RVB2601开发板的开发环境，并且完成了智能灯的硬件搭建和嵌入式软件开发。

你可以看到，当面对一个新的芯片和新的开发板时，我们需要根据GPIO接口的功能来选择合适的接口，比如选择具备PWM功能的接口连接LED模块的R、G、B通道。

针对RVB2601开发板，PWM输出接口的选择还需要注意一个点——通道（Channel）的选择。CH0/CH1、CH2/CH3、CH4/CH5、CH6/CH7、CH8/CH9和CH10/CH11分别对应编号0～5的6个PWM通道。

另外，因为现在的实验使用C语言，嵌入式系统应用的开发步骤与之前使用Python语言是不同的，包括下图所示的步骤。

![](https://static001.geekbang.org/resource/image/50/01/50a9822f97e0ec7a92078bd27yy5f501.png?wh=2046x286)

如果你暂时没有开发板，可以申请体验一下云上实验室。除了可以像我上面提到的那样修改代码来运行，我还推荐你来动手实践一下Linux环境下的开发工具 [YocTools](https://yoc.docs.t-head.cn/yocbook/Chapter2-%E5%BF%AB%E9%80%9F%E4%B8%8A%E6%89%8B%E6%8C%87%E5%BC%95/YocTools.html) 的使用方法。

## 思考题

最后，我想提出一个挑战，当你完成本节的实验后，是否可以为开发板上自带的用户按键开发代码，实现按键控制继电器通断的功能呢？

欢迎你在评论区分享自己的挑战成果。基于你完成的智能灯，下一节中，我将介绍一下连接物联网平台，并实现联网控制的方法。同时，也欢迎你把今天的内容分享给你的朋友，一起来“极客”一把。