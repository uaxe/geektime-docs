你好，我是徐昊。从今天开始，我们就来使用TDD的方式实现注入依赖容器。

在上节课，我们参照其他依赖注入容器，介绍了依赖注入容器的大致功能。现在请回想一下TDD的流程（参看 [第11讲](https://time.geekbang.org/column/article/496703)）：

![](https://static001.geekbang.org/resource/image/a5/9c/a5a74d26cf9581064420d81cff7da89c.jpg?wh=2284x1285)

现在我们需要将需求分解为功能点，并构想架构愿景。

## 将需求分解为功能点

对于组件构造部分，我分解的任务如下：

- 无需构造的组件——组件实例

- 如果注册的组件不可实例化，则抛出异常
  - 抽象类
  - 接口
- 构造函数注入
  - 无依赖的组件应该通过默认构造函数生成组件实例
  - 有依赖的组件，通过Inject标注的构造函数生成组件实例
  - 如果所依赖的组件也存在依赖，那么需要对所依赖的组件也完成依赖注入
  - 如果组件有多于一个Inject标注的构造函数，则抛出异常
  - 如果组件需要的依赖不存在，则抛出异常
  - 如果组件间存在循环依赖，则抛出异常
- 字段注入
  - 通过Inject标注将字段声明为依赖组件
  - 如果组件需要的依赖不存在，则抛出异常
  - 如果字段为final则抛出异常
  - 如果组件间存在循环依赖，则抛出异常
- 方法注入
  - 通过Inject标注的方法，其参数为依赖组件
  - 通过Inject标注的无参数方法，会被调用
  - 按照子类中的规则，覆盖父类中的Inject方法
  - 如果组件需要的依赖不存在，则抛出异常
  - 如果方法定义类型参数，则抛出异常
  - 如果组件间存在循环依赖，则抛出异常

对于依赖选择部分，我分解的任务列表如下：

- 对Provider类型的依赖
  - 注入构造函数中可以声明对于Provider的依赖
  - 注入字段中可以声明对于Provider的依赖
  - 注入方法中可声明对于Provider的依赖
- 自定义Qualifier的依赖
  - 注册组件时，可额外指定Qualifier
  - 注册组件时，可从类对象上提取Qualifier
  - 寻找依赖时，需同时满足类型与自定义Qualifier标注
  - 支持默认Qualifier——Named

对于生命周期管理部分，我分解的任务列表如下：

- Singleton生命周期
  - 注册组件时，可额外指定是否为Singleton
  - 注册组件时，可从类对象上提取Singleton标注
  - 对于包含Singleton标注的组件，在容器范围内提供唯一实例
  - 容器组件默认不是Single生命周期
- 自定义Scope标注
  - 可向容器注册自定义Scope标注的回调

对于架构构想，我倾向于使用类似Guice、PicoContainer等框架，以代码方式来配置容器。而不是像Spring一样，主要依赖配置文件。

由于依赖注入容器的问题规模较小，我将采用经典TDD模式进行开发，因而也不需要对功能点进行进一步的分解了。

在进入红/绿/重构循环之前，我的build.gradle.kts文件如下所示：

```
plugins {
    `java-library`
    "jacoco"
}
repositories {
    mavenCentral()
}
dependencies {
    implementation("jakarta.inject:jakarta.inject-api:2.0.1")
    testImplementation("org.junit.jupiter:junit-jupiter-api:5.8.2")
    testImplementation("org.junit.jupiter:junit-jupiter-params:5.8.2")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:5.8.2")
    testRuntimeOnly("org.junit.vintage:junit-vintage-engine:5.8.2")
    testRuntimeOnly("org.junit.platform:junit-platform-runner:1.8.2")
    testImplementation("org.mockito:mockito-core:4.3.1")
    testImplementation("jakarta.inject:jakarta.inject-tck:2.0.1")
}
tasks.withType<Test>() {
    useJUnitPlatform()
}
java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

```

## 进入红/绿/重构循环

下面让我们进入TDD的红/绿/重构循环：

到这里，我们引入了Provider这样一个类似于Factory工厂方法的结构，得到了整个依赖注入容器的基本结构。

那么剩下的事情就是，我们要围绕DI容器的基本结构，对其进行更多功能上的完善。

## 思考题

在重构的时候，我采用的是增加一个平行实现（Parallel Implementation）。用平行实现替换原有功能，然后再删除原有实现的做法。你有没有不一样的做法？

欢迎把你的思考和想法分享在留言区，也欢迎你扫描详情页的二维码加入读者交流群。我们下节课再见！