你好，我是姚秋辰。

上节课我们落地了一套Seata AT方案，要我说呢，AT绝对是最省心的分布式事务方案，一个注解搞定一切。今天这节课，我们来加一点难度，从Easy模式直接拉到Hard模式，看一个巨复杂的分布式事务方案：Seata TCC。

说TCC复杂，那是相对于AT来讲的。在AT模式下，你通过一个注解就能搞定所有事情，不需要对业务层代码进行任何修改。TCC难就难在它的实现方式上，它是一个基于“补偿模式”的解决方案。补偿的意思就是，你需要通过编写业务逻辑代码实现事务控制。

那TCC是如何通过代码来控制事务状态的呢？这就要说到TCC的三阶段事务模型了。

## TCC事务模型

TCC名字里这三个字母分别是三个单词的首字母缩写，从前到后分别是Try、Confirm和Cancel，这三个单词分别对应了TCC模式的三个执行阶段，每一个阶段都是独立的本地事务。

![图片](https://static001.geekbang.org/resource/image/70/ec/700119981d8a5bf14843d35c4b03ecec.jpg?wh=1920x559)

Try阶段完成的工作是 **预定操作资源（Prepare），** 说白了就是“占座”的意思，在正式开始执行业务逻辑之前，先把要操作的资源占上座。

Confirm阶段完成的工作是 **执行主要业务逻辑（Commit）**，它类似于事务的Commit操作。在这个阶段中，你可以对Try阶段锁定的资源进行各种CRUD操作。如果Confirm阶段被成功执行，就宣告当前分支事务提交成功。

Cancel阶段的工作是 **事务回滚（Rollback），** 它类似于事务的Rollback操作。在这个阶段中，你可没有AT方案的undo\_log帮你做自动回滚，你需要通过业务代码，对Confirm阶段执行的操作进行人工回滚。

我用一个考研占座的例子帮你理解TCC的工作流程。话说学校有一个专给考研学生准备的不打烊的考研复习教室，一座难求。如果你想要用TCC的方式坐定一个位子，那么第一步就是要执行Try操作，比如往座位上放上一块板砖，那这个座位就被你预定住了，后面来的人发现座位上面有块砖就去找其他座位了。第二步是Confirm阶段，这时候需要把板砖拿走，然后本尊坐在位子上，到这里TCC事务就算成功执行了。

如果Try阶段无法锁定资源，或者Confirm阶段发生异常，那么整个全局事务就会回滚，这就触发了第三步Cancel，你需要对Try步骤中锁定的资源进行释放，于是乎，这块砖在Cancel阶段被移走了，座位回到了TCC执行前的状态。

从这个例子可以看出，TCC的每一个步骤都需要你通过执行业务代码来实现。那接下来，让我带你去实战项目中落地一个简单的TCC案例，近距离感受下Hard模式的开发体验。

## 实现TCC

这次我们依然选择优惠券模板删除这个场景作为TCC的落地案例，我将在上节课的AT模式的基础之上，对Template服务做一番改造，将deleteTemplate接口改造为TCC风格。

前面咱提到过，TCC是由Try-Confirm-Cancel三个部分组成的，这三个部分怎么来定义呢？我先来写一个TCC风格的接口，你一看就明白了。

### 注册TCC接口

为了方便你阅读代码，我在Template服务里单独定义了一个新的接口，取名为CouponTemplateServiceTCC，它继承了CouponTemplateService这个接口。

```plain
@LocalTCC
public interface CouponTemplateServiceTCC extends CouponTemplateService {

    @TwoPhaseBusinessAction(
            name = "deleteTemplateTCC",
            commitMethod = "deleteTemplateCommit",
            rollbackMethod = "deleteTemplateCancel"
    )
    void deleteTemplateTCC(@BusinessActionContextParameter(paramName = "id") Long id);

    void deleteTemplateCommit(BusinessActionContext context);

    void deleteTemplateCancel(BusinessActionContext context);
}

```

在这段代码中，我使用了两个TCC的核心注解：LocalTCC和TwoPhaseBusinessAction。

其中@LocalTCC注解被用来修饰实现了二阶段提交的本地TCC接口，而@TwoPhaseBusinessAction注解标识当前方法使用TCC模式管理事务提交。

在TwoPhaseBusinessAction注解内，我通过name属性给当前事务注册了一个全局唯一的TCC bean name，然后分别使用commitMethod和rollbackMethod指定了它在Confirm阶段和Cancel阶段所要执行的方法。Try阶段所要执行的方法，便是被@TwoPhaseBusinessAction所修饰的deleteTemplateTCC方法了。

你一定注意到了我在deleteTemplateCommit和deleteTemplateCancel这两个方法中使用了一个特殊的入参BusinessActionContext，你可以使用它传递查询参数。在TCC模式下，查询参数将作为BusinessActionContext的一部分，在事务上下文中进行传递。

如果你对TCC注解的底层源码感兴趣，我推荐你从GlobalTransactionScanner这个类的wrapIfNecessary方法开始研究。它通过TCCBeanParserUtils工具类来判断当前资源是否为TCC的实现类，如果是TCC自动代理的话，就生成一个TccActionInterceptor作为当前bean对象的事务拦截器。

```plain
if (TCCBeanParserUtils.isTccAutoProxy(bean, beanName, applicationContext)) {
    //TCC interceptor, proxy bean of sofa:reference/dubbo:reference, and LocalTCC
    interceptor = new TccActionInterceptor(TCCBeanParserUtils.getRemotingDesc(beanName));
}

```

接口定义完成后，我们将CouponTemplateServiceImpl的接口类指向刚定义好的CouponTemplateServiceTCC方法，接下来就可以写具体实现了，按照TCC三阶段的顺序，我们先从一阶段Prepare写起。

### 编写一阶段Prepare逻辑

在一阶段Prepare的过程中，我们执行的是Try逻辑，它的目标是“锁定”优惠券模板资源。为了达成这个目标，我们需要对coupon\_template数据库做一个小修改，引入一个名为locked的变量，用来标记当前资源是否被锁定。你可以直接执行下面的SQL语句添加这个属性。

```plain
alter table coupon_template
   add locked tinyint(1) default 0 null;

```

在CouponTemplate类中，我们也要加上locked属性。

```plain
@Column(name = "locked", nullable = false)
private Boolean locked;

```

有了locked字段，我们就可以在Try阶段借助它来锁定券模板了。我们先来看一下简化版的资源锁定代码吧。

```plain
@Override
@Transactional
public void deleteTemplateTCC(Long id) {
    CouponTemplate filter = CouponTemplate.builder()
            .available(true)
            .locked(false)
            .id(id)
            .build();

    CouponTemplate template = templateDao.findAll(Example.of(filter))
            .stream().findFirst()
            .orElseThrow(() -> new RuntimeException("Template Not Found"));

    template.setLocked(true);
    templateDao.save(template);
}

```

在这段代码中，我在通过ID查找优惠券的同时，添加了两个查询限定条件来筛选未被锁定且状态为available的券模板。如果查到了符合条件的记录，我会将其locked状态置为true。

在正式的线上业务中，Try方法的资源锁定逻辑会更加复杂。我举一个例子，就拿转账来说吧，如果张三要向李四转账30元，在TCC模式下这30元会被“锁定”并计入冻结金额中，我们在“锁定”资源的同时还需要记录是“谁”冻结了这部分金额。比如你可以在生成锁定记录的时候将转账交易号也一并记下来，这个交易号就是我们前面说的那个“谁”，这样你就知道这些金额是被哪笔交易锁定的了。这样一来，当你执行回滚逻辑将金额从“冻结余额”里释放的时候，就不会错误地释放其他转账请求锁定的金额了。

接下来我们去看下二阶段Commit的执行逻辑。

### 编写二阶段Commit逻辑

二阶段Commit就是TCC中的Confirm阶段，只要TCC框架执行到了Commit逻辑，那么就代表各个分支事务已经成功执行了Try逻辑。我们在Commit阶段执行的是主体业务逻辑，即删除优惠券，但是别忘了你还要将Try阶段的资源锁定解除掉。

在下面的代码中，我们放心大胆地直接读取了指定ID的优惠券，不用担心ID不存在，因为ID不存在的话，在Try阶段就会抛出异常，TCC会转而执行Rollback方法，压根进不到Commit阶段。读取到Template对象之后，我们分别设置locked=false，available=true。

```plain
@Override
@Transactional
public void deleteTemplateCommit(BusinessActionContext context) {
    Long id = Long.parseLong(context.getActionContext("id").toString());

    CouponTemplate template = templateDao.findById(id).get();

    template.setLocked(false);
    template.setAvailable(false);
    templateDao.save(template);

    log.info("TCC committed");
}

```

现在你已经完成了二阶段Commit，最后让我们来编写Rollback的逻辑吧。

### 编写二阶段Rollback逻辑

二阶段Rollback对应的是TCC中的Cancel阶段，如果在Try或者Confirm阶段发生了异常，就会触发TCC全局事务回滚，Seata Server会将Rollback指令发送给每一个分支事务。

在下面这段简化的Rollback代码中，我们读取了Template对象，并通过将locked设置为false的方式对资源进行解锁。

```plain
@Override
@Transactional
public void deleteTemplateCancel(BusinessActionContext context) {
    Long id = Long.parseLong(context.getActionContext("id").toString());
    Optional<CouponTemplate> templateOption = templateDao.findById(id);

    if (templateOption.isPresent()) {
        CouponTemplate template = templateOption.get();
        template.setLocked(false);
        templateDao.save(template);
    }
    log.info("TCC cancel");
}

```

在线上业务中，Cancel方法只能释放由当前TCC事务在Try阶段锁定的资源，这就要求你在Try阶段记录资源锁定方的信息，并在Confirm和Cancel段逻对这个信息进行判断。

你知道为什么我在Cancel里特意加了一段逻辑，判断Template是否存在吗？这就要提到TCC的空回滚了。

### TCC空回滚

所谓空回滚，是在没有执行Try方法的情况下，TC下发了回滚指令并执行了Cancel逻辑。

那么在什么情况下会出现空回滚呢？比如某个分支事务的一阶段Try方法因为网络不可用发生了Timeout异常，或者Try阶段执行失败，这时候TM端会判定全局事务回滚，TC端向各个分支事务发送Cancel指令，这就产生了一次空回滚。

处理空回滚的正确的做法是，在Cancel阶段，你应当先判断一阶段Try有没有执行成功。示例程序中的判断方式比较简单，我先是判断资源是否已经被锁定，再执行释放操作。如果资源未被锁定或者压根不存在，你可以认为Try阶段没有执行成功，这时在Cancel阶段直接返回成功即可。

更为完善的一种做法是，引入独立的事务控制表，在Try阶段中将XID和分支事务ID落表保存，如果Cancel阶段查不到事务控制记录，那么就说明Try阶段未被执行。同理，Cancel阶段执行成功后，也可以在事务控制表中记录回滚状态，这样做是为了防止另一个TCC的坑，“倒悬”。

### TCC倒悬

倒悬又被叫做“悬挂”，它是指TCC三个阶段没有按照先后顺序执行。我们就拿刚讲过的空回滚的例子来说吧，如果Try方法因为网络问题卡在了网关层，导致锁定资源超时，这时Cancel阶段执行了一次空回滚，到目前为止一切正常。但回滚之后，原先超时的Try方法经过网关层的重试，又被后台服务接收到了，这就产生了一次倒悬场景，即一阶段Try在二阶段回滚之后被触发。

在倒悬的情况下，整个事务已经被全局回滚，那么如果你再执行一次Try操作，当前资源将被长期锁定，这就造成了一种类似死锁的局面。解法很简单，你可以利用事务控制表记录二阶段执行状态，并在Try阶段中检查该状态，如果二阶段回滚完毕，那么就直接跳过一阶段Try。

到这里，我们就落地了一套TCC业务，下面让我们来回顾下这节课的重要内容吧。

## 总结

TCC相比于AT而言，代码开发量至少要double，它以开发量为代价，换取了事务的高度可控性。不过我仍然不建议头脑一热就上TCC方案，因为TCC非常考验开发团队对业务的理解深度，为什么这样说呢？一个重要原因是，你需要把串行的业务逻辑拆分成Try-Confirm-Cancel三个不同的阶段执行，如何设计资源的锁定流程、如果不同资源间有关联性又怎么锁定、回滚的反向补偿逻辑等等，你需要对业务流程的每一个步骤了如指掌，才能设计出高效的TCC流程。

还有需要特别注意的一点是幂等性，接口幂等性是保证数据一致性的重要前提。在大厂中通常有框架层面的幂等组件，或者幂等性服务供你调用，对于中小业务来说，通过本地事务控制表来确保幂等性是一种简单有效的低成本方案。

## 思考题

通过这两节课我们落地了AT和TCC方案，Seata里还有一个SAGA方案，你能举一反三自选SAGA并落地几个小demo吗？

到这里，我们就学完了这个专栏的最后一节正课内容。欢迎你把这个专栏分享给更多对Spring Cloud感兴趣的朋友。我是姚秋辰，我们结束语再见！