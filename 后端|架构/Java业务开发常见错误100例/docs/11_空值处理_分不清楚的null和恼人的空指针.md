你好，我是朱晔。今天，我要和你分享的主题是，空值处理：分不清楚的null和恼人的空指针。

有一天我收到一条短信，内容是“尊敬的null你好，XXX”。当时我就笑了，这是程序员都能Get的笑点，程序没有获取到我的姓名，然后把空格式化为了null。很明显，这是没处理好null。哪怕把null替换为贵宾、顾客，也不会引发这样的笑话。

程序中的变量是null，就意味着它没有引用指向或者说没有指针。这时，我们对这个变量进行任何操作，都必然会引发空指针异常，在Java中就是NullPointerException。那么，空指针异常容易在哪些情况下出现，又应该如何修复呢？

空指针异常虽然恼人但好在容易定位，更麻烦的是要弄清楚null的含义。比如，客户端给服务端的一个数据是null，那么其意图到底是给一个空值，还是没提供值呢？再比如，数据库中字段的NULL值，是否有特殊的含义呢，针对数据库中的NULL值，写SQL需要特别注意什么呢？

今天，就让我们带着这些问题开始null的踩坑之旅吧。

## 修复和定位恼人的空指针问题

**NullPointerException是Java代码中最常见的异常，我将其最可能出现的场景归为以下5种**：

- 参数值是Integer等包装类型，使用时因为自动拆箱出现了空指针异常；
- 字符串比较出现空指针异常；
- 诸如ConcurrentHashMap这样的容器不支持Key和Value为null，强行put null的Key或Value会出现空指针异常；
- A对象包含了B，在通过A对象的字段获得B之后，没有对字段判空就级联调用B的方法出现空指针异常；
- 方法或远程服务返回的List不是空而是null，没有进行判空就直接调用List的方法出现空指针异常。

为模拟说明这5种场景，我写了一个wrongMethod方法，并用一个wrong方法来调用它。wrong方法的入参test是一个由0和1构成的、长度为4的字符串，第几位设置为1就代表第几个参数为null，用来控制wrongMethod方法的4个入参，以模拟各种空指针情况：

```
private List<String> wrongMethod(FooService fooService, Integer i, String s, String t) {
    log.info("result {} {} {} {}", i + 1, s.equals("OK"), s.equals(t),
            new ConcurrentHashMap<String, String>().put(null, null));
    if (fooService.getBarService().bar().equals("OK"))
        log.info("OK");
    return null;
}

@GetMapping("wrong")
public int wrong(@RequestParam(value = "test", defaultValue = "1111") String test) {
    return wrongMethod(test.charAt(0) == '1' ? null : new FooService(),
            test.charAt(1) == '1' ? null : 1,
            test.charAt(2) == '1' ? null : "OK",
            test.charAt(3) == '1' ? null : "OK").size();
}

class FooService {
    @Getter
    private BarService barService;

}

class BarService {
    String bar() {
        return "OK";
    }
}

```

很明显，这个案例出现空指针异常是因为变量是一个空指针，尝试获得变量的值或访问变量的成员会获得空指针异常。但，这个异常的定位比较麻烦。

在测试方法wrongMethod中，我们通过一行日志记录的操作，在一行代码中模拟了4处空指针异常：

- 对入参Integer i进行+1操作；
- 对入参String s进行比较操作，判断内容是否等于"OK"；
- 对入参String s和入参String t进行比较操作，判断两者是否相等；
- 对new出来的ConcurrentHashMap进行put操作，Key和Value都设置为null。

输出的异常信息如下：

```
java.lang.NullPointerException: null
	at org.geekbang.time.commonmistakes.nullvalue.demo2.AvoidNullPointerExceptionController.wrongMethod(AvoidNullPointerExceptionController.java:37)
	at org.geekbang.time.commonmistakes.nullvalue.demo2.AvoidNullPointerExceptionController.wrong(AvoidNullPointerExceptionController.java:20)

```

这段信息确实提示了这行代码出现了空指针异常，但我们很难定位出到底是哪里出现了空指针，可能是把入参Integer拆箱为int的时候出现的，也可能是入参的两个字符串任意一个为null，也可能是因为把null加入了ConcurrentHashMap。

你可能会想到，要排查这样的问题，只要设置一个断点看一下入参即可。但，在真实的业务场景中，空指针问题往往是在特定的入参和代码分支下才会出现，本地难以重现。如果要排查生产上出现的空指针问题，设置代码断点不现实，通常是要么把代码进行拆分，要么增加更多的日志，但都比较麻烦。

在这里，我推荐使用阿里开源的Java故障诊断神器 [Arthas](https://alibaba.github.io/arthas/)。Arthas简单易用功能强大，可以定位出大多数的Java生产问题。

接下来，我就和你演示下如何在30秒内知道wrongMethod方法的入参，从而定位到空指针到底是哪个入参引起的。如下截图中有三个红框，我先和你分析第二和第三个红框：

- 第二个红框表示，Arthas启动后被附加到了JVM进程；
- 第三个红框表示，通过watch命令监控wrongMethod方法的入参。

![](https://static001.geekbang.org/resource/image/e2/6b/e2d39e5da91a8258c5aab3691e515c6b.png?wh=2194*1796)

watch命令的参数包括类名表达式、方法表达式和观察表达式。这里，我们设置观察类为AvoidNullPointerExceptionController，观察方法为wrongMethod，观察表达式为params表示观察入参：

```
watch org.geekbang.time.commonmistakes.nullvalue.demo2.AvoidNullPointerExceptionController wrongMethod params

```

开启watch后，执行2次wrong方法分别设置test入参为1111和1101，也就是第一次传入wrongMethod的4个参数都为null，第二次传入的第1、2和4个参数为null。

配合图中第一和第四个红框可以看到，第二次调用时，第三个参数是字符串OK其他参数是null，Archas正确输出了方法的所有入参，这样我们很容易就能定位到空指针的问题了。

到这里，如果是简单的业务逻辑的话，你就可以定位到空指针异常了；如果是分支复杂的业务逻辑，你需要再借助stack命令来查看wrongMethod方法的调用栈，并配合watch命令查看各方法的入参，就可以很方便地定位到空指针的根源了。

下图演示了通过stack命令观察wrongMethod的调用路径：

![](https://static001.geekbang.org/resource/image/6c/ef/6c9ac7f4345936ece0b0d31c1ad974ef.png?wh=2862*308)

如果你想了解Arthas各种命令的详细使用方法，可以 [点击](https://alibaba.github.io/arthas/commands.html) 这里查看。

接下来，我们看看如何修复上面出现的5种空指针异常。

其实，对于任何空指针异常的处理，最直白的方式是先判空后操作。不过，这只能让异常不再出现，我们还是要找到程序逻辑中出现的空指针究竟是来源于入参还是Bug：

- 如果是来源于入参，还要进一步分析入参是否合理等；
- 如果是来源于Bug，那空指针不一定是纯粹的程序Bug，可能还涉及业务属性和接口调用规范等。

在这里，因为是Demo，所以我们只考虑纯粹的空指针判空这种修复方式。如果要先判空后处理，大多数人会想到使用if-else代码块。但，这种方式既增加代码量又会降低易读性，我们可以尝试利用Java 8的Optional类来消除这样的if-else逻辑，使用一行代码进行判空和处理。

修复思路如下：

- 对于Integer的判空，可以使用Optional.ofNullable来构造一个Optional，然后使用orElse(0)把null替换为默认值再进行+1操作。
- 对于String和字面量的比较，可以把字面量放在前面，比如"OK".equals(s)，这样即使s是null也不会出现空指针异常；而对于两个可能为null的字符串变量的equals比较，可以使用Objects.equals，它会做判空处理。
- 对于ConcurrentHashMap，既然其Key和Value都不支持null，修复方式就是不要把null存进去。HashMap的Key和Value可以存入null，而ConcurrentHashMap看似是HashMap的线程安全版本，却不支持null值的Key和Value，这是容易产生误区的一个地方。
- 对于类似fooService.getBarService().bar().equals(“OK”)的级联调用，需要判空的地方有很多，包括fooService、getBarService()方法的返回值，以及bar方法返回的字符串。如果使用if-else来判空的话可能需要好几行代码，但使用Optional的话一行代码就够了。
- 对于rightMethod返回的List，由于不能确认其是否为null，所以在调用size方法获得列表大小之前，同样可以使用Optional.ofNullable包装一下返回值，然后通过.orElse(Collections.emptyList())实现在List为null的时候获得一个空的List，最后再调用size方法。

```
private List<String> rightMethod(FooService fooService, Integer i, String s, String t) {
    log.info("result {} {} {} {}", Optional.ofNullable(i).orElse(0) + 1, "OK".equals(s), Objects.equals(s, t), new HashMap<String, String>().put(null, null));
    Optional.ofNullable(fooService)
            .map(FooService::getBarService)
            .filter(barService -> "OK".equals(barService.bar()))
            .ifPresent(result -> log.info("OK"));
    return new ArrayList<>();
}

@GetMapping("right")
public int right(@RequestParam(value = "test", defaultValue = "1111") String test) {
    return Optional.ofNullable(rightMethod(test.charAt(0) == '1' ? null : new FooService(),
            test.charAt(1) == '1' ? null : 1,
            test.charAt(2) == '1' ? null : "OK",
            test.charAt(3) == '1' ? null : "OK"))
            .orElse(Collections.emptyList()).size();
}

```

经过修复后，调用right方法传入1111，也就是给rightMethod的4个参数都设置为null，日志中也看不到任何空指针异常了：

```
[21:43:40.619] [http-nio-45678-exec-2] [INFO ] [.AvoidNullPointerExceptionController:45  ] - result 1 false true null

```

但是，如果我们修改right方法入参为0000，即传给rightMethod方法的4个参数都不可能是null，最后日志中也无法出现OK字样。这又是为什么呢，BarService的bar方法不是返回了OK字符串吗？

我们还是用Arthas来定位问题，使用watch命令来观察方法rightMethod的入参，-x参数设置为2代表参数打印的深度为2层：

![](https://static001.geekbang.org/resource/image/0c/82/0ce3c96788f243791cbd512aecfa6382.png?wh=2404*460)

可以看到，FooService中的barService字段为null，这样也就可以理解为什么最终出现这个Bug了。

这又引申出一个问题， **使用判空方式或Optional方式来避免出现空指针异常，不一定是解决问题的最好方式，空指针没出现可能隐藏了更深的Bug**。因此，解决空指针异常，还是要真正case by case地定位分析案例，然后再去做判空处理，而处理时也并不只是判断非空然后进行正常业务流程这么简单，同样需要考虑为空的时候是应该出异常、设默认值还是记录日志等。

## POJO中属性的null到底代表了什么？

在我看来，相比判空避免空指针异常，更容易出错的是null的定位问题。对程序来说，null就是指针没有任何指向，而结合业务逻辑情况就复杂得多，我们需要考虑：

- DTO中字段的null到底意味着什么？是客户端没有传给我们这个信息吗？
- 既然空指针问题很讨厌，那么DTO中的字段要设置默认值么？
- 如果数据库实体中的字段有null，那么通过数据访问框架保存数据是否会覆盖数据库中的既有数据？

如果不能明确地回答这些问题，那么写出的程序逻辑很可能会混乱不堪。接下来，我们看一个实际案例吧。

有一个User的POJO，同时扮演DTO和数据库Entity角色，包含用户ID、姓名、昵称、年龄、注册时间等属性：

```
@Data
@Entity
public class User {
    @Id
    @GeneratedValue(strategy = IDENTITY)
    private Long id;
    private String name;
    private String nickname;
    private Integer age;
    private Date createDate = new Date();
}

```

有一个Post接口用于更新用户数据，更新逻辑非常简单，根据用户姓名自动设置一个昵称，昵称的规则是“用户类型+姓名”，然后直接把客户端在RequestBody中使用JSON传过来的User对象通过JPA更新到数据库中，最后返回保存到数据库的数据。

```
@Autowired
private UserRepository userRepository;

@PostMapping("wrong")
public User wrong(@RequestBody User user) {
    user.setNickname(String.format("guest%s", user.getName()));
    return userRepository.save(user);
}

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
}

```

首先，在数据库中初始化一个用户，age=36、name=zhuye、create\_date=2020年1月4日、nickname是NULL：

![](https://static001.geekbang.org/resource/image/de/67/de1bcb580ea63505a8e093c51c4cd567.png?wh=1004*128)

然后，使用cURL测试一下用户信息更新接口Post，传入一个id=1、name=null的JSON字符串，期望把ID为1的用户姓名设置为空：

```
curl -H "Content-Type:application/json" -X POST -d '{ "id":1, "name":null}' http://localhost:45678/pojonull/wrong

{"id":1,"name":null,"nickname":"guestnull","age":null,"createDate":"2020-01-05T02:01:03.784+0000"}%

```

接口返回的结果和数据库中记录一致：

![](https://static001.geekbang.org/resource/image/af/fd/af9c07a63ba837683ad059a6afcceafd.png?wh=1012*124)

可以看到，这里存在如下三个问题：

- 调用方只希望重置用户名，但age也被设置为了null；
- nickname是用户类型加姓名，name重置为null的话，访客用户的昵称应该是guest，而不是guestnull，重现了文首提到的那个笑点；
- 用户的创建时间原来是1月4日，更新了用户信息后变为了1月5日。

归根结底，这是如下5个方面的问题：

- 明确DTO中null的含义。 **对于JSON到DTO的反序列化过程，null的表达是有歧义的，客户端不传某个属性，或者传null，这个属性在DTO中都是null。** 但，对于用户信息更新操作，不传意味着客户端不需要更新这个属性，维持数据库原先的值；传了null，意味着客户端希望重置这个属性。因为Java中的null就是没有这个数据，无法区分这两种表达，所以本例中的age属性也被设置为了null，或许我们可以借助Optional来解决这个问题。
- **POJO中的字段有默认值。如果客户端不传值，就会赋值为默认值，导致创建时间也被更新到了数据库中。**
- **注意字符串格式化时可能会把null值格式化为null字符串。** 比如昵称的设置，我们只是进行了简单的字符串格式化，存入数据库变为了guestnull。显然，这是不合理的，也是开头我们说的笑话的来源，还需要进行判断。
- **DTO和Entity共用了一个POJO**。对于用户昵称的设置是程序控制的，我们不应该把它们暴露在DTO中，否则很容易把客户端随意设置的值更新到数据库中。此外，创建时间最好让数据库设置为当前时间，不用程序控制，可以通过在字段上设置columnDefinition来实现。
- **数据库字段允许保存null，会进一步增加出错的可能性和复杂度**。因为如果数据真正落地的时候也支持NULL的话，可能就有NULL、空字符串和字符串null三种状态。这一点我会在下一小节展开。如果所有属性都有默认值，问题会简单一点。

按照这个思路，我们对DTO和Entity进行拆分，修改后代码如下所示：

- UserDto中只保留id、name和age三个属性，且name和age使用Optional来包装，以区分客户端不传数据还是故意传null。
- 在UserEntity的字段上使用@Column注解，把数据库字段name、nickname、age和createDate都设置为NOT NULL，并设置createDate的默认值为CURRENT\_TIMESTAMP，由数据库来生成创建时间。
- 使用Hibernate的@DynamicUpdate注解实现更新SQL的动态生成，实现只更新修改后的字段，不过需要先查询一次实体，让Hibernate可以“跟踪”实体属性的当前状态，以确保有效。

```
@Data
public class UserDto {
    private Long id;
    private Optional<String> name;
    private Optional<Integer> age;
;

@Data
@Entity
@DynamicUpdate
public class UserEntity {
    @Id
    @GeneratedValue(strategy = IDENTITY)
    private Long id;
    @Column(nullable = false)
    private String name;
    @Column(nullable = false)
    private String nickname;
    @Column(nullable = false)
    private Integer age;
    @Column(nullable = false, columnDefinition = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    private Date createDate;
}

```

在重构了DTO和Entity后，我们重新定义一个right接口，以便对更新操作进行更精细化的处理。首先是参数校验：

- 对传入的UserDto和ID属性先判空，如果为空直接抛出IllegalArgumentException。
- 根据id从数据库中查询出实体后进行判空，如果为空直接抛出IllegalArgumentException。

然后，由于DTO中已经巧妙使用了Optional来区分客户端不传值和传null值，那么业务逻辑实现上就可以按照客户端的意图来分别实现逻辑。如果不传值，那么Optional本身为null，直接跳过Entity字段的更新即可，这样动态生成的SQL就不会包含这个列；如果传了值，那么进一步判断传的是不是null。

下面，我们根据业务需要分别对姓名、年龄和昵称进行更新：

- 对于姓名，我们认为客户端传null是希望把姓名重置为空，允许这样的操作，使用Optional的orElse方法一键把空转换为空字符串即可。
- 对于年龄，我们认为如果客户端希望更新年龄就必须传一个有效的年龄，年龄不存在重置操作，可以使用Optional的orElseThrow方法在值为空的时候抛出IllegalArgumentException。
- 对于昵称，因为数据库中姓名不可能为null，所以可以放心地把昵称设置为guest加上数据库取出来的姓名。

```
@PostMapping("right")
public UserEntity right(@RequestBody UserDto user) {
    if (user == null || user.getId() == null)
        throw new IllegalArgumentException("用户Id不能为空");

    UserEntity userEntity = userEntityRepository.findById(user.getId())
            .orElseThrow(() -> new IllegalArgumentException("用户不存在"));

    if (user.getName() != null) {
        userEntity.setName(user.getName().orElse(""));
    }
    userEntity.setNickname("guest" + userEntity.getName());
    if (user.getAge() != null) {
        userEntity.setAge(user.getAge().orElseThrow(() -> new IllegalArgumentException("年龄不能为空")));
    }
    return userEntityRepository.save(userEntity);
}

```

假设数据库中已经有这么一条记录，id=1、age=36、create\_date=2020年1月4日、name=zhuye、nickname=guestzhuye：

![](https://static001.geekbang.org/resource/image/5f/47/5f1d46ea87f37a570b32f94ac44ca947.png?wh=980*118)

使用相同的参数调用right接口，再来试试是否解决了所有问题。传入一个id=1、name=null的JSON字符串，期望把id为1的用户姓名设置为空：

```
curl -H "Content-Type:application/json" -X POST -d '{ "id":1, "name":null}' http://localhost:45678/pojonull/right

{"id":1,"name":"","nickname":"guest","age":36,"createDate":"2020-01-04T11:09:20.000+0000"}%

```

结果如下：

![](https://static001.geekbang.org/resource/image/a6/4a/a68db8e14e7dca3ff9b22e2348272a4a.png?wh=860*108)

可以看到，right接口完美实现了仅重置name属性的操作，昵称也不再有null字符串，年龄和创建时间字段也没被修改。

通过日志可以看到，Hibernate生成的SQL语句只更新了name和nickname两个字段：

```
Hibernate: update user_entity set name=?, nickname=? where id=?

```

接下来，为了测试使用Optional是否可以有效区分JSON中没传属性还是传了null，我们在JSON中设置了一个null的age，结果是正确得到了年龄不能为空的错误提示：

```
curl -H "Content-Type:application/json" -X POST -d '{ "id":1, "age":null}' http://localhost:45678/pojonull/right

{"timestamp":"2020-01-05T03:14:40.324+0000","status":500,"error":"Internal Server Error","message":"年龄不能为空","path":"/pojonull/right"}%

```

## 小心MySQL中有关NULL的三个坑

前面提到，数据库表字段允许存NULL除了会让我们困惑外，还容易有坑。这里我会结合NULL字段，和你着重说明sum函数、count函数，以及NULL值条件可能踩的坑。

为方便演示，首先定义一个只有id和score两个字段的实体：

```
@Entity
@Data
public class User {
    @Id
    @GeneratedValue(strategy = IDENTITY)
    private Long id;
    private Long score;
}

```

程序启动的时候，往实体初始化一条数据，其id是自增列自动设置的1，score是NULL：

```
@Autowired
private UserRepository userRepository;

@PostConstruct
public void init() {
    userRepository.save(new User());
}

```

然后，测试下面三个用例，来看看结合数据库中的null值可能会出现的坑：

- 通过sum函数统计一个只有NULL值的列的总和，比如SUM(score)；
- select记录数量，count使用一个允许NULL的字段，比如COUNT(score)；
- 使用=NULL条件查询字段值为NULL的记录，比如score=null条件。

```
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    @Query(nativeQuery=true,value = "SELECT SUM(score) FROM `user`")
    Long wrong1();
    @Query(nativeQuery = true, value = "SELECT COUNT(score) FROM `user`")
    Long wrong2();
    @Query(nativeQuery = true, value = "SELECT * FROM `user` WHERE score=null")
    List<User> wrong3();
}

```

得到的结果，分别是null、0和空List：

```
[11:38:50.137] [http-nio-45678-exec-1] [INFO ] [t.c.nullvalue.demo3.DbNullController:26  ] - result: null 0 []

```

显然，这三条SQL语句的执行结果和我们的期望不同：

- 虽然记录的score都是NULL，但sum的结果应该是0才对；
- 虽然这条记录的score是NULL，但记录总数应该是1才对；
- 使用=NULL并没有查询到id=1的记录，查询条件失效。

原因是：

- **MySQL中sum函数没统计到任何记录时，会返回null而不是0**，可以使用IFNULL函数把null转换为0；
- **MySQL中count字段不统计null值**，COUNT(\*)才是统计所有记录数量的正确方式。
- **MySQL中使用诸如=、<、>这样的算数比较操作符比较NULL的结果总是NULL**，这种比较就显得没有任何意义，需要使用IS NULL、IS NOT NULL或 ISNULL()函数来比较。

修改一下SQL：

```
@Query(nativeQuery = true, value = "SELECT IFNULL(SUM(score),0) FROM `user`")
Long right1();
@Query(nativeQuery = true, value = "SELECT COUNT(*) FROM `user`")
Long right2();
@Query(nativeQuery = true, value = "SELECT * FROM `user` WHERE score IS NULL")
List<User> right3();

```

可以得到三个正确结果，分别为0、1、\[User(id=1, score=null)\] ：

```
[14:50:35.768] [http-nio-45678-exec-1] [INFO ] [t.c.nullvalue.demo3.DbNullController:31  ] - result: 0 1 [User(id=1, score=null)]

```

## 重点回顾

今天，我和你讨论了做好空值处理需要注意的几个问题。

我首先总结了业务代码中5种最容易出现空指针异常的写法，以及相应的修复方式。针对判空，通过Optional配合Stream可以避免大多数冗长的if-else判空逻辑，实现一行代码优雅判空。另外，要定位和修复空指针异常，除了可以通过增加日志进行排查外，在生产上使用Arthas来查看方法的调用栈和入参会更快捷。

在我看来，业务系统最基本的标准是不能出现未处理的空指针异常，因为它往往代表了业务逻辑的中断，所以我建议每天查询一次生产日志来排查空指针异常，有条件的话建议订阅空指针异常报警，以便及时发现及时处理。

POJO中字段的null定位，从服务端的角度往往很难分清楚，到底是客户端希望忽略这个字段还是有意传了null，因此我们尝试用Optional类来区分null的定位。同时，为避免把空值更新到数据库中，可以实现动态SQL，只更新必要的字段。

最后，我分享了数据库字段使用NULL可能会带来的三个坑（包括sum函数、count函数，以及NULL值条件），以及解决方式。

总结来讲，null的正确处理以及避免空指针异常，绝不是判空这么简单，还要根据业务属性从前到后仔细考虑，客户端传入的null代表了什么，出现了null是否允许使用默认值替代，入库的时候应该传入null还是空值，并确保整个逻辑处理的一致性，才能尽量避免Bug。

为处理好null，作为客户端的开发者，需要和服务端对齐字段null的含义以及降级逻辑；而作为服务端的开发者，需要对入参进行前置判断，提前挡掉服务端不可接受的空值，同时在整个业务逻辑过程中进行完善的空值处理。

今天用到的代码，我都放在了GitHub上，你可以点击 [这个链接](https://github.com/JosephZhu1983/java-common-mistakes) 查看。

## 思考与讨论

1. ConcurrentHashMap的Key和Value都不能为null，而HashMap却可以，你知道这么设计的原因是什么吗？TreeMap、Hashtable等Map的Key和Value是否支持null呢？
2. 对于Hibernate框架可以使用@DynamicUpdate注解实现字段的动态更新，对于MyBatis框架如何实现类似的动态SQL功能，实现插入和修改SQL只包含POJO中的非空字段？

关于程序和数据库中的null、空指针问题，你还遇到过什么坑吗？我是朱晔，欢迎在评论区与我留言分享，也欢迎你把这篇文章分享给你的朋友或同事，一起交流。