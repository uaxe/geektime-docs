你好，我是黄俊彬。

上节课，我带你学习了针对“过大类”代码坏味道的重构方法，我们将组件内分层架构重构流程分为3个维度和7个步骤。

![](https://static001.geekbang.org/resource/image/75/ae/75d88677c0284663ac8ae5fa585459ae.jpg?wh=3450x2069)

但在实际代码重构落地过程中，你一定会遇到这两个问题。第一个是在代码重构时，很容易引起新的Bug，然后会被质疑做代码重构的意义。这也是很多开发同学宁愿选择复制黏贴，也不轻易对原有代码进行重构的原因，因为一不小心，很容易背锅。

第二个问题是代码重构时仅通过人工挪动调整代码，既低效又容易出错。并且最后只能依靠手工测试来做质量验证，反馈效率也非常差。

所以今天这节课，我们将按照组件内分层架构的这7个步骤对文件模块的主页面进行MVP重构，在这个过程中你可以感受一下我们是如何解决上面这两个问题的，也就是说怎样重构才能速度快又不会出错？

## 第一步：业务分析

**搞清楚需求是一切的开始，重构也一样。如果我们对原有的需求一知半解，然后就急于重构，那么大概率会以失败告终。** 甚至在重构时，我们需要更进一步去挖掘那些“失传”的逻辑，以始为终才能让我们不会做错方向。

文件模块的主页如下图所示，从页面上来看，文件模块只是用于简单地展示文件的数据。

![](https://static001.geekbang.org/resource/image/9d/88/9d61e4d309b1ea590e707124d136aa88.jpg?wh=3000x2769)

但通过需求分析及梳理，我们发现该页面还包含了其他异常处理逻辑：

- 当用户进入文件页面时，如果成功从网络上加载文件列表，那么页面会显示文件列表（包含文件名及文件大小等）。
- 若从网络上加载文件列表时出现异常，用户界面会展示网络异常的提示信息，此时点击提示会重新触发数据的加载。
- 当加载数据为空时，同样会展示数据为空的提示，点击后重新触发刷新。

我画了一张图，为你展示整体的流程。

![](https://static001.geekbang.org/resource/image/c6/5c/c654f1c3cecf08c40a97c96a3cacf05c.jpg?wh=3205x2638)

需要注意，这些梳理出来的业务场景也是后面我们覆盖验收自动化测试的重要输入，如果遗漏了这些场景，就很容易出现我们上面说的重构时引起新的Bug。

## 第二步：代码分析

所谓知己知彼，才能百战百胜。 **我们必须先了解清楚原有代码里的详细设计、逻辑以及主要存在的问题，才能有针对性地重构，我们也能更清楚重构后的收益。**

下面我们一起来分析文件模块主页面的关键业务逻辑代码，后面是原有的代码设计。

```plain
public class FileFragment extends Fragment {
    //省略初始化代码... ...

    //获取文件列表
    private void getFileList() {
        new Thread(() -> {
            Message message = new Message();
            try {
                List<FileInfo> infoList = fileController.getFileList();
                message.what = 1;
                message.obj = infoList;
            } catch (NetworkErrorException e) {
                message.what = 0;
                message.obj = "NetworkErrorException";
                e.printStackTrace();
            }
            mHandler.sendMessage(message);
        }).start();
    }

    //接收消息
    public Handler mHandler = new Handler(new Handler.Callback() {
        @Override
        public boolean handleMessage(@NonNull Message msg) {
            if (msg.what == 1) {
                showTip(false);
                //显示网络数据
                List<FileInfo> infoList = (List<FileInfo>) msg.obj;
                FileListAdapter fileListAdapter = new FileListAdapter(infoList, getActivity());
                fileListRecycleView.addItemDecoration(new DividerItemDecoration(
                        getActivity(), DividerItemDecoration.VERTICAL));
                //设置布局显示格式
                fileListRecycleView.setLayoutManager(new LinearLayoutManager(getActivity()));
                fileListRecycleView.setAdapter(fileListAdapter);
            } else if (msg.what == 0) {
                showTip(true);
                //显示异常提醒数据
                tvMessage.setText(msg.obj.toString());
            } else {
                showTip(true);
                //显示空数据
                tvMessage.setText("empty data");
            }
            return false;
        }
    });

  //控制视图显示
    public void showTip(boolean show) {
        if (show) {
            tvMessage.setVisibility(View.VISIBLE);
            fileListRecycleView.setVisibility(View.GONE);
        } else {
            tvMessage.setVisibility(View.GONE);
            fileListRecycleView.setVisibility(View.VISIBLE);
        }
    }

   //省略其他代码... ...
}

```

首先，我们可以直观通过代码的行数来侧面反映一个类的复杂度。如果动辄过万行，你就要警惕，这可能是典型的“过大类”的代码坏味道。

其次，你可以通过这个类的import来看看它都依赖了哪些内容。以上面这个FileFragment为例，它的定位是一个页面，主要承担的是处理UI的展示。如果在这个类中import了大量的net、io、thread等包，这个时候也要警惕，这通常也是违反了“单一职责”的设计原则。

最后，我们还可以通过一些基础的工具和规范来检查这个类的代码质量，例如通过lint、sonar等工具检查基础的规范、内存泄露、自动化测试覆盖等问题。

借助上面这些方式，我们分析这个文件模块主页面主要存在四点问题。

- 典型的过大类代码坏味道问题，代码中的获取文件、异常逻辑判断、界面刷新控制等逻辑都是在一个类里面，不利于后续的扩展、修改和维护。
- 代码中的线程管理直接使用了new Thread的方式，不利于对线程进行统一管理。
- Handler存在内存泄漏风险。
- 代码中没有任何自动化守护测试。

## 第三步：补充自动化验收测试

接下来。我们来完成第三步——补充自动化验收测试， **这一步是整个重构的防护网，有了这层防护网，我们就可以在重构时频繁执行这些测试。当有测试失败时，就表明我们的重构破坏了以前的业务逻辑。**

根据前面分析的业务场景可知，用户核心业务操作的自动化可作为重构的测试守护，经过梳理，目前有3个核心用例。

- 测试用例1：当用户进入文件页面时，正常请求到数据，显示文件列表。
- 测试用例2：当用户进入文件页面时，网络异常，显示异常提示。
- 测试用例3：当用户进入文件页面时，数据为空，显示空提示。

我们将这些用例进行自动化。

```plain
//用例1
@Test
public void show_show_file_list_when_get_success() {
    //given
    ShadowFileFragment.state = ShadowFileFragment.State.SUCCESS;
    //when
    FragmentScenario<FileFragment> scenario = FragmentScenario.launchInContainer(FileFragment.class);
    scenario.onFragment(fragment -> {
        //then
        onView(withText("遗留代码重构.pdf")).check(matches(isDisplayed()));
        onView(withText("100.00K")).check(matches(isDisplayed()));
        onView(withText("系统组件化.pdf")).check(matches(isDisplayed()));
        onView(withText("9.67K")).check(matches(isDisplayed()));
    });
}

//用例2
@Test
public void show_show_error_tip_when_net_work_exception() {
    //given
    ShadowFileFragment.state = ShadowFileFragment.State.ERROR;
    //when
    FragmentScenario<FileFragment> scenario = FragmentScenario.launchInContainer(FileFragment.class);
    scenario.onFragment(fragment -> {
        //then
        onView(withText("NetworkErrorException")).check(matches(isDisplayed()));
    });
}

//用例3
@Test
public void show_show_empty_tip_when_not_has_data() {
    //given
    ShadowFileFragment.state = ShadowFileFragment.State.EMPTY;
    //when
    FragmentScenario<FileFragment> scenario = FragmentScenario.launchInContainer(FileFragment.class);
    scenario.onFragment(fragment -> {
        //then
        onView(withText("empty data")).check(matches(isDisplayed()));
    });
}

```

测试用例的执行结果如下图所示：

![](https://static001.geekbang.org/resource/image/af/87/afb0204bdcbbc520fb597e57bff7d787.jpg?wh=3000x1821)

从这个测试用例的执行结果可以看出，我们每次运行测试仅需要几秒的时间就可以得到反馈，这比我们只依赖后期的手工测试反馈问题，效率更高。所以，如果你的项目里原本就覆盖了足够的自动化测试，那么恭喜你。如果没有，你可以尝试和我们一样加上这一层防护网，它将让你在重构的时候更有信心。

## 第四步：简单设计

下面我们进行“简单设计”，搞清楚我们要到哪里去。这一步非常重要， **如果搞不清楚目的地，就很容易导致重构后的系统变成另外一个“遗留系统”。**

目前在移动领域常见的分层架构有MVP和MVVM，采用这两种架构都可以，重构方法也都一样，这里我们选择把文件主页面重构为MVP模式。首先我们来了解一下MVP的架构设计模式，以及基于该模式我们需要定义哪些核心的类、接口和数据模型。

### 1\. MVP架构

MVP架构的主要特点是业务逻辑和视图分离、Presenter和View之间通过接口交互。我还画了一张MVP架构设计图。

![](https://static001.geekbang.org/resource/image/b9/8a/b9435993036afb694d07001f6ac89f8a.jpg?wh=2105x1255)

### 2.关键接口设计

我们在代码分析中的第二点提到，代码直接使用了new Thread的方式来创建线程，会导致线程无法进行统一的管理，这里我们采用RxJava库来解决这个问题。RxJava是一个主流的标准，如果你不太了解它的优点和使用方式，可以参考 [官网的介绍](https://github.com/ReactiveX/RxJava%E3%80%82)。

结合MVP架构，关键的视图、业务、数据接口的设计代码如下：

```plain
public interface FileListContract {
 interface FileView  {
    showFileList(List<FileInfo> fileList);
    showNetWorkException(String errorMessage);
    showEmptyData();
}
interface Presenter {
    void getFileList();
}
}
public interface FileDataSource {
    Flowable<List<FileInfo>> getFileList();
}

```

## 第五步：小步安全重构

终于到了我们正式对代码进行调整的时候了。首先请你思考一个问题，为什么现在越来越多的生产线都使用自动化来替代传统的手工？

其实答案很明显，那就是因为机器不容易出错。那么在实际进行代码重构的时候，道理也是一样的。 **手工挪动必然效率低且容易出错，如果能通过工具自动化来进行代码重构，那么也许重构真的就是使用几个快捷键的事了。**

我们继续对文件模块进行重构，下面我将整个重构分为了几个关键的步骤，每个步骤都附上了用编辑器自动化重构的演示动图，你可以仔细观察我使用的自动化重构手法和所需要的时间。另外，在演示图中我将所使用的快捷键都通过插件在底部显示出来了，你可以由此了解我是怎样触发这些自动重构功能的。

### 1\. 提取业务逻辑到表现层

我们先在文件页面中新建FilePresenter成员变量，使用编辑器自动创建FilePresenter类。接着使用提取参数将mHandle提取为参数，再使用移动方法将getFileList方法移动至FilePresenter类中。

![图片](https://static001.geekbang.org/resource/image/de/78/dea763090b2a3034fdce9f6ffaa19178.gif?wh=1364x726)

### 2\. 提取视图层接口

使用提取方法的重构手法，按简单设计中定义的接口对展示数据代码进行重构。

![图片](https://static001.geekbang.org/resource/image/64/1f/6417596c26986a048b6c6eb6d3a7361f.gif?wh=1364x726)

使用提取接口的重构手法提取公用接口。

![图片](https://static001.geekbang.org/resource/image/60/48/6040e1a5caa3e1b2dd05d00be7876d48.gif?wh=1364x726)

### 3\. 调整表现层逻辑

将Handle类的handleMessage方法中的逻辑提取成公共方法，并移动至FilePresenter类中。然后将FileView的接口传入Presenter逻辑中，把对界面的操作调整为对FileView接口的调用。

![图片](https://static001.geekbang.org/resource/image/50/f8/50525078dafb660a9194e3a9591687f8.gif?wh=1364x726)

### 4\. 提取DataSource作为数据源管理

将原本的FileController重命名为FileRemoteDataSource，提取FileDataSource接口。

![图片](https://static001.geekbang.org/resource/image/b1/e7/b16a3af5b04a3fd94eaff1a113d7b6e7.gif?wh=1364x726)

### 5.使用RxJava优化异步线程操作

使用Rxjava替换原有的线程管理方法和Handler的回调机制，这一步相当于是开发新的功能，所以没办法使用编辑器的自动化重构功能，使用RxJava统一管理线程后的代码是后面这样。

```plain
public class FilePresenterImpl implements FileListContract.FilePresenter {
    private FileDataSource mFileDataSource;
    @VisibleForTesting
    public FileListContract.FileView mFileView;

    private CompositeDisposable compositeDisposable;

    public FilePresenterImpl(FileDataSource fileDataSource, FileListContract.FileView fileView) {
        this.mFileDataSource = fileDataSource;
        this.mFileView = fileView;
        compositeDisposable = new CompositeDisposable();
    }

    @Override
    @VisibleForTesting
    public void getFileList() {
        try {
            compositeDisposable.add(mFileDataSource.getFileList()
                    .subscribeOn(Schedulers.io())
                    .observeOn(AndroidSchedulers.mainThread()).subscribe(
                            fileList -> {
                                if (fileList == null || fileList.isEmpty()) {
                                    mFileView.showEmptyData();
                                } else {
                                    mFileView.showFileList(fileList);
                                }
                            }
                    ));
        } catch (NetworkErrorException e) {
            mFileView.showNetWorkException("NetworkErrorException");
        }
    }
}

```

## **第六步：补充中小型测试**

至此我们已经完成了整体的重构工作，下面我们以FilePresenterImpl为例，对它补充对应的中小型测试。FilePresenterImpTest将对主要的业务逻辑进行测试，但不包含UI部分。我们可以通过Mock的形式，校验最后接口有没有正常的回调即可。

后面是FilePresenterImp测试代码。

```plain
@RunWith(JUnit4.class)
@MediumTest
public class FilePresenterImplTest {
    @Rule
    public RxSchedulerRule rule = new RxSchedulerRule();
    @Test
    public void should_return_file_list_when_call_data_source_success() throws NetworkErrorException {
        //given
        FileListContract.FileView mockView = mock(FileListContract.FileView.class);
        FileDataSource mockFileDataSource = mock(FileDataSource.class);
        List<FileInfo> fileList = new ArrayList<>();
        fileList.add(new FileInfo("遗留代码重构.pdf", 102400));
        fileList.add(new FileInfo("系统组件化.pdf", 9900));
        when(mockFileDataSource.getFileList()).thenReturn(Flowable.fromArray(fileList));
        FileListContract.FilePresenter filePresenter = new FilePresenterImpl(mockFileDataSource, mockView);
        //when
        filePresenter.getFileList();
        //then
        verify(mockView).showFileList(anyList());
    }
    @Test
    public void should_show_empty_data_when_call_data_source_return_empty() throws NetworkErrorException {
        //given
        FileListContract.FileView mockView = mock(FileListContract.FileView.class);
        FileDataSource mockFileDataSource = mock(FileDataSource.class);
        when(mockFileDataSource.getFileList()).thenReturn(Flowable.fromArray(new ArrayList<>()));
        FileListContract.FilePresenter filePresenter = new FilePresenterImpl(mockFileDataSource, mockView);
        //when
        filePresenter.getFileList();
        //then
        verify(mockView).showEmptyData();
    }
    @Test
    public void should_show_network_exception_when_call_data_source_return_net_error() throws NetworkErrorException {
        //given
        FileListContract.FileView mockView = mock(FileListContract.FileView.class);
        FileDataSource mockFileDataSource = mock(FileDataSource.class);
        when(mockFileDataSource.getFileList()).thenThrow(new NetworkErrorException());
        FileListContract.FilePresenter filePresenter = new FilePresenterImpl(mockFileDataSource, mockView);
        //when
        filePresenter.getFileList();
        //then
        verify(mockView).showNetWorkException("NetworkErrorException");
    }
}

```

## 第七步：集成验收

前面已经保证了单个组件内的编译及自动化测试用例运行通过，现在还剩最后一步就是将组件进行发布，集成到主APP里。

注意，集成后应该保证APP模块中的架构守护测试用例和基本冒烟测试通过。我们在前面已经做好了足够的前置测试，在最后集成的阶段应该不会出现太多的质量问题。 **还有一点，我们要尽可能快地集成，因为只有集成才算是为整个重构画上一个完美的句号。**

对比重构前FileFragment将所有的逻辑都写在一个类中，这次重构，MVP的架构解决了业务与UI的逻辑分离、线程调度管理、覆盖自动化测试等问题，重构后的FileFragment代码是后面这样。

```plain
public class FileFragment extends Fragment implements FileListContract.FileView {
    // ... ...
    @Override
    public void showFileList(Object fileList) {
        showTip(false);
        //显示网络数据
        List<FileInfo> infoList = (List<FileInfo>) fileList;
        FileListAdapter fileListAdapter = new FileListAdapter(infoList, getActivity());
        fileListRecycleView.addItemDecoration(new DividerItemDecoration(
                getActivity(), DividerItemDecoration.VERTICAL));
        //设置布局显示格式
        fileListRecycleView.setLayoutManager(new LinearLayoutManager(getActivity()));
        fileListRecycleView.setAdapter(fileListAdapter);
    }
    @Override
    public void showNetWorkException(String msg) {
        showTip(true);
        //显示异常提醒数据
        tvMessage.setText(msg);
    }
    @Override
    public void showEmptyData() {
        showNetWorkException("empty data");
    }
  //... ...
}

```

## 总结

这节课，我通过文件模块主页面的MVP模式重构，为你演示了如何一步步高效安全地进行重构。可以看出，我们将自动化测试作为防护网来保障整个重构的安全性。在实际的重构过程中，每当我们修改了代码，都可以频繁运行守护测试，提前发现修改导致的错误。

另外，我们通过安全重构的手法，尽可能让编辑器自动帮助我们完成重构工作，减少人为直接挪动和修改代码。这样一方面可以减少手工带来的潜在错误，另外一方面自动化能大大提高整个重构的效率。

最后，我将整个文件模块按分层架构重构流程进行MVP重构的关键流程和要点整理成了一张图，方便你查看。

![](https://static001.geekbang.org/resource/image/b2/32/b216a74a74c199f75a39188312efa232.jpg?wh=2900x2424)

下节课我们将同样采用组件内分层架构重构流程方法，使用Kotlin及MVVM架构重构消息模块，敬请期待。

## 思考题

感谢你学完了今天的内容，今天的思考题是这样的：你是否在项目中经常使用Ctrl C + Ctrl V，你觉得这样会让开发效率更快还是更慢呢？

欢迎你把它分享给你的同事或朋友，让我们一起来高效高质量交付软件！