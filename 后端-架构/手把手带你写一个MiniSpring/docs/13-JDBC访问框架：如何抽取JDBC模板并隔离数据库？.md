你好，我是郭屹，今天我们继续手写MiniSpring。从这节课开始我们进入MiniSpring一个全新的部分：JdbcTemplate。

到现在为止，我们的MiniSpring已经成了一个相对完整的简易容器，具备了基本的IoC和MVC功能。现在我们就要在这个简易容器的基础之上，继续添加新的特性。首先就是 **数据访问的特性**，这是任何一个应用系统的基本功能，所以我们先实现它。这之后，我们的MiniSpring就基本落地了，你真的可以以它为框架进行编程了。

我们还是先从标准的JDBC程序开始探讨。

## JDBC通用流程

在Java体系中，数据访问的规范是JDBC，也就是Java Database Connectivity，想必你已经熟悉或者至少听说过，一个简单而典型的JDBC程序大致流程是怎样的呢？我们一步步来看，每一步我也会给你放上一两个代码示例帮助你理解。

第一步，加载数据库驱动程序。

```plain
	Class.forName("com.microsoft.sqlserver.jdbc.SQLServerDriver");

```

或者直接new Driver();也可以。

这是第一步，因为JDBC只是提供了一个访问的API，具体访问数据库的工作是由不同厂商提供的数据库driver来实现的，Java只是规定了这个通用流程。对同一种数据库，可以有不同的driver，我们也可以自己按照协议实现一个driver，我自己就曾在1996年实现了中国第一个JDBC Driver。

这里我多提一句，Java的这种设计很是巧妙，让应用程序的API与对应厂商的SPI分隔开了，它们可以各自独立进化，这是通过一种叫“桥接模式”的办法达到的。这节课你就能切身感受到这种模式的应用效果了。

第二步，获取数据库连接。

```plain
	con = DriverManager.getConnection("jdbc:sqlserver://localhost:1433;databasename=DEMO;user=testuser;password=test;");

```

getConnection()方法的几个参数，分别表示数据库URL、登录数据库的用户名和密码。

这个时候，我们利用底层driver的功能建立了对数据库的连接。不过要注意了，建立和断开连接的过程是很费时间的，所以后面我们会利用数据库连接池技术来提高性能。

第三步，通过Connection对象创建Statement对象，比如下面这两条。

```plain
	stmt = con.createStatement(sql);

```

```plain
	stmt = con.prepareStatement(sql);

```

Statement是对一条SQL命令的包装。

第四步，使用Statement执行SQL语句，还可以获取返回的结果集ResultSet。

```plain
	rs = stmt.executeQuery();

```

```plain
stmt.executeUpdate();

```

第五步，操作ResultSet结果集，形成业务对象，执行业务逻辑。

```plain
	User rtnUser = null;
	if (rs.next()) {
		rtnUser = new User();
		rtnUser.setId(rs.getInt("id"));
		rtnUser.setName(rs.getString("name"));
	}

```

第六步，回收数据库资源，关闭数据库连接，释放资源。

```plain
	rs.close();
	stmt.close();
	con.cloase();

```

这个数据访问的套路或者定式，初学Java的程序员都比较熟悉。写多了JDBC程序，我们会发现Java里面访问数据的程序结构都是类似的，不一样的只是具体的SQL语句，然后还有一点就是执行完SQL语句之后，每个业务对结果的处理是不同的。只要稍微用心思考一下，你就会想到应该把它做成一个模板，方便之后使用，自然会去抽取JdbcTemplate。

## 抽取JdbcTemplate

抽取的基本思路是 **动静分离，将固定的套路作为模板定下来，变化的部分让子类重写**。这是常用的设计模式，基于这个思路，我们考虑提供一个JdbcTemplate抽象类，实现基本的JDBC访问框架。

以数据查询为例，我们可以在这个框架中，让应用程序员传入具体要执行的SQL语句，并把返回值的处理逻辑设计成一个模板方法让应用程序员去具体实现。

```plain
package com.minis.jdbc.core;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

public abstract class JdbcTemplate {
	public JdbcTemplate() {
	}
	public Object query(String sql) {
		Connection con = null;
		PreparedStatement stmt = null;
		ResultSet rs = null;
		Object rtnObj = null;

		try {
			Class.forName("com.microsoft.sqlserver.jdbc.SQLServerDriver");
			con = DriverManager.getConnection("jdbc:sqlserver://localhost:1433;databasename=DEMO;user=sa;password=Sql2016;");

			stmt = con.prepareStatement(sql);
			rs = stmt.executeQuery();

			//调用返回数据处理方法，由程序员自行实现
			rtnObj = doInStatement(rs);
		}
		catch (Exception e) {
				e.printStackTrace();
		}
		finally {
			try {
				rs.close();
				stmt.close();
				con.close();
			} catch (Exception e) {
			}
		}
		return rtnObj;
	}

	protected abstract  Object doInStatement(ResultSet rs);
}

```

通过上述代码我们可以看到，query()里面的代码都是模式化的，SQL语句作为参数传进来，最后处理SQL返回数据的业务代码，留给应用程序员自己实现，就是这个模板方法doInStatement()。这样就实现了动静分离。

比如说，我们数据库里有一个数据表User，程序员可以用一个数据访问类UserJdbcImpl进行数据访问，你可以看一下代码。

```plain
package com.test.service;

import java.sql.ResultSet;
import java.sql.SQLException;
import com.minis.jdbc.core.JdbcTemplate;
import com.test.entity.User;

public class UserJdbcImpl extends JdbcTemplate {
	@Override
	protected Object doInStatement(ResultSet rs) {
        //从jdbc数据集读取数据，并生成对象返回
		User rtnUser = null;
		try {
			if (rs.next()) {
				rtnUser = new User();
				rtnUser.setId(rs.getInt("id"));
				rtnUser.setName(rs.getString("name"));
				rtnUser.setBirthday(new java.util.Date(rs.getDate("birthday").getTime()));
			} else {
			}
		} catch (SQLException e) {
			e.printStackTrace();
		}

		return rtnUser;
	}
}

```

应用程序员在自己实现的doInStatement()里获得SQL语句的返回数据集并进行业务处理，返回一个业务对象给用户类。

而对外提供服务的UserService用户类就可以简化成下面这样。

```plain
package com.test.service;

import com.minis.jdbc.core.JdbcTemplate;
import com.test.entity.User;

public class UserService {
	public User getUserInfo(int userid) {
		String sql = "select id, name,birthday from users where id="+userid;
		JdbcTemplate jdbcTemplate = new UserJdbcImpl();
		User rtnUser = (User)jdbcTemplate.query(sql);

		return rtnUser;
	}
}

```

我们看到，用户类简单地创建一个UserJdbcImpl对象，然后执行query()即可，很简单。

有了这个简单的模板，我们就做到了把JDBC程序流程固化下来，分离出变化的部分，让应用程序员只需要管理SQL语句并处理返回的数据就可以了。

这是一个实用的结构，我们就基于这个结构继续往前走。

## 通过Callback模式简化业务实现类

上面抽取出来的Tempalte，我们也看到了，如果只是停留在现在的这一步，那应用程序的工作量还是很大的，对每一个数据表的访问都要求手写一个对应的JdbcImpl实现子类，很繁琐。为了不让每个实体类都手写一个类似于UserJdbcImpl的类，我们可以采用Callback模式来达到目的。

先介绍一下Callback模式，它是把一个需要被调用的函数作为一个参数传给调用函数。你可以看一下基本的做法。

先定义一个回调接口。

```plain
public interface Callback {
    void call();
}

```

有了这个Callback接口，任务类中可以把它作为参数，比如下面的业务任务代码。

```plain
public class Task {
    public void executeWithCallback(Callback callback) {
        execute(); //具体的业务逻辑处理
        if (callback != null) callback.call();
    }
}

```

这个任务类会先执行具体的业务逻辑，然后调用Callback的回调方法。

用户程序如何使用它呢？

```plain
    public static void main(String[] args) {
        Task task = new Task();
        Callback callback = new Callback() {
            public void call() {
                System.out.println("callback...");
            }
        };
        task.executeWithCallback(callback);
    }

```

先创建一个任务类，然后定义具体的回调方法，最后执行任务的同时将Callback作为参数传进去。这里可以看到，回调接口是一个单一方法的接口，我们可以采用函数式编程进一步简化它。

```plain
    public static void main(String[] args) {
        Task task = new Task();
        task.executeWithCallback(()->{System.out.println("callback;")});
    }

```

上面就是Callback模式的实现，我们把一个回调函数作为参数传给了调用者，调用者在执行完自己的任务后调用这个回调函数。

现在我们就按照这个模式改写JdbcTemplate 的query()方法。

```plain
	public Object query(StatementCallback stmtcallback) {
		Connection con = null;
		Statement stmt = null;

		try {
			Class.forName("com.microsoft.sqlserver.jdbc.SQLServerDriver");
			con = DriverManager.getConnection("jdbc:sqlserver://localhost:1433;databasename=DEMO;user=sa;password=Sql2016;");

			stmt = con.createStatement();

			return stmtcallback.doInStatement(stmt);
		}
		catch (Exception e) {
				e.printStackTrace();
		}
		finally {
			try {
				stmt.close();
				con.close();
			} catch (Exception e) {
			}
		}
		return null;
	}

```

从代码中可以看出，在query()方法中增加了一个参数：StatementCallback，这就是需要回调的方法。这里我还要提醒你一下，Java是纯粹的面向对象编程，没有真正的全局函数，所以实际代码中是一个类。

有了这个回调参数，就不需要给每一个数据访问增加一个子类来实现doInStatemnt()了，而是作为参数传进去。

你可以看一下Callback接口。

```plain
package com.minis.jdbc.core;

import java.sql.SQLException;
import java.sql.Statement;

public interface StatementCallback {
	Object doInStatement(Statement stmt) throws SQLException;
}

```

可以看出这是一个函数式接口。

现在，应用程序就只需要用一个JdbcTemplate类就可以了，不用再为每一个业务类单独做一个子类。就像我们前面说的，用户类需要使用Callback动态匿名类的方式进行改造。

代码如下：

```plain
	public User getUserInfo(int userid) {
		final String sql = "select id, name,birthday from users where id="+userid;
		return (User)jdbcTemplate.query(
				(stmt)->{
					ResultSet rs = stmt.executeQuery(sql);
					User rtnUser = null;
					if (rs.next()) {
						rtnUser = new User();
						rtnUser.setId(userid);
						rtnUser.setName(rs.getString("name"));
						rtnUser.setBirthday(new java.util.Date(rs.getDate("birthday").getTime()));
					}
					return rtnUser;
				}
		);
	}

```

从代码中可以看到，以前写在UserJdbcImpl里的业务代码，也就是对SQL语句返回值的处理逻辑，现在成了匿名类，作为参数传入query()里，最后在query()里会回调到它。

按照同样的办法我们还可以支持PreparedStatement类型，方法调用时带上SQL语句需要的参数值。

```plain
	public Object query(String sql, Object[] args, PreparedStatementCallback pstmtcallback) {
	    //省略获取connection等代码
	    pstmt = con.prepareStatement(sql);
	    for (int i = 0; i < args.length; i++) { //设置参数
    		Object arg = args[i];
            //按照不同的数据类型调用JDBC的不同设置方法
	    	if (arg instanceof String) {
		      pstmt.setString(i+1, (String)arg);
		    } else if (arg instanceof Integer) {
		      pstmt.setInt(i+1, (int)arg);
		    }
        }
	    return pstmtcallback.doInPreparedStatement(pstmt);
	}

```

通过代码可以知道，和普通的Statement相比，这个PReparedStatement场景只是需要额外对SQL参数一个个赋值。这里我们还要注意一点，当SQL语句里有多个参数的时候，MiniSpring会按照参数次序赋值，和参数名没有关系。

我们再来看一下为PreparedStement准备的Callback接口。

```plain
package com.minis.jdbc.core;

import java.sql.PreparedStatement;
import java.sql.SQLException;

public interface PreparedStatementCallback {
	Object doInPreparedStatement(PreparedStatement stmt) throws SQLException;
}

```

这也是一个函数式接口。

用户服务类代码改造如下：

```plain
public User getUserInfo(int userid) {
		final String sql = "select id, name,birthday from users where id=?";
		return (User)jdbcTemplate.query(sql, new Object[]{new Integer(userid)},
			(pstmt)->{
				ResultSet rs = pstmt.executeQuery();
				User rtnUser = null;
				if (rs.next()) {
					rtnUser = new User();
					rtnUser.setId(userid);
					rtnUser.setName(rs.getString("name"));
				}
				return rtnUser;
			}
		);
	}

```

到这里，我们就用一个单一的JdbcTemplate类实现了数据访问。

## 结合IoC容器

当然，我们还可以更进一步，既然我们的MiniSpring是个IoC容器，可以管理一个一个的Bean对象，那么我们就要好好利用它。由于只需要唯一的一个JdbcTemplate类，我们就可以事先把它定义为一个Bean，放在IoC容器里，然后通过@Autowired自动注入。

在XML配置文件中声明一下。

```plain
	<bean id="jdbcTemplate" class="com.minis.jdbc.core.JdbcTemplate" />

```

上层用户service程序中就不需要自己手动创建JdbcTemplate，而是通过Autowired注解进行注入就能得到了。

```plain
package com.test.service;

import java.sql.ResultSet;
import com.minis.beans.factory.annotation.Autowired;
import com.minis.jdbc.core.JdbcTemplate;
import com.test.entity.User;

public class UserService {
		@Autowired
		JdbcTemplate jdbcTemplate;
}

```

我们需要记住，MiniSpring只支持按照名字匹配注入，所以UserService类里的实例变量JdbcTemplate这个名字必须与XML文件中配置的Bean的id是一致的。如果不一致就会导致程序找不到JdbcTemplate。

这样一来，应用程序中和数据库访问相关的代码就全部剥离出去了，应用程序只需要声明使用它，而它的创建、管理都由MiniSpring框架来完成。从这里我们也能看出IoC容器带来的便利，事实上，我们需要用到的很多工具，都会以Bean的方式在配置文件中声明，交给IoC容器来管理。

## 数据源

我们注意到，JdbcTemplate中获取数据库连接信息等套路性语句仍然是硬编码的（hard coded）。

```plain
Class.forName("com.microsoft.sqlserver.jdbc.SQLServerDriver");
con = DriverManager.getConnection("jdbc:sqlserver://localhost:1433;databasename=DEMO;user=sa;password=Sql2016;");

```

现在我们动手把这一部分代码包装成DataSource，通过它获取数据库连接。假设有了这个工具，上层应用程序就简单了。你可以看一下使用者的代码示例。

```plain
con = dataSource.getConnection();

```

这个Data Source被JdbcTemplate使用。

```plain
public class JdbcTemplate {
	private DataSource dataSource;
}

```

而这个属性可以通过配置注入，你可以看下配置文件。

```plain
<bean id="dataSource" class="com.minis.jdbc.datasource.SingleConnectionDataSource">
	<property type="String" name="driverClassName" value="com.microsoft.sqlserver.jdbc.SQLServerDriver"/>
	<property type="String" name="url" value="jdbc:sqlserver://localhost:1433;databasename=DEMO;"/>
	<property type="String" name="username" value="sa"/>
	<property type="String" name="password" value="Sql2016"/>
</bean>
<bean id="jdbcTemplate" class="com.minis.jdbc.core.JdbcTemplate" >
	<property type="javax.sql.DataSource" name="dataSource" ref="dataSource"/>
</bean>

```

在DataSource这个Bean初始化的时候，设置Property时会加载相应的JDBC Driver，然后注入给JdbcTemplate来使用。

我们再次看到，独立抽取这些部件，加上IoC容器的Bean管理，给系统构造带来许多便利。

上面描述的是假定有了一个DataSource之后怎么使用，现在回头再来看DataSource本身是怎么构造出来的。其实Java里已经给出了这个接口，是javax.sql.DataSource。我们就遵守这个规范，做一个简单的实现。

```plain
package com.minis.jdbc.datasource;

import java.io.PrintWriter;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.SQLFeatureNotSupportedException;
import java.util.Properties;
import java.util.logging.Logger;
import javax.sql.DataSource;

public class SingleConnectionDataSource implements DataSource {
	private String driverClassName;
	private String url;
	private String username;
	private String password;
	private Properties connectionProperties;
	private Connection connection;

    //默认构造函数
	public SingleConnectionDataSource() {
	}
    //一下是属性相关的getter和setter
	public String getUrl() {
		return url;
	}
	public void setUrl(String url) {
		this.url = url;
	}
	public String getUsername() {
		return username;
	}
	public void setUsername(String username) {
		this.username = username;
	}
	public String getPassword() {
		return password;
	}
	public void setPassword(String password) {
		this.password = password;
	}
	public Properties getConnectionProperties() {
		return connectionProperties;
	}
	public void setConnectionProperties(Properties connectionProperties) {
		this.connectionProperties = connectionProperties;
	}
	@Override
	public PrintWriter getLogWriter() throws SQLException {
		return null;
	}
	@Override
	public int getLoginTimeout() throws SQLException {
		return 0;
	}
	@Override
	public Logger getParentLogger() throws SQLFeatureNotSupportedException {
		return null;
	}
	@Override
	public void setLogWriter(PrintWriter arg0) throws SQLException {
	}
	@Override
	public void setLoginTimeout(int arg0) throws SQLException {
	}
	@Override
	public boolean isWrapperFor(Class<?> arg0) throws SQLException {
		return false;
	}
	@Override
	public <T> T unwrap(Class<T> arg0) throws SQLException {
		return null;
	}
    //设置driver class name的方法，要加载driver类
	public void setDriverClassName(String driverClassName) {
		this.driverClassName = driverClassName;
		try {
			Class.forName(this.driverClassName);
		}
		catch (ClassNotFoundException ex) {
			throw new IllegalStateException("Could not load JDBC driver class [" + driverClassName + "]", ex);
		}
	}
    //实际建立数据库连接
	@Override
	public Connection getConnection() throws SQLException {
		return getConnectionFromDriver(getUsername(), getPassword());
	}
	@Override
	public Connection getConnection(String username, String password) throws SQLException {
		return getConnectionFromDriver(username, password);
	}
    //将参数组织成Properties结构，然后拿到实际的数据库连接
	protected Connection getConnectionFromDriver(String username, String password) throws SQLException {
		Properties mergedProps = new Properties();
		Properties connProps = getConnectionProperties();
		if (connProps != null) {
			mergedProps.putAll(connProps);
		}
		if (username != null) {
			mergedProps.setProperty("user", username);
		}
		if (password != null) {
			mergedProps.setProperty("password", password);
		}

		this.connection = getConnectionFromDriverManager(getUrl(),mergedProps);
		return this.connection;
	}
    //通过DriverManager.getConnection()建立实际的连接
	protected Connection getConnectionFromDriverManager(String url, Properties props) throws SQLException {
		return DriverManager.getConnection(url, props);
	}
}

```

这个类很简单，封装了和数据访问有关的信息，除了getter和setter之外，它最核心的方法就是getConnection()，这个方法又会调用getConnectionFromDriver()，最后会调用到getConnectionFromDriverManager()。你看一下这个方法，里面就是我们熟悉的DriverManager.getConnection()，一层层调用，最后还是落实到这里了。

所以我们看实际的数据库连接是什么时候创建的呢？这个可以采用不同的策略，可以在初始化Bean的时候创建，也可以延后到实际使用的时候。MiniSpring到现在这一步，采取的是后面这个策略，在应用程序dataSource.getConnection()的时候才实际生成数据库连接。

## 小结

我们这节课通过三个手段叠加，简化了数据库操作，重构了数据访问的程序结构。第一个手段是 **模板化**，把通用代码写到一个JdbcTemplate模板里，把变化的部分交给具体的类来实现。第二个手段就是通过 **Callback模式**，把具体类里实现的业务逻辑包装成一个回调函数，作为参数传给JdbcTemplate模板，这样就省去了要为每一个数据表单独增加一个具体实现类的工作。第三个手段就是结合IoC容器， **把JdbcTemplate声明成一个Bean**，并利用@Autowired注解进行自动注入。

之后我们抽取出了数据源的概念，包装connection，让应用程序和底下的数据库分隔开。

当然，程序走到这一步，还是有很多不足，主要的就是JdbcTemplate中还保留了很多固定的代码，比如SQL结果和业务对象的自动匹配问题，而且也没有考虑数据库连接池等等。这些都需要我们在后面的课程中一个个解决。

完整源代码参见 [https://github.com/YaleGuo/minis](https://github.com/YaleGuo/minis)

## 课后题

学完这节课，我也给你留一道思考题。我们现在只实现了query，想一想如果想要实现update应该如何做呢？欢迎你在留言区与我交流讨论，也欢迎你把这节课分享给需要的朋友。我们下节课见！