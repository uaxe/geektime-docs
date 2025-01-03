你好，我是徐昊，今天我们来继续学习AI时代的软件工程。

上节课，我们讲解了如何利用架构划分功能上下文，以及如何为不同的架构组件，选择恰当的测试替身技术（Test Double），从而构造恰当的测试策略。

那么构建了测试策略之后，对于我们使用大语言模型（Large Language Model）生成代码有什么帮助呢？那么今天就让我们来看一看。

## 按照测试策略构造提示词模板

我们仍然使用上节课的例子，在上节课的讨论中，我们最后得到的测试策略是这样的：

![](https://static001.geekbang.org/resource/image/bc/9a/bca7e85d866338a5bea5f974b3b1129a.jpg?wh=1920x1054)

也就是说，我们将架构中的三种不同的组件分别进行测试，其中Persistent层中的组件，使用假对象（Fake，内存数据库）作为测试替身。而HTTP interface和Application Logic层则通过存根（Stub）作为测试替身。最后，再通过功能测试，对整个系统进行验证。

接下来让我们按照测试策略，针对不同的组件构造提示词模板（Prompting template）。我们先从Persistent层开始：

> 架构描述
>
> =======
>
> 当前系统技术栈为Spring Boot，Jersey和MyBatis。
>
> 当前系统采用典型的三层架构设计，分布为:
>
> \- HTTP interface层，负责提供RESTful API，命名规则为XXXAPI，比如OrdersAPI；
>
> – Application Logic层，负责提供核心逻辑，命名规则为XXXService，比如OrderService；
>
> – Persistent层，负责与持久化数据交互，命名规则为XXXDAO，比如OrderDAO；
>
> – DAO通过MyBatis的Mapper实现
>
> – 在对DAO进行测试时，使用H2数据库作为fake implementation，也就是在测试中，初始化H2数据库，然后保证应用程序链接到这个数据库，并在测试结束后销毁这个数据库。
>
> 功能需求
>
> =======
>
> {functionalities}
>
> 任务
>
> ====
>
> 上面功能需求描述的场景，在Persistent层中需要哪些组件（目标组件）；
>
> 列出需求描述的场景使用到目标组件的功能（目标功能）；
>
> 列出目标功能需要测试的场景。描述场景，并给出相关的测试数据。

注意在这个提示词模板中，我们并没有直接要求LLM帮助我们生成代码，还是与之前一样，先让LLM给出场景和测试数据。ChatGPT的答案如下：

![](https://static001.geekbang.org/resource/image/26/c5/26ca0258d837ab21e0e1d93687dffac5.jpg?wh=1558x1507)

在这个提示词模板中，使用了另一个我发明的小技巧，叫 **代词消除，** 可以在上下文中去除隐含的歧义。通过目标组件和目标功能的明确指示，我们可以确保LLM在后续交互中保持上下文连贯。

随后，我们就可以要求LLM帮助我们生成测试代码：

> 请按照指定技术栈，为目标功能场景提供测试代码

LLM给出的结果是：

![](https://static001.geekbang.org/resource/image/c1/ed/c13f524d4a4a579e0a84431b5e28f1ed.jpg?wh=1900x343)

```plain
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mybatis.spring.boot.test.autoconfigure.MybatisTest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

@SpringBootTest
@MybatisTest
@TestPropertySource(locations = "classpath:application-test.properties") // 使用测试配置文件
public class ProductDAOTest {

  @Autowired
  private DataSource dataSource;

  @Autowired
  private ProductDAO productDAO;
  private Connection connection;

  @BeforeEach
  public void setUp() throws SQLException {
    // 获取H2数据库连接
    connection = dataSource.getConnection();
    // 创建测试表
    try (Statement statement = connection.createStatement()) {
      statement.executeUpdate("CREATE TABLE Product (product_id INT PRIMARY KEY, name VARCHAR(255), description VARCHAR(255), price DECIMAL(10,2))");
      // 插入测试数据
      statement.executeUpdate("INSERT INTO Product (product_id, name, description, price) VALUES (1, 'Product 1', 'Description of Product 1', 19.99)");
      statement.executeUpdate("INSERT INTO Product (product_id, name, description, price) VALUES (2, 'Product 2', 'Description of Product 2', 29.99)");
      statement.executeUpdate("INSERT INTO Product (product_id, name, description, price) VALUES (3, 'Product 3', 'Description of Product 3', 39.99)");
    }
  }

  @Test
  public void testGetAllProducts() {
    // 调用被测试的方法
    List<Product> products = productDAO.getAllProducts();
    // 验证结果
    assertEquals(3, products.size());
    assertTrue(products.stream().anyMatch(p -> p.getProductId() == 1 && p.getName().equals("Product 1")));
    assertTrue(products.stream().anyMatch(p -> p.getProductId() == 2 && p.getName().equals("Product 2")));
    assertTrue(products.stream().anyMatch(p -> p.getProductId() == 3 && p.getName().equals("Product 3")));
  }

  @AfterEach
  public void tearDown() throws SQLException {
    // 删除测试表并关闭连接
    try (Statement statement = connection.createStatement()) {
      statement.executeUpdate("DROP TABLE IF EXISTS Product");
    }
    if (connection != null) {
      connection.close();
    }
  }
}

```

![](https://static001.geekbang.org/resource/image/5e/10/5eda253f8d2e914134c76d90214d7410.jpg?wh=1568x899)

接下来，我们进一步要求LLM给出application-test.properties的具体配置，也可以让LLM帮助我们补全一些其他的细节。现在也可以直接让LLM帮助我们生成代码。

> 请给出ProductDAO的实现

![](https://static001.geekbang.org/resource/image/1c/e4/1c281a71613deaa13b460fd08de346e4.jpg?wh=1920x1977)

对于现在这个简单的例子，这个代码也就足够了。接下来，我们可以补充提示词模板中关于HTTP Interface部分的架构描述，并更改任务描述：

> 架构描述
>
> =======
>
> 当前系统技术栈为Spring Boot，Jersey和MyBatis。
>
> 当前系统采用典型的三层架构设计，分布为:
>
> \- HTTP interface层，负责提供RESTful API，命名规则为XXXAPI，比如OrdersAPI；
>
> \- API通过JAX-RS的Resource实现
>
> \- 在对API进行测试时，首先要stub掉Application Logic层中的Services，然后再使用JerseyTest对API进行测试
>
> \- Application Logic层，负责提供核心逻辑，命名规则为XXXService，比如OrderService；
>
> \- Persistent层，负责与持久化数据交互，命名规则为XXXDAO，比如OrderDAO；
>
> \- DAO通过MyBatis的Mapper实现
>
> \- 在对DAO进行测试时，使用H2数据库作为fake implementation，也就是在测试中，初始化H2数据库，然后保证应用程序链接到这个数据库，并在测试结束后销毁这个数据库。
>
> 功能需求
>
> =======
>
> {functionalities}
>
> 任务
>
> ====
>
> 上面功能需求描述的场景，在HTTP Interface层中需要哪些组件（目标组件）；
>
> 列出需求描述的场景使用到目标组件的功能（目标功能）；
>
> 列出目标功能需要测试的场景。描述场景，并给出相关的测试数据。

ChatGPT的答案如下：

![](https://static001.geekbang.org/resource/image/1a/32/1a4b9yydeda811ebb5a2067504ccbb32.jpg?wh=2040x3230)

> 请按照指定技术栈，为目标功能场景提供测试代码

![](https://static001.geekbang.org/resource/image/14/96/14307a022d4497709246bca613aba596.jpg?wh=2020x340)

```plain
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import java.util.List;
import javax.ws.rs.client.Entity;
import javax.ws.rs.client.Invocation;
import javax.ws.rs.core.Application;
import javax.ws.rs.core.GenericType;
import javax.ws.rs.core.Response;
import org.glassfish.jersey.server.ResourceConfig;
import org.glassfish.jersey.test.JerseyTest;
import org.junit.Test;

public class OrdersAPITest extends JerseyTest {

  @Override
  protected Application configure() {
    return new ResourceConfig(OrdersAPI.class);
  }

  @Test
  public void testGetAllProducts() {
    // 发送GET请求到/products端点
    Response response = target("/products").request().get();
    // 确保响应状态码为200
    assertEquals(Response.Status.OK.getStatusCode(), response.getStatus());
    // 从响应中获取产品目录列表
    List<Product> productList = response.readEntity(new GenericType<List<Product>>() {});
    // 确保产品目录列表不为空
    assertNotNull(productList);
    // 检查第一个产品的信息
    Product firstProduct = productList.get(0);
    assertEquals(1, firstProduct.getId());
    assertEquals("Product 1", firstProduct.getName());
    assertEquals("Description of Product 1", firstProduct.getDescription());
    assertEquals(10.99, firstProduct.getPrice(), 0.001);
    // 可以继续检查其他产品信息...
  }
}

```

![](https://static001.geekbang.org/resource/image/96/89/96ecae0a2c69cff4a7b32df225eae389.jpg?wh=1531x854)

还剩下一个Application Logic层，做法大同小异，我给你留作课后作业自行练习。

## 使用LLM构造功能测试

按照我们之前讨论的测试策略，我们已经使用LLM完成了三个Q1象限的测试。在测试策略中，除去Q1象限之外，我们还有Q2象限的功能测试。现在来构造提示词模板，完成这个Q2的测试。需要注意的是，为了测试的可重复性，我们会在功能测试中，完成测试数据的灌入。

首先给出任务描述：

> 架构描述
>
> =======
>
> 当前系统采用典型的三层架构设计，分布为:
>
> HTTP interface层，负责提供RESTful API，命名规则为XXXAPI，比如OrdersAPI；
>
> Application Logic层，负责提供核心逻辑，命名规则为XXXService，比如OrderService；
>
> Persistent层，负责与持久化数据交互，命名规则为XXXDAO，比如OrderDAO；
>
> 当前系统技术栈为Spring Boot、Jersery和MyBatis
>
> 当为当前系统生成功能测试时，我们使用Http Client通过访问API完成真正的测试。但是为了保证测试的可重复性，我们在setup测试的时候，链接数据库，完成测试数据的准备。测试时，使用MySQL数据库。
>
> 功能需求
>
> =======
>
> 目前为一个电子商务系统。需要列出所有产品的目录
>
> 任务
>
> ====
>
> 上面功能需求描述的场景，需要用到哪些API（目标API）；
>
> 列出需求描述的场景使用到目标API的功能（目标功能）；
>
> 列出目标功能需要测试的场景。描述场景，并给出相关的测试数据。

![](https://static001.geekbang.org/resource/image/81/96/81c5834f92yy5f86c1dfda4b31108a96.jpg?wh=2020x4841)

接着要求GPT提供测试，返回结果如下。

> 请为目标功能测试场景提供测试

![](https://static001.geekbang.org/resource/image/f4/7a/f4987c62ef310af18e4cb6e724e5b77a.jpg?wh=2020x1645)

```plain
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.web.server.LocalServerPort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import static org.junit.jupiter.api.Assertions.assertEquals;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class ProductAPITest {
  @LocalServerPort
  private int port;

  @Autowired
  private RestTemplate restTemplate;

  private Connection connection;

  @BeforeEach
  public void setUp() throws SQLException {
    // 连接测试用MySQL数据库，准备测试数据
    connection = DriverManager.getConnection("jdbc:mysql://localhost:3306/test_db", "username", "password");
    Statement statement = connection.createStatement();
    statement.executeUpdate("INSERT INTO products (product_id, product_name, category) VALUES (1, 'Laptop', 'Electronics')");
    statement.executeUpdate("INSERT INTO products (product_id, product_name, category) VALUES (2, 'Smartphone', 'Electronics')");
    statement.executeUpdate("INSERT INTO products (product_id, product_name, category) VALUES (3, 'Bookshelf', 'Furniture')");
    statement.executeUpdate("INSERT INTO products (product_id, product_name, category) VALUES (4, 'Office Chair', 'Furniture')");
    statement.executeUpdate("INSERT INTO products (product_id, product_name, category) VALUES (5, 'T-shirt', 'Clothing')");
  }

  @AfterEach
  public void tearDown() throws SQLException {
    // 清除测试数据库中的数据
    Statement statement = connection.createStatement();
    statement.executeUpdate("DELETE FROM products");
    connection.close();
  }

  @Test
  public void testListAllProducts() {
    // 发送GET请求到API端点
    ResponseEntity<String> responseEntity = restTemplate.getForEntity("http://localhost:" + port + "/products", String.class);
    // 验证响应状态码为200
    assertEquals(HttpStatus.OK, responseEntity.getStatusCode());
    // 验证响应内容是否符合预期
    String expectedResponseBody = "[{\"productId\":1,\"productName\":\"Laptop\",\"category\":\"Electronics\"}," +
        "{\"productId\":2,\"productName\":\"Smartphone\",\"category\":\"Electronics\"}," +
        "{\"productId\":3,\"productName\":\"Bookshelf\",\"category\":\"Furniture\"}," +
        "{\"productId\":4,\"productName\":\"Office Chair\",\"category\":\"Furniture\"}," +
        "{\"productId\":5,\"productName\":\"T-shirt\",\"category\":\"Clothing\"}]";
    assertEquals(expectedResponseBody, responseEntity.getBody());
  }
}

```

![](https://static001.geekbang.org/resource/image/fa/d0/fae21bd4393191ea5e3b8bbfebbe8ed0.jpg?wh=2020x616)

## 小结

至此，我们按照测试策略的指导，遵循前面讲过的测试驱动开发的节奏，完成了一个简单的功能。那么这么做有什么用处呢？最显而易见的用处是， **针对存量系统，我们可以由测试策略切入，让LLM生成符合我们要求的代码**。

所谓存量系统，就是指不是全部由LLM/AI主导生成的代码库。在这样的代码库中，组织结构已经存在，LLM生成的代码需要符合既定的结构，才能被引入代码库中。

那么通过这节课我们所介绍的方法，我们就可以在任何代码库中，随时引入LLM的辅助了。

## 思考题

请完成Application Layer的架构说明，并使用LLM完成代码生成。

欢迎在留言区分享你的想法，我会让编辑置顶一些优质回答供大家学习讨论。