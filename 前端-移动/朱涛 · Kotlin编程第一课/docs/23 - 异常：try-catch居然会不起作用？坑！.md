你好，我是朱涛。这节课我们来学习Kotlin协程的异常处理。

其实到这里，我们就已经学完所有Kotlin协程的语法知识了。但在真正把Kotlin协程应用到生产环境之前，我们还需要掌握一个重要知识点，那就是异常处理。

比起Kotlin协程的语法知识点，协程的异常处理，其实更难掌握。在前面的课程中，我们已经了解到： **协程就是互相协作的程序，协程是结构化的**。正因为Kotlin协程有这两个特点，这就导致它的异常处理机制与我们普通的程序完全不一样。

换句话说： **如果把Java里的那一套异常处理机制，照搬到Kotlin协程里来，你一定会四处碰壁**。因为在普通的程序当中，你使用try-catch就能解决大部分的异常处理问题，但是在协程当中，根据不同的协程特性，它的异常处理策略是随之变化的。

我自己在工作中就踩过很多这方面的坑，遇到过各种匪夷所思的问题：协程无法取消、try-catch不起作用导致线上崩溃率突然大增、软件功能错乱却追踪不到任何异常信息，等等。说实话，Kotlin协程的普及率之所以不高，很大一部分原因也是因为它的异常处理机制太复杂了，稍有不慎就可能会掉坑里去。

那么今天这节课，我们就会来分析几个常见的协程代码模式，通过解决这些异常，我们可以总结出协程异常处理的6大准则。掌握了这些准则之后，你在以后遇到异常问题时，就能有所准备，也知道该怎么处理了。

## 为什么cancel()不起作用？

在Kotlin协程当中，我们通常把异常分为两大类，一类是 **取消异常**（CancellationException），另一类是 **其他异常**。之所以要这么分类，是因为在Kotlin协程当中，这两种异常的处理方式是不一样的。或者说，在Kotlin协程所有的异常当中，我们需要把CancellationException单独拎出来，特殊对待。

要知道，当协程任务被取消的时候，它的内部是会产生一个CancellationException的。而协程的结构化并发，最大的优势就在于：如果我们取消了父协程，子协程也会跟着被取消。但是我们也知道，很多初学者都会遇到一个问题，那就是协程无法被取消。

这里，主要涉及了三个场景，我们一个个来分析下。

### 场景1：cancel()不被响应

```plain
// 代码段1

fun main() = runBlocking {
    val job = launch(Dispatchers.Default) {
        var i = 0
        while (true) {
            Thread.sleep(500L)
            i ++
            println("i = $i")
        }
    }

    delay(2000L)

    job.cancel()
    job.join()

    println("End")
}

/*
输出结果

i = 1
i = 2
i = 3
i = 4
i = 5
// 永远停不下来
*/

```

在上面的代码中，我们启动了一个协程，在这个协程的内部，我们一直对i进行自增。过了2000毫秒以后，我们调用了job.cancel()。但通过运行的结果，我们可以看到协程并不会被取消。这是为什么呢？

其实前面课程里我们就讲过，协程是互相协作的程序。因此，对于协程任务的取消，也是需要互相协作的。协程外部取消，协程内部需要做出响应才行。具体来说，我们可以在协程体中加入状态判断：

```plain
// 代码段2

fun main() = runBlocking {
    val job = launch(Dispatchers.Default) {
        var i = 0
        // 变化在这里
        while (isActive) {
            Thread.sleep(500L)
            i ++
            println("i = $i")
        }
    }

    delay(2000L)

    job.cancel()
    job.join()

    println("End")
}

/*
输出结果
i = 1
i = 2
i = 3
i = 4
i = 5
End
*/

```

在这段代码里，我们把while循环的条件改成了while (isActive)，这就意味着，只有协程处于活跃状态的时候，才会继续执行循环体内部的代码。

这里，我们就可以进一步分析代码段1无法取消的原因了：当我们调用job.cancel()以后，协程任务已经不是活跃状态了，但代码并没有把isActive作为循环条件，因此协程无法真正取消。

所以到这里，我们就可以总结出协程异常处理的第一准则了： **协程的取消需要内部的配合**。

### 场景2：结构被破坏

我们都知道，协程是结构化的，当我们取消父协程的时候，子协程也会跟着被取消。比如，我们在 [第16讲](https://time.geekbang.org/column/article/487930) 当中，就看到过这张图：

![图片](https://static001.geekbang.org/resource/image/9b/02/9bf8c808c91040e25fc62e468b7dfc02.gif?wh=1080x608)

但在某些情况下，我们嵌套创建的子协程并不会跟随父协程一起取消，比如下面这个案例：

```plain
// 代码段3

val fixedDispatcher = Executors.newFixedThreadPool(2) {
    Thread(it, "MyFixedThread").apply { isDaemon = false }
}.asCoroutineDispatcher()

fun main() = runBlocking {
    // 父协程
    val parentJob = launch(fixedDispatcher) {

        // 1，注意这里
        launch(Job()) { // 子协程1
            var i = 0
            while (isActive) {
                Thread.sleep(500L)
                i ++
                println("First i = $i")
            }
        }

        launch { // 子协程2
            var i = 0
            while (isActive) {
                Thread.sleep(500L)
                i ++
                println("Second i = $i")
            }
        }
    }

    delay(2000L)

    parentJob.cancel()
    parentJob.join()

    println("End")
}

/*
输出结果
First i = 1
Second i = 1
First i = 2
Second i = 2
Second i = 3
First i = 3
First i = 4
Second i = 4
End
First i = 5
First i = 6
// 子协程1永远不会停下来
*/

```

以上代码中，我们创建了一个fixedDispatcher，它是由两个线程的线程池实现的。接着，我们通过launch创建了三个协程，其中parentJob是父协程，随后我们等待2000毫秒，然后取消父协程。

不过，通过程序的运行结果，我们发现，虽然“子协程1”当中使用了while(isActive)作为判断条件，它也仍然无法被取消。其实，这里的主要原因还是在注释1处，我们在创建子协程的时候， **使用了launch(Job()){}**。而这种创建方式，就打破了原有的协程结构。

为了方便你理解，我画了一张图，描述它们之间的父子关系。

![](https://static001.geekbang.org/resource/image/19/c2/191c4ffcf783a14a4aef9ca934dffec2.jpg?wh=2000x983)

根据这张图，可以看到“子协程1”已经不是parentJob的子协程了，而对应的，它的父Job是我们在launch当中传入的Job()对象。所以，在这种情况下，当我们调用parentJob.cancel()的时候，自然也就无法取消“子协程1”了。

其实这个时候，如果我们稍微改动一下上面的代码，不传入Job()，程序就可以正常运行了。

```plain
// 代码段4

fun main() = runBlocking {
    val parentJob = launch(fixedDispatcher) {

        // 变化在这里
        launch {
            var i = 0
            while (isActive) {
                Thread.sleep(500L)
                i ++
                println("First i = $i")
            }
        }

        launch {
            var i = 0
            while (isActive) {
                Thread.sleep(500L)
                i ++
                println("Second i = $i")
            }
        }
    }

    delay(2000L)

    parentJob.cancel()
    parentJob.join()

    println("End")
}

/*
输出结果
First i = 1
Second i = 1
First i = 2
Second i = 2
First i = 3
Second i = 3
First i = 4
Second i = 4
End
*/

```

在上面的代码中，parentJob与它内部的子协程1、子协程2之间是父子关系，因此它们两个都是会响应协程取消的事件的。这时候，它们之间的关系就变成了下图这样：

![](https://static001.geekbang.org/resource/image/fb/7d/fb2bf0b6f4307dcb9b678557cb1f027d.jpg?wh=2000x856)

那么到这里，我们其实就可以总结出第二条准则了： **不要轻易打破协程的父子结构**！

### 场景3：未正确处理CancellationException

其实，对于Kotlin提供的挂起函数，它们是可以自动响应协程的取消的，比如说，当我们把Thread.sleep(500)改为delay(500)以后，我们就不需要在while循环当中判断isActive了。

```plain
// 代码段5

fun main() = runBlocking {

    val parentJob = launch(Dispatchers.Default) {
        launch {
            var i = 0
            while (true) {
                // 变化在这里
                delay(500L)
                i ++
                println("First i = $i")
            }
        }

        launch {
            var i = 0
            while (true) {
                // 变化在这里
                delay(500L)
                i ++
                println("Second i = $i")
            }
        }
    }

    delay(2000L)

    parentJob.cancel()
    parentJob.join()

    println("End")
}

/*
输出结果
First i = 1
Second i = 1
First i = 2
Second i = 2
First i = 3
Second i = 3
End
*/

```

实际上，对于delay()函数来说，它可以自动检测当前的协程是否已经被取消，如果已经被取消的话，它会抛出一个CancellationException，从而终止当前的协程。

为了证明这一点，我们可以在以上代码的基础上，增加一个try-catch。

```plain
// 代码段6

fun main() = runBlocking {

    val parentJob = launch(Dispatchers.Default) {
        launch {
            var i = 0
            while (true) {
                // 1
                try {
                    delay(500L)
                } catch (e: CancellationException) {
                    println("Catch CancellationException")
                    // 2
                    throw e
                }
                i ++
                println("First i = $i")
            }
        }

        launch {
            var i = 0
            while (true) {
                delay(500L)
                i ++
                println("Second i = $i")
            }
        }
    }

    delay(2000L)

    parentJob.cancel()
    parentJob.join()

    println("End")
}

/*
输出结果
First i = 1
Second i = 1
First i = 2
Second i = 2
First i = 3
Second i = 3
Second i = 4
Catch CancellationException
End
*/

```

请看注释1，在用try-catch包裹了delay()以后，我们就可以在输出结果中，看到“Catch CancellationException”，这就说明delay()确实可以自动响应协程的取消，并且产生CancellationException异常。

不过，以上代码中，最重要的其实是注释2：“throw e”。当我们捕获到CancellationException以后，还要把它重新抛出去。而如果我们删去这行代码的话，子协程将同样无法被取消。

```plain
// 代码段7

fun main() = runBlocking {

    val parentJob = launch(Dispatchers.Default) {
        launch {
            var i = 0
            while (true) {
                try {
                    delay(500L)
                } catch (e: CancellationException) {
                    println("Catch CancellationException")
                    // 1，注意这里
                    // throw e
                }
                i ++
                println("First i = $i")
            }
        }

        launch {
            var i = 0
            while (true) {
                delay(500L)
                i ++
                println("Second i = $i")
            }
        }
    }

    delay(2000L)

    parentJob.cancel()
    parentJob.join()

    println("End")
}

/*
输出结果
输出结果
First i = 1
Second i = 1
First i = 2
Second i = 2
First i = 3
Second i = 3
Second i = 4
..
First i = 342825
Catch CancellationException
// 程序将永远无法终止
*/

```

可见，在这段代码中，我们把“throw e”这行代码注释掉，重新运行之后，程序就永远无法终止了。这主要是因为，我们捕获了CancellationException以后没有重新抛出去，就导致子协程无法正常取消。

所以到这里，我们就可以总结出第三条准则了： **捕获了CancellationException以后，要考虑是否应该重新抛出来**。

> 题外话：很多开发者喜欢在代码里捕获Exception这个父类，比如这样：catch(e: Exception){}，这也是很危险的。平时写Demo为了方便这样写没问题，但在生产环境则应该禁止。

好，到这里，我们就通过协程取消异常的三个场景，总结了三条准则，来应对CancellationException这个特殊的异常。

那么接下来，我们再来看看如何在协程当中处理普通的异常。

## 为什么try-catch不起作用？

如果你有Java经验，那你一定会习惯性地把try-catch当做是解决所有异常的手段。但是，在Kotlin协程当中，try-catch并非万能的。有时候，即使你用try-catch包裹了可能抛异常的代码，软件仍然会崩溃。比如下面这个例子：

```plain
// 代码段8

fun main() = runBlocking {
    try {
        launch {
            delay(100L)
            1 / 0 // 故意制造异常
        }
    } catch (e: ArithmeticException) {
        println("Catch: $e")
    }

    delay(500L)
    println("End")
}

/*
输出结果：
崩溃
Exception in thread "main" ArithmeticException: / by zero
*/

```

在这段代码中，我们使用try-catch包裹了launch{}，在协程体内部，我们制造了一个异常。不过从运行结果这里，我们可以看到，try-catch并没有成功捕获异常，程序等待了100毫秒左右，最终还是崩溃了。

类似的，如果我们把代码段8当中的launch换成async，结果也是差不多的：

```plain
// 代码段9

fun main() = runBlocking {
    var deferred: Deferred<Unit>? = null
    try {
        deferred = async {
            delay(100L)
            1 / 0
        }
    } catch (e: ArithmeticException) {
        println("Catch: $e")
    }

    deferred?.await()

    delay(500L)
    println("End")
}

/*
输出结果：
崩溃
Exception in thread "main" ArithmeticException: / by zero
*/

```

其实，对于这种try-catch失效的问题，如果你还记得在 [第14讲](https://time.geekbang.org/column/article/486305) 当中，我提到的launch、async的 **代码运行顺序** 的问题，那你就一定可以理解其中的原因。这主要就是因为，当协程体当中的“1/0”执行的时候，我们的程序已经跳出try-catch的作用域了。

当然，要解决这两个问题也很容易。对于代码段8来说，我们可以挪动一下try-catch的位置，比如说这样：

```plain
// 代码段10

fun main() = runBlocking {

    launch {
        try {
            delay(100L)
            1 / 0 // 故意制造异常
        } catch (e: ArithmeticException) {
            println("Catch: $e")
        }
    }

    delay(500L)
    println("End")
}

/*
输出结果：
Catch: java.lang.ArithmeticException: / by zero
End
*/

```

也就是说，我们可以把try-catch挪到launch{} 协程体内部。这样一来，它就可以正常捕获到ArithmeticException这个异常了。

而对于代码段9的async的这个例子，我们其实有两种解决手段，其中一种跟上面的做法一样，我们把try-catch挪到了async{} 协程体内部，比如这样：

```plain
// 代码段11

fun main() = runBlocking {
    var deferred: Deferred<Unit>? = null

    deferred = async {
        try {
            delay(100L)
            1 / 0
        } catch (e: ArithmeticException) {
            println("Catch: $e")
        }
    }

    deferred?.await()

    delay(500L)
    println("End")
}

```

OK，到这里，我们就可以总结出第四条准则了： **不要用try-catch直接包裹launch、async**。

接下来，我们再看看async的另外一种手段，其实这种方式网上有些博客也介绍过，我们可以使用try-catch包裹“deferred.await()”。让我们来看看是否可行：

```plain
// 代码段12

fun main() = runBlocking {
    val deferred = async {
        delay(100L)
        1 / 0
    }

    try {
        deferred.await()
    } catch (e: ArithmeticException) {
        println("Catch: $e")
    }

    delay(500L)
    println("End")
}

/*
输出结果
Catch: java.lang.ArithmeticException: / by zero
崩溃：
Exception in thread "main" ArithmeticException: / by zero
*/

```

那么，根据以上程序的运行结果可以看到，这样做其实是行不通的。如果你看过一些其他博客，甚至还有种说法是：await()如果不调用的话，async当中的异常甚至不会发生。我们再来试试看：

```plain
// 代码段13

fun main() = runBlocking {
    val deferred = async {
        delay(100L)
        1 / 0
    }

    delay(500L)
    println("End")
}

/*
输出结果
崩溃：
Exception in thread "main" ArithmeticException: / by zero
*/

```

可见，async当中产生异常，即使我们不调用await()同样是会导致程序崩溃的。那么，为什么会发生这样的情况？是不是我们忽略了什么？

### SupervisorJob

实际上，如果我们要使用try-catch包裹“deferred.await()”的话，还需要配合 **SupervisorJob** 一起使用。也就是说，借助SupervisorJob来改造代码段13的话，我们就可以实现“不调用await()就不会产生异常而崩溃”。

```plain
// 代码段14

fun main() = runBlocking {
    val scope = CoroutineScope(SupervisorJob())
    scope.async {
        delay(100L)
        1 / 0
    }

    delay(500L)
    println("End")
}

/*
输出结果
End
*/

```

可以看到，当我们使用SupervisorJob创建一个scope以后，用scope.async{}启动协程后，只要不调用“deferred.await()”，程序就不会因为异常而崩溃。

所以同样的，我们也能用类似的办法来改造代码段12当中的逻辑：

```plain
// 代码段15

fun main() = runBlocking {
    val scope = CoroutineScope(SupervisorJob())
    // 变化在这里
    val deferred = scope.async {
        delay(100L)
        1 / 0
    }

    try {
        deferred.await()
    } catch (e: ArithmeticException) {
        println("Catch: $e")
    }

    delay(500L)
    println("End")
}

/*
输出结果
Catch: java.lang.ArithmeticException: / by zero
End
*/

```

在上面的代码中，我们仍然使用“scope.async {}”创建了协程，同时也用try-catch包裹“deferred.await()”，这样一来，这个异常就成功地被我们捕获了。

那么， **SupervisorJob到底是何方神圣**？让我们来看看它的源码定义：

```plain
// 代码段16

public fun SupervisorJob(parent: Job? = null) : CompletableJob
                    = SupervisorJobImpl(parent)

public interface CompletableJob : Job {
    public fun complete(): Boolean

    public fun completeExceptionally(exception: Throwable): Boolean
}

```

根据以上代码，我们可以看到，SupervisorJob()其实不是构造函数， **它只是一个普通的顶层函数**。而这个方法返回的对象，是Job的子类。

SupervisorJob与Job最大的区别就在于，当它的子Job发生异常的时候，其他的子Job不会受到牵连。我这么说你可能会有点懵，下面我做了一个动图，来演示普通Job与SupervisorJob之间的差异。

![图片](https://static001.geekbang.org/resource/image/c0/64/c0eeea3b0b8b016df76ae7b3d9620264.gif?wh=1080x608)

这个是普通Job，对于子Job出现异常时的应对策略。可以看到，由于parentJob是一个普通的Job对象，当job1发生异常之后，它会导致parentJob取消，进而导致job2、job3也受到牵连。

而这时候，如果我们把parentJob改为SupervisorJob，job1发生异常的的话，就不会影响到其他的Job了。

![](https://static001.geekbang.org/resource/image/a4/cc/a482f7082d6d87dea51ffdb856e292cc.jpg?wh=2000x864)

所以到这里，我们就可以总结出第五条准则了： **灵活使用SupervisorJob，控制异常传播的范围**。

> 提示：并非所有情况下，我们都应该使用SupervisorJob，有时候Job会更合适，这要结合实际场景分析。

好，到目前为止，我们就已经了解了try-catch和SupervisorJob这两种处理异常的手段。但是，由于协程是结构化的，当我们的协程任务出现复杂的层级时，这两种手段其实都无法很好的应对。所以这个时候，我们就需要CoroutineExceptionHandler出场了。

### CoroutineExceptionHandler

对于CoroutineExceptionHandler，我们其实在 [第17讲](https://time.geekbang.org/column/article/488571) 里也简单地提到过。它是CoroutineContext的元素之一，我们在创建协程的时候，可以指定对应的CoroutineExceptionHandler。

那么CoroutineExceptionHandler究竟适用于什么样的场景呢？让我们来看一个例子：

```plain
// 代码段17

fun main() = runBlocking {

    val scope = CoroutineScope(coroutineContext)

    scope.launch {
        async {
            delay(100L)
        }

        launch {
            delay(100L)

            launch {
                delay(100L)
                1 / 0 // 故意制造异常
            }
        }

        delay(100L)
    }

    delay(1000L)
    println("End")
}

/*
输出结果
Exception in thread "main" ArithmeticException: / by zero
*/

```

在上面的代码中，我模拟了一个复杂的协程嵌套场景。对于这样的情况，我们其实很难一个个在每个协程体里面去写try-catch。所以这时候，为了捕获到异常，我们就可以使用CoroutineExceptionHandler了。

```plain
// 代码段18

fun main() = runBlocking {
    val myExceptionHandler = CoroutineExceptionHandler { _, throwable ->
        println("Catch exception: $throwable")
    }

    // 注意这里
    val scope = CoroutineScope(coroutineContext + Job() + myExceptionHandler)

    scope.launch {
        async {
            delay(100L)
        }

        launch {
            delay(100L)

            launch {
                delay(100L)
                1 / 0 // 故意制造异常
            }
        }

        delay(100L)
    }

    delay(1000L)
    println("End")
}

/*
Catch exception: ArithmeticException: / by zero
End
*/

```

以上代码中，我们定义了一个CoroutineExceptionHandler，然后把它传入了scope当中，这样一来，我们就可以捕获其中所有的异常了。

看到这里，你也许松了一口气：终于有了一个简单处理协程异常的方式了。不过，你也别高兴得太早，因为我曾经就踩过CoroutineExceptionHandler的一个坑，最终导致App功能大面积异常。

而出现这个问题的原因就是：CoroutineExceptionHandler不起作用了！

### 为什么CoroutineExceptionHandler不起作用？

为了模拟我当时的业务场景，我把代码段18稍作改动。

```plain
// 代码段19
fun main() = runBlocking {
   val myExceptionHandler = CoroutineExceptionHandler { _, throwable ->
       println("Catch exception: $throwable")
   }

   // 不再传入myExceptionHandler
   val scope = CoroutineScope(coroutineContext)
   scope.launch {
       async {
           delay(100L)
       }
       launch {
           delay(100L)
           // 变化在这里
           launch(myExceptionHandler) {
               delay(100L)
               1 / 0
           }
       }
       delay(100L)
   }
   delay(1000L)
   println("End")
}
/*
输出结果
崩溃：
Exception in thread "main" ArithmeticException: / by zero
*/

```

请你留意上面的注释，我们把自定义的myExceptionHandler，放到出现异常的launch那里传了进去。按理说，程序的执行结果是不会发生变化才对的。但实际上，myExceptionHandler并不会起作用，我们的异常不会被它捕获。

如果你对比代码段18和代码段19，你会发现，myExceptionHandler直接定义在发生异常的位置反而不生效，而定义在最顶层却可以生效！你说它的作用域是不是很古怪？

![图片](https://static001.geekbang.org/resource/image/22/13/22fyya9f9de13c8580b4508e7eabe813.gif?wh=1080x608)

其实，出现这种现象的原因，就是因为：CoroutineExceptionHandler只在顶层的协程当中才会起作用。也就是说，当子协程当中出现异常以后，它们都会统一上报给顶层的父协程，然后顶层的父协程才会去调用CoroutineExceptionHandler，来处理对应的异常。

那么到这里，我们就可以总结出第六条准则了： **使用CoroutineExceptionHandler处理复杂结构的协程异常，它仅在顶层协程中起作用**。

## 小结

至此，这节课的内容就接近尾声了，我们来做一个简单的总结。

在Kotlin协程当中，异常主要分为两大类，一类是协程取消异常（CancellationException），另一类是其他异常。为了处理这两大类问题，我们一共总结出了6大准则，这些我们都要牢记在心。

![](https://static001.geekbang.org/resource/image/72/c5/72b96aa44f68fde40f626fe536eb36c5.jpg?wh=2000x763)

- 第一条准则： **协程的取消需要内部的配合**。
- 第二条准则： **不要轻易打破协程的父子结构**！这一点，其实不仅仅只是针对协程的取消异常，而是要贯穿于整个协程的使用过程中。我们知道，协程的优势在于结构化并发，它的许多特性都是建立在这个特性之上的，如果我们无意中打破了它的父子结构，就会导致协程无法按照预期执行。
- 第三条准则： **捕获了CancellationException以后，要考虑是否应该重新抛出来**。在协程体内部，协程是依赖于CancellationException来实现结构化取消的，有的时候我们出于某些目的需要捕获CancellationException，但捕获完以后，我们还需要思考是否需要将其重新抛出来。
- 第四条准则： **不要用try-catch直接包裹launch、async**。这一点是很多初学者会犯的错误，考虑到协程代码的执行顺序与普通程序不一样，我们直接使用try-catch包裹launch、async，是不会有任何效果的。
- 第五条准则： **灵活使用SupervisorJob，控制异常传播的范围**。SupervisorJob是一种特殊的Job，它可以控制异常的传播范围。普通的Job，它会因为子协程当中的异常而取消自身，而SupervisorJob则不会受到子协程异常的影响。在很多业务场景下，我们都不希望子协程影响到父协程，所以SupervisorJob的应用范围也非常广。比如说Android当中的viewModelScope，它就使用了SupervisorJob，这样一来，我们的App就不会因为某个子协程的异常导致整个应用的功能出现紊乱。
- 第六条准则： **使用CoroutineExceptionHandler处理复杂结构的协程异常，它仅在顶层协程中起作用**。我们都知道，传统的try-catch在协程当中并不能解决所有问题，尤其是在协程嵌套层级较深的情况下。这时候，Kotlin官方为我们提供了CoroutineExceptionHandler作为补充。有了它，我们可以轻松捕获整个作用域内的所有异常。

其实，这节课里我提到的这些案例，只是我平时工作中遇到的很小一部分。案例是讲不完的，在协程中处理异常，你将来肯定也会遇到千奇百怪的问题。但重要的是分析问题的思路，还有解决问题的手段。这节课我给你总结的6大准则呢，就是你将来遇到协程异常时，可以用的6种处理手段。

当我们遇到问题的时候，首先要分析是CancellationException导致的，还是其他异常导致的。接着我们就可以根据实际情况去思考，该用哪种处理手段了。

另外如果你足够细心的话，你会发现这节课总结出的6大准则，其实都跟协程的 **结构化并发** 有着密切联系。由于协程之间存在父子关系，因此它的异常处理也是遵循这一规律的。而协程的异常处理机制之所以这么复杂，也是因为它的结构化并发特性。

所以，除了这6大准则以外，我们还可以总结出一个核心理念： **因为协程是“结构化的”，所以异常传播也是“结构化的”**。

如果你能理解协程异常处理的核心理念，同时能够牢记前面的6大准则。我相信，将来不论你遇到什么样的古怪问题，你都可以分析出问题的根源，找到解决方案！

## 思考题

前面我们提到过，CoroutineExceptionHandler可以一次性捕获整个作用域内所有协程的异常。那么，我们是不是可以抛弃try-catch，只使用CoroutineExceptionHandler呢？为什么？

欢迎在留言区分享你的答案，也欢迎你把今天的内容分享给更多的朋友。