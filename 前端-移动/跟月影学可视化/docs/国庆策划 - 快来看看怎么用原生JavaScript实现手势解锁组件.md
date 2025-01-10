你好，我是月影。前几天，我给你出了一道实操题，不知道你完成得怎么样啦？

今天，我就给你一个 [参考版本](https://github.com/akira-cn/handlock)。当然，并不是说这一版就最好，而是说，借助这一版的实现，我们就能知道当遇到这样比较复杂的 UI 需求时，我们应该怎样思考和实现。

![](https://static001.geekbang.org/resource/image/b1/b2/b1a40490690d3c0418842d86fc81b2b2.jpeg?wh=1920*1080)

首先，组件设计一般来说包括7个步骤，分别是理解需求、技术选型、结构（UI）设计、数据和API设计、流程设计、兼容性和细节优化，以及工具和工程化。

当然了，并不是每个组件设计的时候都需要进行这些过程，但一个项目总会在其中一些过程里遇到问题需要解决。所以，下面我们来做一个简单的分析。

## 理解需求

上节课的题目本身只是说设计一个常见的手势密码的 UI 交互，那我们就可以通过选择验证密码和设置密码来切换两种状态，每种状态有自己的流程。

如果你就照着需求把整个组件的状态切换和流程封装起来，或者只是提供了一定的 UI 样式配置能力的话，还远远不够。实际上这个组件如果要给用户使用，我们需要将过程节点开放出来。也就是说， **需要由使用者决定设置密码的过程里执行什么操作、验证密码的过程和密码验证成功后执行什么操作**，这些是组件开发者无法代替使用者来决定的。

```
var password = '11121323';

var locker = new HandLock.Locker({
  container: document.querySelector('#handlock'),
  check: {
    checked: function(res){
      if(res.err){
        console.error(res.err); //密码错误或长度太短
        [执行操作...]
      }else{
        console.log(`正确，密码是：${res.records}`);
        [执行操作...]
      }
    },
  },
  update:{
    beforeRepeat: function(res){
      if(res.err){
        console.error(res.err); //密码长度太短
        [执行操作...]
      }else{
        console.log(`密码初次输入完成，等待重复输入`);
        [执行操作...]
      }
    },
    afterRepeat: function(res){
      if(res.err){
        console.error(res.err); //密码长度太短或者两次密码输入不一致
        [执行操作...]
      }else{
        console.log(`密码更新完成，新密码是：${res.records}`);
        [执行操作...]
      }
    },
  }
});

locker.check(password)

```

## 技术选型

这个问题的 UI 展现的核心是九宫格和选中的小圆点，从技术上来讲，我们有三种可选方案： DOM/Canvas/SVG，三者都是可以实现主体 UI 的。那我们该怎么选择呢？

如果使用 DOM，最简单的方式是使用 flex 布局，这样能够做成响应式的。使用 DOM 的优点是容易实现响应式，事件处理简单，布局也不复杂（但是和 Canvas 比起来略微复杂），但是斜线（demo 里没有画）的长度和斜率需要计算。

除了使用 DOM 外，使用 Canvas 绘制也很方便。用 Canvas 实现有两个小细节，一是要实现响应式，我们可以用 DOM 构造一个正方形的容器。这里，我们使用 `padding-top:100%` 撑开容器高度使它等于容器宽度。 代码如下：

```
#container {
  position: relative;
  overflow: hidden;
  width: 100%;
  padding-top: 100%;
  height: 0px;
  background-color: white;
}

```

第二个细节是为了在 retina 屏上获得清晰的显示效果，我们将 Canvas 的宽高增加一倍，然后通过 `transform: scale(0.5)` 来缩小到匹配容器宽高。

```
#container canvas{
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%) scale(0.5);
}

```

由于 Canvas 的定位是 absolute，它本身的默认宽高并不等于容器的宽高，需要通过 JavaScript 设置。

```
let width = 2 * container.getBoundingClientRect().width;
canvas.width = canvas.height = width;

```

使用上面的代码，我们就可以通过在 Canvas 上绘制实心圆和连线来实现 UI 了。具体的方法，我下面会详细来讲。

最后，我们来看一下使用 SVG 的绘制方法。不过，由于 SVG 原生操作的 API 不是很方便，我们可以使用了 [Snap.svg 库](http://snapsvg.io/)，实现起来和使用 Canvas 大同小异，我就不详细来说了。但是，SVG 的问题是移动端兼容性不如 DOM 和 Canvas 好，所以综合上面三者的情况，我最终选择使用 Canvas 来实现。

## 结构设计

使用 Canvas 实现的话， DOM 结构就比较简单了。为了实现响应式，我们需要实现一个自适应宽度的正方形容器，方法前面已经讲过了，然后我们在容器中创建 Canvas。

这里需要注意的一点是，我们应当把 Canvas 分层。这是因为 Canvas 的渲染机制里，要更新画布的内容，需要刷新要更新的区域重新绘制。因此我们有必要把频繁变化的内容和基本不变的内容分层管理，这样能显著提升性能。

在这里我把 UI 分别绘制在 3 个图层里，对应 3 个 Canvas。最上层只有随着手指头移动的那个线段，中间是九个点，最下层是已经绘制好的线。之所以这样分，是因为随手指头移动的那条线需要不断刷新，底下两层都不用频繁更新，但是把连好的线放在最底层是因为我要做出圆点把线的一部分遮挡住的效果。

![](https://static001.geekbang.org/resource/image/cf/93/cf14330f6f0149252afb57ccb991a293.jpeg?wh=1920*1080)

接着，我们确定圆点的位置。

![](https://static001.geekbang.org/resource/image/f7/bd/f731ffa24422655e218b7f362385f6bd.jpeg?wh=1920*1080)

圆点的位置有两种定位法，第一种是九个九宫格，圆点在小九宫格的中心位置。认真的同学肯定已经发现了，在前面 DOM 方案里，我们就是采用这样的方式。这个时候，圆点的直径为 11.1%。第二种方式是用横竖三条线把宽高四等分，圆点在这些线的交点处。

在 Canvas 里我们采用第二种方法来确定圆点（代码里的 n = 3）。

```
let range = Math.round(width / (n + 1));

let circles = [];

//drawCircleCenters
for(let i = 1; i <= n; i++){
  for(let j = 1; j <= n; j++){
    let y = range * i, x = range * j;
    drawSolidCircle(circleCtx, fgColor, x, y, innerRadius);
    let circlePoint = {x, y};
    circlePoint.pos = [i, j];
    circles.push(circlePoint);
  }

```

最后一点严格说不属于结构设计，但因为我们的 UI 是通过触屏操作，所以我们需要考虑 Touch 事件处理和坐标的转换。

```
function getCanvasPoint(canvas, x, y){
  let rect = canvas.getBoundingClientRect();
  return {
    x: 2 * (x - rect.left),
    y: 2 * (y - rect.top),
  };
}

```

我们将 Touch 相对于屏幕的坐标转换为 Canvas 相对于画布的坐标。代码里的 2 倍是因为我们前面说了要让 retina 屏下清晰，我们将 Canvas 放大为原来的 2 倍。

## API 设计

接下来我们需要设计给使用者使用的 API 了。在这里，我们将组件功能分解一下，独立出一个单纯记录手势的 Recorder。将组件功能分解为更加底层的组件，是一种简化组件设计的常用模式。

![](https://static001.geekbang.org/resource/image/53/df/53c4bb35522954095ca736bdf6d86edf.jpeg?wh=1920*1080)

我们抽取出底层的 Recorder，让 Locker 继承 Recorder，Recorder 负责记录，Locker 管理实际的设置和验证密码的过程。

我们的 Recorder 只负责记录用户行为，由于用户操作是异步操作，我们将它设计为 Promise 规范的 API，它可以以如下方式使用：

```
var recorder = new HandLock.Recorder({
  container: document.querySelector('#main')
});

function recorded(res){
  if(res.err){
    console.error(res.err);
    recorder.clearPath();
    if(res.err.message !== HandLock.Recorder.ERR_USER_CANCELED){
      recorder.record().then(recorded);
    }
  }else{
    console.log(res.records);
    recorder.record().then(recorded);
  }
}

recorder.record().then(recorded)

```

对于输出结果，我们简单用选中圆点的行列坐标拼接起来得到一个唯一的序列。例如 “11121323” 就是如下选择图形：

![](https://static001.geekbang.org/resource/image/82/b8/82500410b843734363a9c49d6f3b5fb8.jpeg?wh=1920*1080)

为了让 UI 显示具有灵活性，我们还可以将外观配置抽取出来。

```
const defaultOptions = {
  container: null, //创建canvas的容器，如果不填，自动在 body 上创建覆盖全屏的层
  focusColor: '#e06555',  //当前选中的圆的颜色
  fgColor: '#d6dae5',     //未选中的圆的颜色
  bgColor: '#fff',        //canvas背景颜色
  n: 3, //圆点的数量： n x n
  innerRadius: 20,  //圆点的内半径
  outerRadius: 50,  //圆点的外半径，focus 的时候显示
  touchRadius: 70,  //判定touch事件的圆半径
  render: true,     //自动渲染
  customStyle: false, //自定义样式
  minPoints: 4,     //最小允许的点数
};

```

这样，我们实现完整的 Recorder 对象，核心代码如下：

```
[...] //定义一些私有方法

const defaultOptions = {
  container: null, //创建canvas的容器，如果不填，自动在 body 上创建覆盖全屏的层
  focusColor: '#e06555',  //当前选中的圆的颜色
  fgColor: '#d6dae5',     //未选中的圆的颜色
  bgColor: '#fff',        //canvas背景颜色
  n: 3, //圆点的数量： n x n
  innerRadius: 20,  //圆点的内半径
  outerRadius: 50,  //圆点的外半径，focus 的时候显示
  touchRadius: 70,  //判定touch事件的圆半径
  render: true,     //自动渲染
  customStyle: false, //自定义样式
  minPoints: 4,     //最小允许的点数
};

export default class Recorder{
  static get ERR_NOT_ENOUGH_POINTS(){
    return 'not enough points';
  }
  static get ERR_USER_CANCELED(){
    return 'user canceled';
  }
  static get ERR_NO_TASK(){
    return 'no task';
  }
  constructor(options){
    options = Object.assign({}, defaultOptions, options);

    this.options = options;
    this.path = [];

    if(options.render){
      this.render();
    }
  }
  render(){
    if(this.circleCanvas) return false;

    let options = this.options;
    let container = options.container || document.createElement('div');

    if(!options.container && !options.customStyle){
      Object.assign(container.style, {
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        lineHeight: '100%',
        overflow: 'hidden',
        backgroundColor: options.bgColor
      });
      document.body.appendChild(container);
    }
    this.container = container;

    let {width, height} = container.getBoundingClientRect();

    //画圆的 canvas，也是最外层监听事件的 canvas
    let circleCanvas = document.createElement('canvas');

    //2 倍大小，为了支持 retina 屏
    circleCanvas.width = circleCanvas.height = 2 * Math.min(width, height);
    if(!options.customStyle){
      Object.assign(circleCanvas.style, {
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%) scale(0.5)',
      });
    }

    //画固定线条的 canvas
    let lineCanvas = circleCanvas.cloneNode(true);

    //画不固定线条的 canvas
    let moveCanvas = circleCanvas.cloneNode(true);

    container.appendChild(lineCanvas);
    container.appendChild(moveCanvas);
    container.appendChild(circleCanvas);

    this.lineCanvas = lineCanvas;
    this.moveCanvas = moveCanvas;
    this.circleCanvas = circleCanvas;

    this.container.addEventListener('touchmove',
      evt => evt.preventDefault(), {passive: false});

    this.clearPath();
    return true;
  }
  clearPath(){
    if(!this.circleCanvas) this.render();

    let {circleCanvas, lineCanvas, moveCanvas} = this,
        circleCtx = circleCanvas.getContext('2d'),
        lineCtx = lineCanvas.getContext('2d'),
        moveCtx = moveCanvas.getContext('2d'),
        width = circleCanvas.width,
        {n, fgColor, innerRadius} = this.options;

    circleCtx.clearRect(0, 0, width, width);
    lineCtx.clearRect(0, 0, width, width);
    moveCtx.clearRect(0, 0, width, width);

    let range = Math.round(width / (n + 1));

    let circles = [];

    //drawCircleCenters
    for(let i = 1; i <= n; i++){
      for(let j = 1; j <= n; j++){
        let y = range * i, x = range * j;
        drawSolidCircle(circleCtx, fgColor, x, y, innerRadius);
        let circlePoint = {x, y};
        circlePoint.pos = [i, j];
        circles.push(circlePoint);
      }
    }

    this.circles = circles;
  }
  async cancel(){
    if(this.recordingTask){
      return this.recordingTask.cancel();
    }
    return Promise.resolve({err: new Error(Recorder.ERR_NO_TASK)});
  }
  async record(){
    if(this.recordingTask) return this.recordingTask.promise;

    let {circleCanvas, lineCanvas, moveCanvas, options} = this,
        circleCtx = circleCanvas.getContext('2d'),
        lineCtx = lineCanvas.getContext('2d'),
        moveCtx = moveCanvas.getContext('2d');

    circleCanvas.addEventListener('touchstart', ()=>{
      this.clearPath();
    });

    let records = [];

    let handler = evt => {
      let {clientX, clientY} = evt.changedTouches[0],
          {bgColor, focusColor, innerRadius, outerRadius, touchRadius} = options,
          touchPoint = getCanvasPoint(moveCanvas, clientX, clientY);

      for(let i = 0; i < this.circles.length; i++){
        let point = this.circles[i],
            x0 = point.x,
            y0 = point.y;

        if(distance(point, touchPoint) < touchRadius){
          drawSolidCircle(circleCtx, bgColor, x0, y0, outerRadius);
          drawSolidCircle(circleCtx, focusColor, x0, y0, innerRadius);
          drawHollowCircle(circleCtx, focusColor, x0, y0, outerRadius);

          if(records.length){
            let p2 = records[records.length - 1],
                x1 = p2.x,
                y1 = p2.y;

            drawLine(lineCtx, focusColor, x0, y0, x1, y1);
          }

          let circle = this.circles.splice(i, 1);
          records.push(circle[0]);
          break;
        }
      }

      if(records.length){
        let point = records[records.length - 1],
            x0 = point.x,
            y0 = point.y,
            x1 = touchPoint.x,
            y1 = touchPoint.y;

        moveCtx.clearRect(0, 0, moveCanvas.width, moveCanvas.height);
        drawLine(moveCtx, focusColor, x0, y0, x1, y1);
      }
    };

    circleCanvas.addEventListener('touchstart', handler);
    circleCanvas.addEventListener('touchmove', handler);

    let recordingTask = {};
    let promise = new Promise((resolve, reject) => {
      recordingTask.cancel = (res = {}) => {
        let promise = this.recordingTask.promise;

        res.err = res.err || new Error(Recorder.ERR_USER_CANCELED);
        circleCanvas.removeEventListener('touchstart', handler);
        circleCanvas.removeEventListener('touchmove', handler);
        document.removeEventListener('touchend', done);
        resolve(res);
        this.recordingTask = null;

        return promise;
      }

      let done = evt => {
        moveCtx.clearRect(0, 0, moveCanvas.width, moveCanvas.height);
        if(!records.length) return;

        circleCanvas.removeEventListener('touchstart', handler);
        circleCanvas.removeEventListener('touchmove', handler);
        document.removeEventListener('touchend', done);

        let err = null;

        if(records.length < options.minPoints){
          err = new Error(Recorder.ERR_NOT_ENOUGH_POINTS);
        }

        //这里可以选择一些复杂的编码方式，本例子用最简单的直接把坐标转成字符串
        let res = {err, records: records.map(o => o.pos.join('')).join('')};

        resolve(res);
        this.recordingTask = null;
      };
      document.addEventListener('touchend', done);
    });

    recordingTask.promise = promise;

    this.recordingTask

```

这里有几个公开的方法，分别是ecorder 负责记录绘制结果， clearPath 负责在画布上清除上一次记录的结果，cancel 负责终止记录过程，这是为后续流程准备的。

## 流程设计

接下来，我们基于 Recorder 来设计设置和验证密码的流程：

首先是验证密码的流程：

![](https://static001.geekbang.org/resource/image/c1/3c/c1e94603bfb1d26a0b354377095b6f3c.jpeg?wh=1920*1080)

其次是设置密码的流程：

![](https://static001.geekbang.org/resource/image/da/3a/da4509d380c71e30bdd03ec27c000e3a.jpeg?wh=1920*1080)

有了前面异步 Promise API 的 Recorder，我们不难实现上面的两个流程。

**验证密码的内部流程**

```
async check(password){
  if(this.mode !== Locker.MODE_CHECK){
    await this.cancel();
    this.mode = Locker.MODE_CHECK;
  }

  let checked = this.options.check.checked;

  let res = await this.record();

  if(res.err && res.err.message === Locker.ERR_USER_CANCELED){
    return Promise.resolve(res);
  }

  if(!res.err && password !== res.records){
    res.err = new Error(Locker.ERR_PASSWORD_MISMATCH)
  }

  checked.call(this, res);
  this.check(password);
  return Promise.resolve(res

```

**设置密码的内部流程**

```
async update(){
  if(this.mode !== Locker.MODE_UPDATE){
    await this.cancel();
    this.mode = Locker.MODE_UPDATE;
  }

  let beforeRepeat = this.options.update.beforeRepeat,
      afterRepeat = this.options.update.afterRepeat;

  let first = await this.record();

  if(first.err && first.err.message === Locker.ERR_USER_CANCELED){
    return Promise.resolve(first);
  }

  if(first.err){
    this.update();
    beforeRepeat.call(this, first);
    return Promise.resolve(first);
  }

  beforeRepeat.call(this, first);

  let second = await this.record();

  if(second.err && second.err.message === Locker.ERR_USER_CANCELED){
    return Promise.resolve(second);
  }

  if(!second.err && first.records !== second.records){
    second.err = new Error(Locker.ERR_PASSWORD_MISMATCH);
  }

  this.update();
  afterRepeat.call(this, second);
  return Promise.resolve(se

```

我们可以看到，有了 Recorder 之后，Locker 的验证和设置密码基本上就是顺着流程用 async/await 写下来就行了。

另外，我们还要注意一些细节问题。由于实际在手机上触屏时，如果上下拖动，浏览器的默认行为会导致页面上下移动，因此我们需要阻止 touchmove 的默认事件。

```
this.container.addEventListener('touchmove',
      evt => evt.preventDefault(), {passive: false});

```

touchmove 事件在 Chrome 下默认是一个 [Passive Event](https://dom.spec.whatwg.org/#in-passive-listener-flag)，因此，我们addEventListener 的时候需要传参 {passive: false}，否则就不能 preventDefault。

此外，因为我们的代码使用了 ES6+，所以需要引入 babel 编译，我们的组件也使用 webpack 进行打包，以便于使用者在浏览器中直接引入。

## 要点总结

今天，我和你一起完成了前几天留下的“手势密码”实战题。通过解决这几道题，我希望你能记住这三件事：

1. 在设计 API 的时候思考真正的需求，判断什么该开放、什么该封装
2. 做好技术调研和核心方案研究，选择合适的方案
3. 着手优化和解决细节问题，要站在API使用者的角度思考

* * *

## 源码

[GitHub 工程](https://github.com/akira-cn/handlock)