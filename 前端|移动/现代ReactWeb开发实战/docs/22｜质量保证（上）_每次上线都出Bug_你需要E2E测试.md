你好，我是宋一玮，欢迎回到React应用开发的学习。

上节课我们学习了前端应用的性能优化，强调了不要过早做性能优化，应用开发的主线工作还是应用开发。当“慢”或者“卡”的性能问题真实发生时，再去用一些工具定位性能问题的根源。如果确认是React领域内的性能问题，可以通过为生产环境构建、避免不必要的渲染/重新渲染或代码分割等方案解决。

接下来两节课，我们将进入大中型React项目最重要的实践之一：自动化测试的学习。我们会利用端到端（E2E）测试和单元测试，保证React项目的质量。同时也了解一下测试金字塔的理论，有助于你更深入理解端到端和单元测试的关系。

这节课我们先关注端到端测试。

## 人工测试有什么问题吗？

质量保证是软件行业现代化的标志之一， **开发与测试可谓软件质量保证的矛与盾**。

软件测试方法可以分为 **人工测试** 和 **自动化测试**，两者对比如下表：

![图片](https://static001.geekbang.org/resource/image/ca/6e/ca6564572ae38f666334132ef094326e.jpg?wh=1620x846)

当前端项目规模大、迭代次数多时，测试工作量和难度往往呈几何上升，人工测试就会不堪重负，这时自动化测试就成为了前端项目的必选项。

这里额外提一下 **浏览器兼容性测试**。在前几年，各种浏览器之间的差异很大，浏览器兼容性测试以人工测试为主；而近年来，随着现代浏览器成为主流，自动化测试框架也不断演进，虽然浏览器兼容性依然是一个问题，但已经可以通过自动化方式来测试来降本增效。国内和国际上，都有不少SaaS软件测试平台支持浏览器兼容性测试。

## 自动化测试，谁来写？

如果你已经很熟悉软件工程师与测试工程师的“一人开发（dòugén）另一人测试（pěnggén）”的工作模式，可能会想当然地认为，编写自动化测试应该是测试工程师的职责。

确实有一些企业是这样做的，但从业界更多的敏捷开发实践，以及我自己的亲身经历来看，更有效的方式，是 **谁开发业务功能，谁就需要来写配套的自动化测试**。

这种做法看似有点“人格分裂”。用“人格分裂”这个词来评价一种工程实践是不太合适的，但我第一次接触这种开发测试方式时确实就是这个感觉。

当时的我认为，软件开发思维和测试思维是存在冲突的：开发是 **白盒**，以实现业务功能为目标；而测试是 **黑盒**，目标是在已经实现的业务功能中发现问题（zhǎochá）。这两种工作由同一个人来做，岂不是左手打右手？

后来当我采用这种方式，在一段时间内同时开发业务功能和测试用例，终于开始了解到这种方式的好处：

- 首先，我作为开发者，必须要从白盒和黑盒两个层面理解业务需求，这保证了我 **不会** 在一知半解的情况下 **盲目** 开发；
- 其次，编写业务代码和测试脚本之间也是一种 **迭代** 开发，我在开发业务时没考虑到的边界情况、错误处理等问题，在编写测试脚本时都会揭露出来，也督促我完善业务代码；
- 还有，这种方式可以最大化地保证业务代码和测试脚本的 **同步**，基本不会出现因为测试脚本长期不维护导致失效的情况；
- 最重要的是，这种方式让我对自己交付的代码质量更有 **信心**。

这种开发测试方式对开发者提出了更高的要求：

- 建立软件测试 **知识体系**；
- 具备自动化测试工具和脚本 **开发技能**；
- 开发的业务功能本身也要有更高的 **可测试性（Testability）**。

另外还有一个维度需要考虑：当多人协作开发一个前端应用项目时，每个人应为自己负责的业务模块开发自动化测试。这既是对自己的工作负责，也是为其他人的工作负责。毕竟每个人都不希望看到，由于别人代码把项目搞挂了，导致自己工作无法继续开展。

## 用Playwright进行E2E测试

这节课一开始提到会关注在端到端测试上。 **端到端测试（End-to-End Testing，简称E2E Testing），就是从最终用户体验出发，模拟真实的用户场景，验证软件行为和数据是否符合预期的测试**。这个“模拟”只是相对而言的，E2E测试应尽量基于真实的前端、后端服务、终端设备甚至网络环境，这样才能更有效地发现问题。E2E也有人工测试和自动化测试之分，这里我们特指自动化E2E测试。

下面请你跟随我，用开源自动化测试工具 **Playwright**，搭建一个自动化E2E测试项目。

### 创建E2E测试项目

Playwright是微软推出的一款开源的Web自动化测试框架（ [官网](https://playwright.dev/)），支持Chromium、Firefox和Webkit内核的现代浏览器，支持Windows、macOS和Linux多种操作系统，也提供了TypeScript、JavaScript、Python等多种语言的API。

首先我们需要创建E2E测试项目，说是创建，其实更推荐把E2E测试写在React应用项目里，而不是创建一个独立的项目。

还是以我们的 `oh-my-kanban` 项目举例，命令行进入项目根目录，初始化playwright，会提示几个问题，大部分用默认值就好，其中保存E2E测试脚本的路径建议改成 `tests/e2e` ，避免跟其他种类的测试混淆。然后playwright会自动为当前项目加入E2E测试功能：

```bash
npm init playwright@latest

Need to install the following packages:
  create-playwright@latest
Ok to proceed? (y) y
Getting started with writing end-to-end tests with Playwright:
Initializing project in '.'
✔ Do you want to use TypeScript or JavaScript? · TypeScript
✔ Where to put your end-to-end tests? · tests/e2e
✔ Add a GitHub Actions workflow? (y/N) · false
✔ Install Playwright browsers (can be done manually via 'npx playwright install')? (Y/n) · true
Installing Playwright Test (npm install --save-dev @playwright/test)…

# ...
Downloading browsers (npx playwright install)…
Downloading Chromium 107.0.5304.18 (playwright build v1028) - 119.8 Mb
# ...
Downloading Firefox 105.0.1 (playwright build v1357) - 68.5 Mb
# ...
Downloading Webkit 16.0 (playwright build v1724) - 53.9 Mb
# ...
Writing playwright.config.ts.
Writing tests/e2e/example.spec.ts.
Writing tests-examples/demo-todo-app.spec.ts.
Writing package.json.
✔ Success! Created a Playwright Test project at # ...

Inside that directory, you can run several commands:

  npx playwright test
    Runs the end-to-end tests.

  npx playwright test --project=chromium
    Runs the tests only on Desktop Chrome.

  npx playwright test example
    Runs the tests in a specific file.

  npx playwright test --debug
    Runs the tests in debug mode.

  npx playwright codegen
    Auto generate tests with Codegen.

We suggest that you begin by typing:

    npx playwright test

And check out the following files:
  - ./tests/e2e/example.spec.ts - Example end-to-end test
  - ./tests-examples/demo-todo-app.spec.ts - Demo Todo App end-to-end tests
  - ./playwright.config.ts - Playwright Test configuration

# ...

```

安装完成，在 `package.json` 中加入一个新的NPM脚本 `e2e` ：

![图片](https://static001.geekbang.org/resource/image/b6/af/b64d84378d701c714c70b4da499535af.png?wh=1129x360)

运行这个脚本，如果有以下提示则为测试通过：

```bash
npm run e2e

> oh-my-kanban@0.13.0 e2e
> playwright test

Running 3 tests using 3 workers

  3 passed (13s)

To open last HTML report run:

  npx playwright show-report

```

这时项目的文件树如下：

```bash
oh-my-kanban
├── build
├── playwright-report         # 测试报告目录
│   └── index.html            # HTML格式测试报告
├── public
├── src
├── tests
│   └── e2e                   # E2E测试目录
│       └── example.spec.ts   # 测试用例文件
├── tests-examples            # 测试用例的例子，看过就删了吧
│   └── demo-todo-app.spec.ts
├── LICENSE
├── README.md
├── package-lock.json
├── package.json
└── playwright.config.ts      # playwright的配置文件

```

直接打开 `playwright-report/index.html` 或者运行 `npx playwright show-report` 查看测试结果：

![图片](https://static001.geekbang.org/resource/image/5c/c2/5ccafc0f42406887711d58f3ddf61dc2.png?wh=1920x1120)

从结果可以看出，Playwright分别在3个不同内核的浏览器中，以 **无头（Headless）** 方式，跑了同一个自动化测试用例。

### 设计E2E测试用例

现在可以开始为 `oh-my-kanban` 项目编写E2E测试用例了。

马上迎来第一个“拷问”：“单个E2E测试用例应该涵盖多少业务功能？”

其实一个测试用例可大可小，如果太小了会迫使你写更多个数的用例，太大了又容易运行不稳定且难以维护。最终用户使用软件，主要还是通过一系列操作，完成他/她特定的目标。这里建议 **以真实用户的一个目标明确、有头有尾的使用流程作为参照，设计E2E测试用例**。

以 `oh-my-kanban` 项目为例，我们可以设计这样一个测试用例：

1. 用户打开看板应用；
2. 用户添加新卡片；
3. 用户将新添加的卡片拖拽到“进行中”看板列；
4. 用户点击保存所有卡片；
5. 用户刷新浏览器（代表先关闭然后再重新打开应用）。

然后认真的你开始焦虑了：“这个用例是不是太简单了？如果用户非要从另外一个浏览器中新打开一个看板应用，我需不需要测？如果用户非要从两个浏览器间拖拽卡片，我需不需要测？”

你永远无法约束一个用户最终会怎样使用你开发的软件，一个务实的测试工程师不会去尝试穷举所有可能性，否则开发出来的测试用例就算比源码都大好多好多倍，也都不一定能达到100%覆盖。所以说，设定测试范围（Scope）很重要。

也许你听说过 **80-20法则（即帕累托法则）**：

> 所有变因中，最重要的仅有20%，虽然剩余的80%占了多数，影响的幅度却远低于“关键的少数”。
>
> ——《 [帕累托法则 \- 维基百科](https://zh.wikipedia.org/wiki/%E5%B8%95%E7%B4%AF%E6%89%98%E6%B3%95%E5%88%99)》

从你 **最需要服务好的用户群的需求** 出发，你会发现，他们的用例才是你软件产品成功的关键，而不是那些异想天开的花活儿。当然，一些重要的边界情况还是要照顾到的。

### 开发测试用例

在Playwright之前，市面上已经有很多成熟的自动化测试框架，而Playwright吸收了这些框架的最佳实践，提供了功能丰富且强大的API。

我们没必要一上来就全学一遍，先熟悉以下这几个API就好：

- 导航： `page.goto()` ；
- 定位： `locator()` 、 `getByText()` ；
- 动作： `click()` 、 `type()` 、 `press()` 、 `dragTo()` ；
- 断言： `expect()` ，这与Jest框架的断言库是相同的。

先创建一个新的E2E测试用例文件 `tests/e2e/newCard.spec.ts` ，加入如下内容：

```typescript
import { test, expect } from '@playwright/test';

test('添加新卡片并移到进行中', async ({ page }) => {
  // 1. 用户打开看板应用
  await page.goto('http://localhost:3000');

  // 2. 用户添加新卡片
  // 2.1 点击“添加新卡片”
  const todoListColumn = page.locator('section', { hasText: '待处理' });
  const showAddNewButton = todoListColumn.getByText(/添加新卡片/);
  await showAddNewButton.click();

  // 2.2 输入新卡片
  const addNewCard = todoListColumn.locator('li').first();
  await expect(addNewCard).toContainText('添加新卡片');
  const newCardTitleText = addNewCard.locator('input');
  await expect(newCardTitleText).toBeFocused();
  await newCardTitleText.type('测试E2E任务-1');
  await newCardTitleText.press('Enter');

  // 2.3 断言新卡片
  const newCard = todoListColumn.locator('li').first();
  await expect(newCard).toContainText('测试E2E任务-1');

  // 3. 用户将新添加的卡片拖拽到“进行中”看板列
  const ongoingListColumn = page.locator('section', { hasText: '进行中' });
  await newCard.dragTo(ongoingListColumn);
  await expect(todoListColumn.locator('li').first()).not.toContainText('测试E2E任务-1');
  await expect(ongoingListColumn.locator('li').first()).toContainText('测试E2E任务-1');

  // 4. 用户点击保存所有卡片
  const saveAllButton = page.getByText('保存所有卡片');
  await saveAllButton.click();

  // 5. 用户刷新浏览器
  await page.reload();
  await expect(ongoingListColumn.locator('li').first()).toContainText('测试E2E任务-1');
});

```

开两个命令行窗口，一个跑 `npm start` ，另一个跑 `npm run e2e` ，可以看到测试用例在三个浏览器上都通过了，点进任一个测试详情可以看到每个步骤所花的时间，如下图所示：

![图片](https://static001.geekbang.org/resource/image/12/79/12e69fec7bef5f1a115105b571ac2f79.png?wh=1920x1128)

这段测试用例可以工作，但有一个明显的问题，就是它使用了太多HTML标签名来定位元素，如 `page.locator('section')` ，相当于是使用了CSS语法来查询元素。

而我们早在 [第5节课](https://time.geekbang.org/column/article/561203) 就达成共识，React组件内是使用了 `<section>` 还是 `<li>` ，属于组件的内部实现，连同为源码的父组件都不应该知道，那外部的自动化测试脚本更不应该知道了。这样的写法会导致内部实现细节的泄漏，降低测试用例的可维护性。

更何况，React渲染生成的DOM结构往往比组件树复杂，E2E脚本定位元素时常会有偏差，需要反复调整。看来应用源码和测试用例代码之间存在着Gap。

这就是一个典型的应用 **可测试性（Testability）** 的问题。

那么如何开发React应用，才能对E2E测试更友好呢？可以利用 `data-testid` 字段。这个HTML元素字段并不属于哪个标准，但广泛被Jest等主流测试框架所采用。

以 `src/KanbanColumn.js` 为例，为 `<section>` 标签加入一个 `data-testid` 属性：

![](https://static001.geekbang.org/resource/image/df/7c/df7c61a50f87eed2d7yya5d4111f117c.png?wh=1040x337)

然后修改测试用例 `tests/e2e/newCard.spec.ts` ，改用这个属性来定位元素：

![](https://static001.geekbang.org/resource/image/cc/06/cc8de6fdd3b2cd623ecdeea4918ab306.png?wh=1031x336)

这样就可以避免暴露HTML标签名这样的实现细节。

### 执行E2E测试

每次执行E2E要启两个命令行窗口，有点麻烦，稍微改一下 `playwright.config.ts` ：

```typescript
// ...
const config: PlaywrightTestConfig = {
  // ...
  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run start',
    port: 3000,
  },
};

export default config;

```

这样Playwright就会在执行E2E前，自动启动CRA的开发服务器。你只需要敲一个 `npm run e2e` 命令就够了。

每次启动3个浏览器有点重？那可以再加一个NPM命令 `npm run e2e:firefox` ，单独跑Firefox浏览器：

```json
  "scripts": {
    "e2e": "playwright test",
    "e2e:firefox": "playwright test --project=firefox",
  },

```

需要Debug测试用例？加上 `--debug` 参数就可以打开 **有头（Headed）** 浏览器，进入调试模式了：

```bash
npm run e2e:firefox -- --debug

```

![图片](https://static001.geekbang.org/resource/image/c8/ba/c849bdfc9278d8b4a79362c2584955ba.png?wh=1920x1245)

## 其他E2E测试工具

主流的Web前端自动化E2E测试工具还包括Cypress、Selenium。其中Cypress是在Electron基础上运行了一个高度自定义的浏览器环境，在这个环境中加入了自动化测试的各种功能和API；而Selenium则是基于各个浏览器各自的WebDriver。

Playwright与二者都不同，它使用了现代浏览器原生支持的 [CDP协议](https://chromedevtools.github.io/devtools-protocol/) **（DevTools Protocol）**，标准较新，运行效率也更高一些。

## 小结

在这节课里，我们了解了人工测试与自动化测试的区别，以及自动化测试对大型前端项目的重要意义，也探讨了由业务功能的开发者亲自来编写自动化测试脚本的好处。

然后我们学习了，如何利用现代自动化测试框架Playwright为 `oh-my-kanban` 项目开发自动化E2E测试用例。在最后的结尾处，也提及了另外两种自动化测试工具Cypress和Selenium。

在下节课，我们会继续学习大中型React项目的质量保证，利用单元测试进一步提升项目质量。

## 思考题

1. 这节课虽然提到了浏览器兼容性测试，但并没有细讲如何实现它的自动化。你在之前的工作学习中，有接触过浏览器兼容性测试吗？当时的测试范围、测试要点都是怎样的？哪些过程你认为是可以被自动化的？
2. 难得有机会，我们来讨论一个得罪人的问题。在之前的工作学习中，你曾经与专职的测试工程师共事过吗？他/她的主要工作是人工测试还是自动化测试？如果作为开发者的你，把自动化测试的活儿都给“抢”了，那他/她该干什么呢？

好了，这节课内容就到这里。我们下节课再见。