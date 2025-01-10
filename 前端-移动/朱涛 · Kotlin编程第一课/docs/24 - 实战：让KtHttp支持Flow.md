你好，我是朱涛。又到了熟悉的实战环节，这一次我们接着来改造KtHttp，让它能够支持协程的Flow API。

有了前面两次实战的基础，这次我们应该就轻车熟路了。在之前的 [4.0版本](https://time.geekbang.org/column/article/488985) 中，为了让KtHttp支持挂起函数，我们有两种思路，一种是 **改造内部**，另一种是 **扩展外部**。同理，为了让KtHttp支持Flow，这次的实战也是这两种思路。

因此，这节课我们仍然会分为两个版本。

- 5.0版本，基于4.0版本的代码，从KtHttp的 **外部扩展** 出Flow的能力。
- 6.0版本， **修改KtHttp内部**，让它支持Flow API。

其实在实际的工作中，我们往往没有权限修改第三方提供的SDK，那么这时候，如果想要让SDK获得Flow的能力，我们就只能借助Kotlin的扩展函数，为它 **扩展** 出Flow的能力。而对于工程内部的代码，我们希望某个功能模块获得Flow的能力，就可以 **直接修改它的源代码**，让它直接支持Flow。

那么在这节课里，我会同时用这两种手段来扩展并改造KtHttp，为你演示其中的关键步骤。在这个过程中，我也会为你讲解其中的常见误区和陷阱，这样一来，你就可以放心地将Flow应用到你的实际工作中了。

OK，让我们正式开始吧！

## 5.0版本：Callback转Flow

在上次的实战课当中，我们在3.0版本里，实现了KtHttp的异步Callback请求。之后在4.0版本里，我们并没有改动KtHttp的源代码，而是直接在KtCall的基础上扩展了 **挂起函数** 的支持。让我们重新回顾一下之前的代码：

```plain
// 代码段1

// 扩展函数
suspend fun <T : Any> KtCall<T>.await(): T =
//      暴露挂起函数的continuation
//              ↓
    suspendCancellableCoroutine { continuation ->
        val call = call(object : Callback<T> {
            override fun onSuccess(data: T) {
                println("Request success!")
                continuation.resume(data)
            }

            override fun onFail(throwable: Throwable) {
                println("Request fail!：$throwable")
                continuation.resumeWithException(throwable)
            }
        })

//          响应取消事件
//              ↓
        continuation.invokeOnCancellation {
            println("Call cancelled!")
            call.cancel()
        }
    }

```

我们知道，上面这种做法非常适合针对第三方SDK的扩展，而这一切，都要归功于Kotlin的 **扩展函数** 特性。那么这节课里，我们希望KtHttp支持Flow，其实也同样可以借助扩展函数来实现。Kotlin官方提供了一个API： **callbackFlow**，它就是专门用于将Callback转为Flow的。

Callback转Flow，用法跟Callback转挂起函数是差不多的。如果你去分析代码段1当中的代码模式，会发现Callback转挂起函数，主要有三个步骤。

- 第一步：使用suspendCancellableCoroutine执行Callback代码，等待Callback回调；
- 第二步：将Callback回调结果传出去，onSuccess的情况就传结果，onFail的情况就传异常；
- 第三步：响应协程取消事件invokeOnCancellation{}。

所以使用callbackFlow，也是这样三个步骤。如果你看过Google官方写的 [文档](https://developer.android.com/kotlin/flow#callback)，你可能会写出这样的代码：

```plain
// 代码段2

fun <T : Any> KtCall<T>.asFlow(): Flow<T> = callbackFlow {
    // 调用Callback
    val call = call(object : Callback<T> {
        override fun onSuccess(data: T) {
            // 1，传递成功数据，报错！
            offer(data)
        }

        override fun onFail(throwable: Throwable) {
            // 2，传递失败数据
            close(throwable)
        }

    })

    // 3，响应协程取消
    awaitClose {
        call.cancel()
    }
}

```

在这段代码里，callbackFlow的使用步骤也是分了三步。不过，由于Google官方写的文档已经有些过时了，如果你按照文档来写，会发现注释1处的代码其实会报错，IDE会提示应该使用trySend()替代offer()。

所以我们要再来改一改：

```plain
// 代码段3

fun <T : Any> KtCall<T>.asFlow(): Flow<T> = callbackFlow {
    val call = call(object : Callback<T> {
        override fun onSuccess(data: T) {
            // 1
            trySend(data)
        }

        override fun onFail(throwable: Throwable) {
            // 2
            close(throwable)
        }

    })

    awaitClose {
        call.cancel()
    }
}

```

那么从上面的代码中，你会发现，callbackFlow的底层用到了Channel，所以你才可以使用trySend()这样的API。这个API我在 [第19讲](https://time.geekbang.org/column/article/491021) 里提到过，它其实就是Channel.send()的 **非挂起函数** 版本的API。

这样改完以后，我们的代码就已经没有明显报错了。但，它仍然还有优化空间，对应的地方我已经用注释标记出来了。

我们来看一下注释1，这里使用trySend()，虽然在这个案例当中用这个API确实没问题，但在大部分场景下，它其实是不够稳妥的。你可以查看一下它的源码文档，会看到它的返回值类型是 **ChannelResult**，代表trySend()的执行结果是成功还是失败。

```plain
// 代码段4
public fun trySend(element: E): ChannelResult<Unit>

```

也就是说，如果我们往Channel当中成功地添加了元素，那么trySend()的返回值就是成功，如果当前的Channel管道已经满了，那么trySend()的返回值就是失败。

其实，当Channel管道容量已满的时候，我们更希望trySend()可以多等等，直到管道容量空闲以后再返回成功。所以这时候，我们可以使用 **trySendBlocking()** 来替代它。它是Kotlin协程1.5出现的一个新的API。

```plain
// 代码段5

fun <T : Any> KtCall<T>.asFlow(): Flow<T> = callbackFlow {
    val call = call(object : Callback<T> {
        override fun onSuccess(data: T) {
            // 1，变化在这里
            trySendBlocking(data)
        }

        override fun onFail(throwable: Throwable) {
            // 2
            close(throwable)
        }

    })

    awaitClose {
        call.cancel()
    }
}

```

不过，这里我们仅仅只是改为trySendBlocking()仍然还不够，让我们来运行一下程序，看看问题出在哪里：

```plain
// 代码段6

interface ApiServiceV5 {
    @GET("/repo")
    fun repos(
        @Field("lang") lang: String,
        @Field("since") since: String
    ): KtCall<RepoList>
}

fun main() = runBlocking {
    testFlow()
}

private suspend fun testFlow() =
    KtHttpV5.create(ApiServiceV5::class.java)
        .repos(lang = "Kotlin", since = "weekly")
        .asFlow()
        .catch { println("Catch: $it") }
        .collect {
        println(it)
    }

/*
输出正常
程序不会终止
*/

```

其实，问题的原因也很简单，由于callbackFlow的底层是Channel实现的，在我们用完它以后，应该主动将其关闭或者释放。不然的话，它就会一直 **占用计算机资源**。所以这时候，我们可以进一步完善trySendBlocking()这部分的代码。

```plain
// 代码段7

fun <T : Any> KtCall<T>.asFlow(): Flow<T> = callbackFlow {
    val call = call(object : Callback<T> {
        override fun onSuccess(data: T) {
            // 1，变化在这里
            trySendBlocking(data)
                .onSuccess { close() }
                .onFailure { close(it) }
        }

        override fun onFail(throwable: Throwable) {
            close(throwable)
        }

    })

    awaitClose {
        call.cancel()
    }
}

/*
输出结果
输出正常
程序等待一会后自动终止
*/

```

上面代码中的onSuccess、onFailure其实就相当于回调，在这里，不管是成功还是失败，我们都主动把callbackFlow当中的Channel关闭。这样一来，程序就可以正常终止了。

> 提示：在大部分场景下trySendBlocking()会比trySend()更稳妥一些，因为它会尽可能发送成功。但在某些特殊情况下，trySend()也有它的优势，因为它不会出现阻塞问题。

好，现在，5.0版本的代码其实就已经算是合格了。不过，我还想给你介绍下callbackFlow的一些使用细节： **close()与close(throwable)**。

close()这个方法，我们既可以传入异常，也可以不传入。不过，这两者在callbackFlow当中是有差异的。如果你将代码段7当中所有的close(throwable)都改为不传异常的话，程序代码也会出现问题。

```plain
// 代码段8
// 错误示范！错误示范！错误示范！

fun main() = runBlocking {
    testFlow()
}

private suspend fun testFlow() =
    KtHttpV5.create(ApiServiceV5::class.java)
        .repos(lang = "Kotlin", since = "weekly")
        .asFlow()
        .catch { println("Catch: $it") }
        .collect {
            println(it)
        }

fun <T : Any> KtCall<T>.asFlow(): Flow<T> = callbackFlow {
    val call = call(object : Callback<T> {
        override fun onSuccess(data: T) {
            trySendBlocking(data)
                .onSuccess { close() }
                .onFailure {
                    // 变化在这里
                    close()
                }
        }

        override fun onFail(throwable: Throwable) {
            // 变化在这里
            close()
        }
    })

    awaitClose {
        call.cancel()
    }
}

/*
断网执行以上代码：
不会有任何结果，连异常信息都没有
*/

```

在以上代码中，我们断网执行了这段程序，但在控制台上看不到任何异常的输出信息。这就是因为，我们调用close()的时候没有传入异常信息。

所以，在callbackFlow当中的异常分支里，我们如果使用close()，一定要 **带上对应的异常**，就像代码段7的那样“close(throwable)”。或者，为了防止在开发的过程中忘记传入异常信息，我们可以使用 **cancel()方法**。就像下面这样：

```plain
// 代码段9

fun <T : Any> KtCall<T>.asFlow(): Flow<T> = callbackFlow {
    val call = call(object : Callback<T> {
        override fun onSuccess(data: T) {
            trySendBlocking(data)
                .onSuccess { close() }
                .onFailure {
                    // 变化在这里
                    cancel(CancellationException("Send channel fail!", it))
                }
        }

        override fun onFail(throwable: Throwable) {
            // 变化在这里
            cancel(CancellationException("Request fail!", throwable))
        }
    })

    awaitClose {
        call.cancel()
    }
}

/*
断网执行
Catch: java.util.concurrent.CancellationException: Request fail!
*/

```

根据这里的运行结果，我们可以看到，把close()改成cancel()以后，程序运行结果也符合预期。而cancel其实还有一个优势：就算不小心忘记传throwable，我们还是可以看到一个CancellationException。

不过总的来说，只要我们可以记住传入异常信息，close()和cancel()两者的差别并不大。

另外还有一点，如果我们在callbackFlow当中还启动了其他的协程任务，close()和cancel()也同样可以取消对应的协程。如下所示：

```plain
// 代码段10

fun main() = runBlocking {
    testFlow()
}

private suspend fun testFlow() =
    KtHttpV5.create(ApiServiceV5::class.java)
        .repos(lang = "Kotlin", since = "weekly")
        .asFlow() // 注意这里
        .catch { println("Catch: $it") }
        .collect {
        println(it)
    }

fun <T : Any> KtCall<T>.asFlow(): Flow<T> = callbackFlow {

    val job = launch {
        println("Coroutine start")
        delay(3000L)
        println("Coroutine end") // 没有机会执行
    }

    job.invokeOnCompletion {
        println("Coroutine completed $it")
    }

    val call = call(object : Callback<T> {
        override fun onSuccess(data: T) {
            trySendBlocking(data)
                .onSuccess { close() }
                .onFailure {
                    cancel(CancellationException("Send channel fail!", it))
                }
        }

        override fun onFail(throwable: Throwable) {
            cancel(CancellationException("Request fail!", throwable))
        }
    })

    awaitClose {
        call.cancel()
    }
}

/*
断网执行
Coroutine start
Coroutine completed java.util.concurrent.CancellationException: Request fail!
Catch: java.util.concurrent.CancellationException: Request fail!
*/

```

可以看到，由于协程是结构化的，所以，当我们取消callbackFlow的时候，在它内部创建的协程job，也会跟着被取消。而且，它的异常信息也是一样的。

不过，如果我们把上面的launch{} 改成了“launch(Job()){}”，那么，协程任务就不会跟随callbackFlow一起被取消了。我相信，如果你还记得上节课讲的第二条准则，那你一定可以轻松理解这句话。因为， **它们的协程的父子关系已经被破坏了**！

最后，我还想再提一下 **awaitClose{}** 这个挂起函数，它的作用其实就是监听callbackFlow的生命周期，当它被关闭或者取消的时候，我们应该同时把OkHttp当中的网络请求也取消掉。它的作用，跟代码段1当中的continuation.invokeOnCancellation{} 是类似的。

好，callbackFlow的用法我们就讲解完了，有了它，以后我们就可以轻松地把第三方SDK的Callback扩展成Flow了。

那么接下来，我们就进入6.0版本的开发吧！

## 6.0版本：直接支持Flow

实际上，对于KtHttp来说，4.0版本、5.0版本都只是外部扩展，我们对KtHttp的内部源代码并没有做改动。

而对于6.0版本的开发，我们其实是希望KtHttp可以直接支持返回Flow类型的数据，也就是这样：

```plain
// 代码段11

interface ApiServiceV5 {
    @GET("/repo")
    fun repos(
        @Field("lang") lang: String,
        @Field("since") since: String
    ): KtCall<RepoList>

    @GET("/repo")
    fun reposFlow(
        @Field("lang") lang: String,
        @Field("since") since: String
    ): Flow<RepoList> // 注意这里
}

```

请你留意上面的代码注释，在ApiServiceV5当中，我定义了一个接口方法reposFlow()，它的返回值类型是 `Flow<RepoList>`，而不是之前的 `KtCall<RepoList>`。这样一来，我们在main()函数当中使用它的时候，就不需要使用asFlow()这个扩展函数了。就像下面这样：

```plain
// 代码段12

private suspend fun testFlow() =
    KtHttpV5.create(ApiServiceV5::class.java)
        .reposFlow(lang = "Kotlin", since = "weekly")
        // 注意这里不需要asFlow，因为reposFlow()返回值类型就是Flow
        .catch { println("Catch: $it") }
        .collect {
            println(it)
        }

fun main() = runBlocking {
    testFlow()
}

```

可以看到，当我们把reposFlow()的返回值类型定义成 `Flow<RepoList>` 以后，就需要改动KtHttp的源代码了。因为，它的内部需要根据这种情况做一些特殊的判断。

其实，在前面3.0版本的开发中，我们就已经做过一次判断了。当时，我们特地判断了一下，返回值类型是 `KtCall<T>` 还是 `T`。让我们来重新回顾一下当时的代码细节：

```plain
// 代码段13

private fun <T: Any> invoke(path: String, method: Method, args: Array<Any>): Any? {
    // 省略部分代码
    return if (isKtCallReturn(method)) {
        // 返回值类型是KtCall<RepoList>

        val genericReturnType = getTypeArgument(method)
        KtCall<T>(call, gson, genericReturnType)
    } else {
        // 返回值类型是 RepoList

        val response = okHttpClient.newCall(request).execute()
        val genericReturnType = method.genericReturnType
        val json = response.body?.string()
        gson.fromJson<Any?>(json, genericReturnType)
    }
}

```

看到上面的代码，相信你马上就能想明白了，如果要支持Flow，我们只需要在这里判断一下，返回值类型是不是 `Flow<T>` 即可。比如说：

```plain
// 代码段14

private fun <T : Any> invoke(path: String, method: Method, args: Array<Any>): Any? {
    // 省略部分代码
    return when {
        isKtCallReturn(method) -> {
            val genericReturnType = getTypeArgument(method)
            KtCall<T>(call, gson, genericReturnType)
        }
        isFlowReturn(method) -> {
            // 直接返回Flow
            flow<T> {
                // 请求API
                val genericReturnType = getTypeArgument(method)
                val response = okHttpClient.newCall(request).execute()
                val json = response.body?.string()
                val result = gson.fromJson<T>(json, genericReturnType)

                // 传出结果
                emit(result)

            }
        }
        else -> {
            val response = okHttpClient.newCall(request).execute()

            val genericReturnType = method.genericReturnType
            val json = response.body?.string()
            gson.fromJson<Any?>(json, genericReturnType)
        }
    }
}

// 判断返回值类型是不是 Flow<T>
private fun isFlowReturn(method: Method) =
        getRawType(method.genericReturnType) == Flow::class.java

```

由于代码段13当中已经有了if、else两个条件分支了，再增加一个分支的话，我们选择了when表达式。这里，我们增加了一个isFlowReturn(method)的分支，意思就是判断返回值类型是不是Flow，如果是的话，我们就直接使用flow{} 创建一个Flow返回了。

至此，我们6.0版本的开发工作，其实就已经完成了。是不是觉得非常轻松？ **对比起Callback转Flow，让KtHttp直接支持Flow确实要简单很多**。从这一点上，我们也可以看到Flow的强大和易用性。

那么在这时候，我们就可以写一些简单的测试代码，来验证我们的代码是否可靠了。

```plain
// 代码段15

private fun <T : Any> invoke(path: String, method: Method, args: Array<Any>): Any? {
    // 省略部分代码
    return when {
        isKtCallReturn(method) -> {
            val genericReturnType = getTypeArgument(method)
            KtCall<T>(call, gson, genericReturnType)
        }
        isFlowReturn(method) -> {
            // 增加日志
            logX("Start out")
            flow<T> {
                logX("Start in")
                val genericReturnType = getTypeArgument(method)
                val response = okHttpClient.newCall(request).execute()
                val json = response.body?.string()
                val result = gson.fromJson<T>(json, genericReturnType)
                logX("Start emit")
                emit(result)
                logX("End emit")
            }
        }
        else -> {
            val response = okHttpClient.newCall(request).execute()

            val genericReturnType = method.genericReturnType
            val json = response.body?.string()
            gson.fromJson<Any?>(json, genericReturnType)
        }
    }
}

private suspend fun testFlow() =
    KtHttpV5.create(ApiServiceV5::class.java)
        .reposFlow(lang = "Kotlin", since = "weekly")
        .flowOn(Dispatchers.IO) //切换线程
        .catch { println("Catch: $it") }
        .collect {
            logX("${it.count}")
        }
/*
输出结果
================================
Start out
Thread:main @coroutine#1
================================
================================
Start in
Thread:DefaultDispatcher-worker-1 @coroutine#2
================================
================================
Start emit
Thread:DefaultDispatcher-worker-1 @coroutine#2
================================
================================
End emit
Thread:DefaultDispatcher-worker-1 @coroutine#2
================================
================================
25
Thread:main @coroutine#1
================================

程序结束
*/

```

在上面的代码中，我们增加了一些日志，同时在调用处增加了“flowOn(Dispatchers.IO)”。可以看到，这样一来整个网络请求就执行在了DefaultDispatcher这个线程池当中，而其他部分的代码，仍然执行在main()线程。这也是符合预期的。

然后，我们可以通过断网来模拟出现异常的情况：

```plain
// 代码段16

/*
输出结果：
================================
Start out
Thread:main @coroutine#1
================================
================================
Start in
Thread:DefaultDispatcher-worker-1 @coroutine#2
================================
Catch: java.net.UnknownHostException:  nodename nor servname provided, or not known

程序结束
*/

```

可以看到，程序的运行结果仍然是符合预期的。

下面，我们再来看看6.0完整的代码：

```plain
// 代码段17

interface ApiServiceV5 {
    @GET("/repo")
    fun repos(
        @Field("lang") lang: String,
        @Field("since") since: String
    ): KtCall<RepoList>

    // 注释1
    @GET("/repo")
    fun reposFlow(
        @Field("lang") lang: String,
        @Field("since") since: String
    ): Flow<RepoList>
}

object KtHttpV5 {

    private var okHttpClient: OkHttpClient = OkHttpClient()
    private var gson: Gson = Gson()
    var baseUrl = "https://baseUrl.com"

    fun <T : Any> create(service: Class<T>): T {
        return Proxy.newProxyInstance(
            service.classLoader,
            arrayOf<Class<*>>(service)
        ) { proxy, method, args ->
            val annotations = method.annotations
            for (annotation in annotations) {
                if (annotation is GET) {
                    val url = baseUrl + annotation.value
                    return@newProxyInstance invoke<T>(url, method, args!!)
                }
            }
            return@newProxyInstance null

        } as T
    }

    private fun <T : Any> invoke(path: String, method: Method, args: Array<Any>): Any? {
        if (method.parameterAnnotations.size != args.size) return null

        var url = path
        val parameterAnnotations = method.parameterAnnotations
        for (i in parameterAnnotations.indices) {
            for (parameterAnnotation in parameterAnnotations[i]) {
                if (parameterAnnotation is Field) {
                    val key = parameterAnnotation.value
                    val value = args[i].toString()
                    if (!url.contains("?")) {
                        url += "?$key=$value"
                    } else {
                        url += "&$key=$value"
                    }

                }
            }
        }

        val request = Request.Builder()
            .url(url)
            .build()

        val call = okHttpClient.newCall(request)

        return when {
            isKtCallReturn(method) -> {
                val genericReturnType = getTypeArgument(method)
                KtCall<T>(call, gson, genericReturnType)
            }
            isFlowReturn(method) -> {
                logX("Start out")

                // 注释2
                flow<T> {
                    logX("Start in")
                    val genericReturnType = getTypeArgument(method)
                    val response = okHttpClient.newCall(request).execute()
                    val json = response.body?.string()
                    val result = gson.fromJson<T>(json, genericReturnType)
                    logX("Start emit")
                    emit(result)
                    logX("End emit")
                }
            }
            else -> {
                val response = okHttpClient.newCall(request).execute()

                val genericReturnType = method.genericReturnType
                val json = response.body?.string()
                gson.fromJson<Any?>(json, genericReturnType)
            }
        }
    }

    private fun getTypeArgument(method: Method) =
        (method.genericReturnType as ParameterizedType).actualTypeArguments[0]

    private fun isKtCallReturn(method: Method) =
        getRawType(method.genericReturnType) == KtCall::class.java

    private fun isFlowReturn(method: Method) =
        getRawType(method.genericReturnType) == Flow::class.java

}

fun main() = runBlocking {
    testFlow()
}

private suspend fun testFlow() =
    KtHttpV5.create(ApiServiceV5::class.java)
        .reposFlow(lang = "Kotlin", since = "weekly")
        .flowOn(Dispatchers.IO)
        .catch { println("Catch: $it") }
        .collect {
            logX("${it.count}")
        }

```

最后，我们也再来分析一下，为什么6.0的代码可以这么简单。这里有两个关键的地方，我也分别用注释标记了。

请你留意注释1处的 **reposFlow()** 方法的定义，它其实是一个普通的函数，并不是挂起函数。换言之，虽然它的返回值类型是Flow，但我们并不要求它在协程当中被调用。

另外，请留意注释2处， **flow{}** 这个高阶函数，它也只是一个普通函数，同样也不是挂起函数，这就意味着，它可以在普通函数里面直接调用。我们可以看看flow{} 的定义：

```plain
// 代码段18

// 不是挂起函数
public fun <T> flow(@BuilderInference block: suspend FlowCollector<T>.() -> Unit): Flow<T> = SafeFlow(block)

```

所以，正因为以上这两点，就使得Flow的易用性非常高，还记得我们在 [第20讲](https://time.geekbang.org/column/article/491632) 当中看过的那张Flow“上游、下游”的示意图吗？我们其实可以进一步完善它：

![](https://static001.geekbang.org/resource/image/37/20/370553ac768913a0702fda89a85b8120.jpg?wh=2000x1125)

也就是说，对于Flow的 **上游、中间操作符** 而言，它们其实根本就不需要协程作用域，只有在下游调用collect{} 的时候，才需要协程作用域。

因此，我们前面在写main()函数的时候，也可以换成这样的写法：

```plain
// 代码段19
fun main() {
    // 协程作用域外
    val flow = KtHttpV5.create(ApiServiceV5::class.java)
        .reposFlow(lang = "Kotlin", since = "weekly")
        .flowOn(Dispatchers.IO)
        .catch { println("Catch: $it") }

    runBlocking {
        // 协程作用域内
        flow.collect {
            logX("${it.count}")
        }
    }
}

```

可见，正因为Flow的上游不需要协程作用域，我们才可以轻松完成6.0版本的代码。

## 小结

这节实战课，为了让KtHttp支持Flow API，我们使用了两种方法。第一种，是从KtHttp的外部进行扩展，用这种思路，我们完成了5.0版本的开发；第二种，是修改KtHttp的内部，让ApiService当中的方法可以直接以Flow作为返回值类型，利用这种思路，我们完成了6.0的开发。

具体来说，我们是用到了这几个知识点，你可以重点关注一下：

- **callbackFlow{}**，它的作用就是把Callback转换成Flow。它的底层其实用到了Channel，因此，我们可以在callbackFlow{} 当中调用trySend()、trySendBlocking()，这两个方法都是Channel当中的“非挂起函数”的方法。需要注意的是，这里我们不能直接使用Channel的挂起函数send()，因为它必须要在协程体当中执行。
- 在callbackFlow{} 里，出现异常的逻辑分支当中，如果我们需要关闭callbackFlow，那么在调用close()的时候，一定要传入对应的异常参数 **close(throwable)**。不然的话，Flow的下游就无法收到任何的异常信息。
- 在callbackFlow{} 当中创建的 **协程任务**，也可以跟随callbackFlow一同被取消，只要我们不打破它原有的协程父子关系。
- 由于 **Flow的上游、中间操作符不需要协程作用域**，因此，我们可以在非协程当中执行创建Flow。这就导致我们6.0版本的代码轻松就可以实现。

## 思考题

在5.0版本的代码中，awaitClose{} 的作用是响应协程的取消，同时取消OkHttp的请求。其实，它除了这个作用以外，还有另外一个作用。

你可以把5.0版本代码中的awaitClose删掉，看看会发生什么。对于这样的现象，你能想到awaitClose{} 的另一个作用吗？

```plain
// 代码段20
fun <T : Any> KtCall<T>.asFlow(): Flow<T> = callbackFlow {
    val call = call(object : Callback<T> {
        override fun onSuccess(data: T) {
            trySendBlocking(data)
                .onSuccess { close() }
                .onFailure {
                    cancel(CancellationException("Send channel fail!", it))
                }
        }

        override fun onFail(throwable: Throwable) {
            cancel(CancellationException("Request fail!", throwable))
        }
    })

    // 注意这里
    // awaitClose {
    //     call.cancel()
    // }
}

```