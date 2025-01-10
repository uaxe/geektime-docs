你好，我是郭屹。

到这一节课，我们的Spring AOP部分也就结束了，你是不是跟随我的这个步骤也实现了自己的AOP呢？欢迎你把你的实现代码分享出来，我们一起讨论，共同进步！为了让你对这一章的内容掌握得更加牢固，我们对AOP的内容做一个重点回顾。

### 重点回顾

Spring AOP是Spring框架的一个核心组件之一，是Spring面向切面编程的探索。面向对象和面向切面，两者一纵一横，编织成一个完整的程序结构。

在AOP编程中，Aspect指的是横切逻辑（cross-cutting concerns），也就是那些和基本业务逻辑无关，但是却是很多不同业务代码共同需要的功能，比如日志记录、安全检查、事务管理，等等。Aspect能够通过Join point，Advice和Pointcut来定义，在运行的时候，能够自动在Pointcut范围内的不同类型的Advice作用在不同的Join point上，实现对横切逻辑的处理。

所以，这个AOP编程可以看作是一种以Aspect为核心的编程方式，它强调的是将横切逻辑作为一个独立的属性进行处理，而不是直接嵌入到基本业务逻辑中。这样做，可以提高代码的可复用性、可维护性和可扩展性，使得代码更容易理解和设计。

AOP的实现，是基于JDK动态代理的，站在Java的角度，这很自然，概念很容易实现，但是效率不高，限制也比较多。可以说AOP的实现是Spring框架中少数不尽人意的一部分，也可以看出世界顶级高手也有考虑不周到的地方。

那我们在课程中是如何一步步实现AOP的呢？

我们是基于JDK来实现的，因为比较自然、容易。我们先是引入了Java的动态代理技术，探讨如何用这个技术动态插入业务逻辑。然后我们进一步抽取动态业务逻辑，引入Spring里的Interceptor和Advice的概念。之后通过引入Spring的PointCut概念，进行advice作用范围的定义，让系统知道前面定义的Advice 会对哪些对象产生影响。最后为了免除手工逐个配置PointCut和Interceptor的工作，我们就通过一个自动化的机制自动生成动态代理。最终实现了一个有模有样的AOP解决方案。

好了，回顾完这一章的重点，我们再来看一下我每节课后给你布置的思考题。题目和答案我都放到下面了，不要偷懒，好好思考之后再来看答案。

### 17｜动态代理：如何在运行时插入逻辑？

#### 思考题

如果MiniSpring想扩展到支持Cglib，程序应该从哪里下手改造？

#### 参考答案

我们的动态代理包装在AopProxy这个接口中，对JDK动态代理技术，使用了JdkDynamicAopProxy这个类来实现，所以平行的做法，对于Cglib技术，我们就可以新增一个CglibAopProxy类进行实现。

同时，采用哪一种AOP Proxy可以由工厂方法决定，也就是在ProxyFactoryBean中所使用的aopProxyFactory，它在初始化的时候有个默认实现，即DefaultAopProxyFactory。我们可以将这个类的createAopProxy()方法改造一下。

```plain
	public class DefaultAopProxyFactory implements AopProxyFactory {
		public AopProxy createAopProxy(Object target) {
			if (targetClass.isInterface() || Proxy.isProxyClass(targetClass)) {
				return new JdkDynamicAopProxy(target);
			}
			return new CglibAopProxy(config);
		}
	}

```

根据某些条件决定使用JdkDynamicAopProxy还是CglibAopProxy，或者通过配置文件给一个属性来配置也可以。

### 18｜拦截器 ：如何在方法前后进行拦截？

#### 思考题

如果我们希望beforeAdvice能在某种情况下阻止目标方法的调用，应该从哪里下手改造改造我们的程序？

#### 参考答案

答案在MethodBeforeAdviceInterceptor 的实现中，看它的invoke方法。

```plain
	public class MethodBeforeAdviceInterceptor implements MethodInterceptor {
		public Object invoke(MethodInvocation mi) throws Throwable {
			this.advice.before(mi.getMethod(), mi.getArguments(), mi.getThis());
			return mi.proceed();
		}
	}

```

这个方法先调用advice.before()，然后再调用目标方法。所以如果我们希望beforeAdvice能够阻止流程继续，可以将advice.before()接口改造成有一个boolean返回值，规定返回false则不调用mi.proceed()。

### 19｜Pointcut ：如何批量匹配代理方法？

#### 思考题

我们现在实现的匹配规则是按照 `*` 模式串进行匹配，如果有不同的规则，应该如何改造呢？

#### 参考答案

如果仍然按照名字来匹配，那就可以改造NameMatchMethodPointcut类，它现在的核心代码是：

```plain
	public class NameMatchMethodPointcut implements MethodMatcher,Pointcut{
		private String mappedName = "";
		protected boolean isMatch(String methodName, String mappedName) {
			return PatternMatchUtils.simpleMatch(mappedName, methodName);
		}
	}

```

默认的实现用的是PatternMatchUtils.simpleMatch()，比较简单的模式串。我们可以给PatternMatchUtils增加一个方法，如regExprMatch()正则表达式匹配，在这里接收正则表达式串，进行匹配校验。

如果超出名字匹配的范围，需要用到不一样的匹配规则，就可以并列增加一个OtherMatchMethodPointcut类h和响应的advisor类，自己实现。并在配置文件里指定使用这个Advisor。

```plain
	<bean id="advisor" class="com.minis.aop.OtherMatchMethodPointcutAdvisor">
    </bean>
    <bean id="action" class="com.minis.aop.ProxyFactoryBean">
        <property type="String" name="interceptorName" value="advisor" />
    </bean>

```

### 20｜AutoProxyCreator：如何自动添加动态代理？

#### 思考题

AOP时常用于数据库事务处理，如何用我们现在的AOP架构实现简单的事务处理？

#### 参考答案

针对数据库事务，手工代码简化到了极致，就是执行SQL之前执行conn.setAutoCommit(false),在执行完SQL之后，再执行conn.commit()。因此，我们用一个MethodInterceptor就可以简单实现。

假定有了这样一个interceptor。

```plain
<bean id="transactionInterceptor" class="TransactionInterceptor" />

```

这个Interceptor拦截目标方法后添加事务处理逻辑，因此需要改造一下。

```plain
public class TransactionInterceptor implements MethodInterceptor{
	@Override
	public Object invoke(MethodInvocation invocation) throws Throwable {
conn.setAutoCommit(false);
Object ret=invocation.proceed();
conn.commit();
		return ret;
	}
}

```

从代码里可以看到，这里需要一个conn，因此我们要设法将数据源信息注入到这里。

我们可以抽取出一个TranactionManager类，大体如下：

```plain
public class TransactionManager {
	@Autowired
	private DataSource dataSource;
	Connection conn = null;

	protected void doBegin() {
		conn = dataSource.getConnection();
		if (conn.getAutoCommit()) {
			conn.setAutoCommit(false);
		}
	}
	protected void doCommit() {
		conn.commit();
	}
}

```

由这个transaction manager负责数据源以及开始和提交事务，然后将这个transaction manager作为一个Bean注入Interceptor，因此配置应该是这样的。

```plain
<bean id="transactionInterceptor" class="TransactionInterceptor" >
    <property type="TransactionManager" name="transactionManager" value="txManager" />
</bean>
<bean id="txManager" class="TransactionManager">
</bean>

```

所以Interceptor最后应该改造成这个样子：

```plain
public class TransactionInterceptor implements MethodInterceptor{
  TransactionManager transactionManager;
	@Override
	public Object invoke(MethodInvocation invocation) throws Throwable {
transactionManager.doBegin();
Object ret=invocation.proceed();
transactionManager.doCommit();
		return ret;
	}
}

```