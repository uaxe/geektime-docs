你好，我是建元。

上节课，我们讲了空间音频的基本概念，以及空间音频是如何采集和播放的。相信你已经基本掌握了空间音频的基本原理。其实在游戏、社交、影视等场景中，空间音频被广泛地应用于构建虚拟的空间环境。

在空间音频的应用里最常见的一种就是“听音辨位”。比如在很多射击游戏中，我们能够通过耳机中目标的脚步、枪声等信息来判断目标的方向。

那么这节课我们就来看看，我们是如何利用HRTF（Head Related Transfer Functions）头相关传递函数来实现“听音辨位”的。

## HRTF简介

上节课我们讲的“双耳效应”实际上就是空间中音源的声波从不同的方向传播到左右耳的路径不同，所以音量、音色、延迟在左右耳会产生不同的变化。

其实这些声波变化的过程就是我们说的声波的空间传递函数，是不是很耳熟？我们在讲回声消除的时候就是通过计算回声的空间传递函数来做回声信号估计的。

那么如果我们预先把空间中不同位置声源的空间传递函数都测量并记录下来，然后利用这个空间传递函数，我们只需要有一个普通的单声道音频以及这个音源和听音者所在虚拟空间中的位置信息，就可以用预先采集好的空间传递函数来渲染出左右耳的声音，从而实现“听音辨位”的功能了。
<div><strong>精选留言（1）</strong></div><ul>
<li><img src="https://static001.geekbang.org/account/avatar/00/2e/86/12/791d0f5e.jpg" width="30px"><span>采夫同志</span> 👍（0） 💬（0）<div>把单通道的音频分别5.0 声道音箱摆放位置所在的五个角度的双耳 HRIR 做卷积，从而渲染出特定方向的声音</div>2022-07-11</li><br/>
</ul>