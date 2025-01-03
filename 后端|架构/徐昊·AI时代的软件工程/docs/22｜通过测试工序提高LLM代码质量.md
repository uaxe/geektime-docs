你好，我是徐昊，今天我们来继续学习AI时代的软件工程。

上节课，我们讲解了如何将架构模式转化为测试工序，以及工序在架构落地过程中发挥的作用。测试工序有助于将抽象的架构设计转化为具体的开发任务和实际的工作流程，帮助团队有效地实现架构设计，并最终产生质量高、可靠性强的软件系统。

同样，通过测试工序，我们也可以让LLM帮助我们有效地实现架构设计，并提高LLM生成代码的质量。这节课我们就讨论一下如何实现这个目标。

## 将工序转化为提示词模版

首先，我们需要将测试工序转化为CoT（Chain of Thought），通过CoT指导LLM按照测试工序的要求，将给定的需求功能拆分成对应的任务列表。

这里我们使用的测试工序仍然是前面提到的那一个：

![](https://static001.geekbang.org/resource/image/26/ee/26e48c8fc6ca29b39eb57366dbb42fee.jpg?wh=1833x932)

我们将架构组件中的三种不同的组件分别进行测试，其中Persistent层中的组件，使用假对象（Fake，内存数据库）作为测试替身。而HTTP interface和Application Logic层则通过存根（Stub）作为测试替身。最后，再通过功能测试，对整个系统进行验证。

那么让我们来构造CoT的提示词模板：

```plain
架构描述
=======
当前系统技术栈为Spring Boot，Jersey和MyBatis。

当前系统采用典型的三层架构设计，分别为:
- HTTP interface层，负责提供RESTful API，命名规则为XXXAPI，比如OrdersAPI；
  - API通过JAX-RS的Resource实现；
  - HTTP interface层调用Application Logic层的Service，完成功能；
- Application Logic层，负责提供核心逻辑，命名规则为XXXService，比如OrderService；
  - 使用Java实现，Service使用POJO为主的领域对象；
  - Application Logic层调用Persistent层的DAO完成对于数据的访问；
- Persistent层，负责与持久化数据交互，命名规则为XXXDAO，比如OrderDAO；
  - 使用Java实现，DAO使用DTO为主的数据对象；
  - DAO通过MyBatis的Mapper实现

工序说明
=======
  - 如果功能要求使用到HTTP interface层，那么：
     - 使用Application Logic层中对应Service的Stub作为测试替身；
     - 列出需求描述的场景使用到HTTP interface组件的功能（HTTP interface层目标功能）；
     - 列出“HTTP interface层目标功能”需要测试的场景（HTTP层目标场景）；

  - 如果功能要求使用到Application Logic层，那么：
     - 使用Persistent层中对应DAO的Stub作为测试替身；
     - 列出需求描述的场景使用到Application Logic组件的功能（Application Logic层目标功能）；
     - 列出“Application Logic层目标功能”要测试的场景（Application Logic层目标场景）；

  - 如果功能要求使用到Persistent层，那么：
     - 使用H2数据库作为fake implementation；
     - 列出需求描述的场景使用到Persistent组件的功能（Persistent层目标功能）；
     - 列出“Persistent层目标功能”要测试的场景（Persistent层目标场景）；

功能需求
=======
{functionalities}

任务
====
首先，列出每一个验收场景以及对应的测试数据；
然后，针对每一个验收场景，按照架构描述和工序说明的指引，列出任务列表。

```

当我们针对列出所有商品的功能使用这个模板时，可以得到以下的回答：

![](https://static001.geekbang.org/resource/image/a2/fc/a2c27e002fd44786ccdfc248a012fefc.jpg?wh=1070x2109)

可以看到，虽然这个任务列表稍显粗略，但是对于任务的划分，的确是按照我们给定的工序进行的。在获得任务列表之后，我们可以围绕任务列表的指引，让LLM帮助我们完成代码的编写，这里我只展示对于测试代码的编写：

```plain
请按照任务列表，编写http interface层的测试代码

```

![](https://static001.geekbang.org/resource/image/2e/38/2e1699bc68fe93eed6a8ef8f8d3a4638.jpg?wh=1658x239)

```plain
import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import javax.ws.rs.core.Response;
import org.junit.Before;
import org.junit.Test;

public class ProductsAPITest {
  private ProductsAPI productsAPI;

  private OrderService orderServiceMock;

  @Before
  public void setUp() {
    // 创建 OrderService 的 Mock 对象
    orderServiceMock = mock(OrderService.class);
    // 初始化 ProductsAPI 并注入 Mock 对象
    productsAPI = new ProductsAPI(orderServiceMock);
  }

  @Test
  public void testGetProductCatalogList() {
    // 模拟 OrderService 返回的产品目录列表
    List<ProductCatalog> mockProductCatalogList = new ArrayList<>();
    // 添加一些测试数据
    mockProductCatalogList.add(new ProductCatalog("1", "Product 1"));
    mockProductCatalogList.add(new ProductCatalog("2", "Product 2"));
    // 当调用 orderServiceMock 的方法时，返回模拟的产品目录列表
    when(orderServiceMock.getProductCatalogList()).thenReturn(mockProductCatalogList);
    // 发送获取产品目录列表的请求
    Response response = productsAPI.getProductCatalogList();
    // 验证响应状态码是否为 200 OK
    assertEquals(Response.Status.OK.getStatusCode(), response.getStatus());
    // 验证响应内容是否与模拟数据一致
    List<ProductCatalog> actualProductCatalogList = (List<ProductCatalog>) response.getEntity();
    assertEquals(mockProductCatalogList.size(), actualProductCatalogList.size());
    for (int i = 0; i < mockProductCatalogList.size(); i++) {
      assertEquals(mockProductCatalogList.get(i).getId(), actualProductCatalogList.get(i).getId());
      assertEquals(mockProductCatalogList.get(i).getName(), actualProductCatalogList.get(i).getName());
    }
  }

  @Test
  public void testGetEmptyProductCatalogList() {
    // 模拟 OrderService 返回空的产品目录列表
    List<ProductCatalog> emptyProductCatalogList = new ArrayList<>();
    // 当调用 orderServiceMock 的方法时，返回空的产品目录列表
    when(orderServiceMock.getProductCatalogList()).thenReturn(emptyProductCatalogList);
    // 发送获取产品目录列表的请求
    Response response = productsAPI.getProductCatalogList();
    // 验证响应状态码是否为 200 OK
    assertEquals(Response.Status.OK.getStatusCode(), response.getStatus());
    // 验证响应内容是否为空列表
    List<ProductCatalog> actualProductCatalogList = (List<ProductCatalog>) response.getEntity();
    assertEquals(0, actualProductCatalogList.size());
  }
}

```

![](https://static001.geekbang.org/resource/image/df/d9/df259706632f7b8bccb32ff5399417d9.jpg?wh=1598x337)

```plain
请按照任务列表，编写application logic层的测试代码

```

![](https://static001.geekbang.org/resource/image/2a/6a/2a60080f07f7319df2d0d61de5e3516a.jpg?wh=1696x229)

```plain
import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import java.util.ArrayList;
import java.util.List;
import org.junit.Before;
import org.junit.Test;

public class OrderServiceTest {
  private OrderService orderService;
  private OrderDAO orderDAOMock;

  @Before
  public void setUp() {
    // 创建 OrderDAO 的 Mock 对象
    orderDAOMock = mock(OrderDAO.class);
    // 初始化 OrderService 并注入 Mock 对象
    orderService = new OrderService(orderDAOMock);
  }

  @Test
  public void testGetProductCatalogList() {
    // 模拟 OrderDAO 返回的产品目录列表
    List<ProductCatalog> mockProductCatalogList = new ArrayList<>();
    // 添加一些测试数据
    mockProductCatalogList.add(new ProductCatalog("1", "Product 1"));
    mockProductCatalogList.add(new ProductCatalog("2", "Product 2"));
    // 当调用 orderDAOMock 的方法时，返回模拟的产品目录列表
    when(orderDAOMock.getProductCatalogList()).thenReturn(mockProductCatalogList);
    // 调用 OrderService 的方法获取产品目录列表
    List<ProductCatalog> actualProductCatalogList = orderService.getProductCatalogList();
    // 验证返回的产品目录列表是否与模拟数据一致
    assertEquals(mockProductCatalogList.size(), actualProductCatalogList.size());
    for (int i = 0; i < mockProductCatalogList.size(); i++) {
      assertEquals(mockProductCatalogList.get(i).getId(), actualProductCatalogList.get(i).getId());
      assertEquals(mockProductCatalogList.get(i).getName(), actualProductCatalogList.get(i).getName());
    }
  }

  @Test
  public void testGetEmptyProductCatalogList() {
    // 模拟 OrderDAO 返回空的产品目录列表
    List<ProductCatalog> emptyProductCatalogList = new ArrayList<>();
    // 当调用 orderDAOMock 的方法时，返回空的产品目录列表
    when(orderDAOMock.getProductCatalogList()).thenReturn(emptyProductCatalogList);
    // 调用 OrderService 的方法获取产品目录列表
    List<ProductCatalog> actualProductCatalogList = orderService.getProductCatalogList();
    // 验证返回的产品目录列表是否为空列表
    assertEquals(0, actualProductCatalogList.size());
  }
}

```

![](https://static001.geekbang.org/resource/image/56/b3/563d5ba66376967c6a4e9414bd46a5b3.jpg?wh=1640x330)

```plain
请按照任务列表，编写persistent层的测试代码

```

![](https://static001.geekbang.org/resource/image/6f/69/6f03b6b550f58122625365f6c7d33169.jpg?wh=1708x262)

```plain
import static org.junit.Assert.assertEquals;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

public class OrderDAOTest {
  private static final String DB_URL = "jdbc:h2:mem:test;DB_CLOSE_DELAY=-1";
  private static final String DB_USER = "sa";
  private static final String DB_PASSWORD = "";
  private OrderDAO orderDAO;

  @Before
  public void setUp() throws SQLException {
    // 初始化并创建内存数据库表
    createTable();
    // 初始化 OrderDAO
    orderDAO = new OrderDAO(DB_URL, DB_USER, DB_PASSWORD);
  }

  @After
  public void tearDown() throws SQLException {
    // 删除内存数据库表
    dropTable();
  }

  @Test
  public void testGetProductCatalogList() throws SQLException {
    // 插入测试数据到内存数据库
    insertTestData();
    // 调用 OrderDAO 的方法获取产品目录列表
    List<ProductCatalog> productCatalogList = orderDAO.getProductCatalogList();
    // 验证返回的产品目录列表是否与预期一致
    assertEquals(2, productCatalogList.size());
    assertEquals("1", productCatalogList.get(0).getId());
    assertEquals("Product 1", productCatalogList.get(0).getName());
    assertEquals("2", productCatalogList.get(1).getId());
    assertEquals("Product 2", productCatalogList.get(1).getName());
  }

  private void createTable() throws SQLException {
    try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
      Statement stmt = conn.createStatement()) {
      stmt.execute("CREATE TABLE product_catalog (id VARCHAR(50), name VARCHAR(100))");
    }
  }

  private void dropTable() throws SQLException {
    try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
      Statement stmt = conn.createStatement()) {
      stmt.execute("DROP TABLE product_catalog");
    }
  }

  private void insertTestData() throws SQLException {
    try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
      Statement stmt = conn.createStatement()) {
      stmt.execute("INSERT INTO product_catalog VALUES ('1', 'Product 1')");
      stmt.execute("INSERT INTO product_catalog VALUES ('2', 'Product 2')");
    }
  }
}

```

![](https://static001.geekbang.org/resource/image/30/7c/303f6c0e47f068917cd63a60ef68297c.jpg?wh=1580x291)

请注意观察，上述代码中对于测试策略的应用，是符合我们对于测试工序的描述的。在确认测试代码没有问题之后，我们就可以通过与LLM的交互配合，完成生产代码的编写。这个在前面的课程里已经给过了例子，就不再重复了。

## 将测试工序模版化

对于简单的场景，我们通过CoT化的测试工序，就足以应对了。但是如果工序本身就有很多细节，需要更多的指导时，我们要怎么办呢？这时候，我们可以为这样的测试工序提供独立的提示词模板。

比如，对于Persistent层的测试工序，我们希望使用flyway，在测试开始之前完成对于schema的灌注。那么我们可以提供一个独立的测试工序提示词模板：

```plain
技术要求
=======
使用H2数据库作为fake implementation；
在所有测试开始之前，使用flyway db构建表结构；
在所有测试结束后，清空数据库；

需求
====
{requirements}

任务列表
====
{task list}

任务
===
按照任务列表，符合技术要求，编写测试代码

```

![](https://static001.geekbang.org/resource/image/ff/32/ffb73ccb52c6689c13b099df6051d232.jpg?wh=1620x214)

```plain
import org.flywaydb.core.Flyway;
import org.h2.jdbcx.JdbcDataSource;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import static org.junit.Assert.assertEquals;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;

public class OrderDAOTest {
  private static JdbcDataSource dataSource;

  private static OrderDAO orderDAO;

  @BeforeClass
  public static void setupDatabase() throws SQLException {
    // 设置H2数据库
    dataSource = new JdbcDataSource();
    dataSource.setURL("jdbc:h2:mem:test;DB_CLOSE_DELAY=-1");
    // 运行Flyway来创建表结构
    Flyway flyway = Flyway.configure().dataSource(dataSource).load();
    flyway.migrate();
    // 初始化OrderDAO
    orderDAO = new OrderDAO(dataSource);
  }

  @AfterClass
  public static void tearDownDatabase() throws SQLException {
    // 清空数据库
    try (Connection conn = dataSource.getConnection();
      Statement stmt = conn.createStatement()) {
      stmt.executeUpdate("DROP ALL OBJECTS DELETE FILES");
    }
  }

  @Test
  public void testGetProductCatalogWhenNotEmpty() {
    // 插入一些测试数据
    insertTestDataIntoDatabase();
    // 测试获取产品目录列表
    assertEquals(2, orderDAO.getProductCatalog().size());
  }

  @Test
  public void testGetProductCatalogWhenEmpty() {
    // 测试空产品目录列表情况
    assertEquals(0, orderDAO.getProductCatalog().size());
  }

  private void insertTestDataIntoDatabase() {
    // 在数据库中插入一些测试数据
    // 这里可以使用任何测试数据来模拟实际场景
    // 由于这里只是示例，我将简单地插入两条数据作为示例
    // 实际项目中应该根据需要插入更多的测试数据
    try (Connection conn = dataSource.getConnection();
      Statement stmt = conn.createStatement()) {
      stmt.executeUpdate("INSERT INTO product_catalog (id, name) VALUES (1, 'Product 1')");
      stmt.executeUpdate("INSERT INTO product_catalog (id, name) VALUES (2, 'Product 2')");
    } catch (SQLException e) {
      e.printStackTrace();
    }
  }
}

```

![](https://static001.geekbang.org/resource/image/e9/a3/e947eb686851666b85f8cb239c6904a3.jpg?wh=1536x271)

需要注意的是，在这个提示词模版中，我们需要填入 **需求** 和 **任务列表** 这两个上下文。从而保证CoT的提示词模板和具体测试工序的提示词模板，在上下文中是统一的。在得到上面的回答时，我分别填入的上下文是：

```plain
验收场景及测试数据
		用户请求获取产品目录列表：
请求：GET /products/catalog
预期响应：200 OK
测试数据：无
		空产品目录列表情况下的响应：
请求：GET /products/catalog
预期响应：200 OK，空列表
测试数据：空的产品目录列表

```

```plain
用户请求获取产品目录列表：
  创建名为 OrderDAO 的 DAO 类。
  实现方法用于从数据库中获取产品目录列表。
  创建 H2 数据库作为 fake implementation。
  编写 SQL 查询以获取产品目录列表。
  返回查询结果，如果为空则返回空列表。

```

## 小结

当然，另一个做法是，在得到任务列表之后。与LLM交互，进入到某个测试工序时，将该工序的技术要求直接贴到LLM的对话中，比如前面用到持久层工序的时候，我们可以直接这样来写：

```plain
请按照任务列表，编写persistent层的测试代码。请注意，要符合下列技术要求

技术要求
=======
使用H2数据库作为fake implementation；
在所有测试开始之前，使用flyway db构建表结构；
在所有测试结束后，清空数据库；

```

这样可以避免需要人工传递上下文的问题。我不建议在CoT模版中放入太多的具体工序细节，这是因为以目前（2024年3月）LLM的能力，当工序细节过多时，它会遗漏一些细节。而独立的测试工序模版，可以帮助我们更好地发现这些细节。

除此之外，另一个使用独立测试工序模版的好处是，更容易过渡到大模型驱动的自主代理架构（LLM based Autonomous Agent）。

![](https://static001.geekbang.org/resource/image/a5/88/a51a7885590830fbe08a4da55b22d088.jpg?wh=2000x1078)

这种由一个Agent控制任务列表，并调用其他Agent完成具体工作的架构，非常类似于最近（2024年3月）火热的Devin。而在crewAI等框架的帮助下，获得一个更加精准的、也符合我们架构要求的“定制版Devin”，成本是非常低的。我们只要梳理清楚与架构对应的测试工序即可。

## 思考题

请修改本文中的样例工序，并调整CoT模版，生成符合工序要求的任务列表。

欢迎在留言区分享你的想法，我会让编辑置顶一些优质回答供大家学习讨论。