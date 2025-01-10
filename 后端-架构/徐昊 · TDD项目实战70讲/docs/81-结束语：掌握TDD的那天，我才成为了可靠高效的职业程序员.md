你好，我是徐昊。今天要对线段编辑器这个项目做一个收尾，同时也是我们整门课程的一个收尾。

## 线段编辑器最终的结果

目前，线段编辑器的代码是这样的：

```plain
import Konva from "konva";
export class LineEditor extends Konva.Group {
    private line?: Konva.Line
    private pointsCount: number = 0
    attach(line: Konva.Line) {
        this.line = line
        line.on('pointsChange', () => {
            this.update()
        })
        this.update()
    }
    update() {
        let points = this.line!.points()
        let previous = -1
        for (let i = 0; i < points.length / 2; i++) {
            this.get(i, 'anchor').setAttrs({x: points[i * 2], y: points[i * 2 + 1]})
            if (previous !== -1)
                this.get(i, 'control').setAttrs({
                    x: points[previous * 2] + (points[i * 2] - points[previous * 2]) / 2,
                    y: points[previous * 2 + 1] + (points[i * 2 + 1] - points[previous * 2 + 1]) / 2
                })
            previous = i
        }
        for (let i = points.length / 2; i < this.pointsCount; i++) {
            this.findOne(`.${i}-anchor`).destroy()
            this.findOne(`.${i}-control`).destroy()
        }
        this.pointsCount = points.length / 2
    }
    private get(index: number, type: string) {
        return this.findOne(`.${index}-${type}`) || this.create(index, type)
    }
    private create(index: number, type: string) {
        let point = new Konva.Circle({name: `${index}-${type}`, radius: 10, draggable: true})
        if (type === 'anchor') {
            point.on('dragmove', (e) => {
                let points = this.line!.points()
                points[index * 2] = e.target.x()
                points[index * 2 + 1] = e.target.y()
                this.line!.points(points)
            }).on('dblclick', (e: Konva.KonvaEventObject<MouseEvent>) => {
                let points = this.line!.points()
                points.splice(index * 2, 2)
                this.line!.points(points)
            })
        } else {
            point.on('dragmove', (e) => {
                let points = this.line!.points()
                points.splice(index * 2, 0, e.target.x(), e.target.y())
                this.line!.points(points)
            })
        }
        this.add(point)
        return point
    }
}

```

从始至终，我们都没有调试过这个编辑器实际的行为是什么样子。现在是时候了，让我们来看看它最终的结果是什么样：

## 结束语

到此为止，我们的课程就要结束了，一共是81节课，包含50+小时的视频演示。学习不易，坚持也不易，大家辛苦了！

回顾整个课程，我们从经典学派入手，以参数解析为例，讲解了测试驱动的整体流程。然后在项目一依赖注入容器中，使用经典学派完成了一个具有相当规模的依赖注入框架。

从项目二开始，我们介绍了伦敦学派的做法，也就是在具有明确架构愿景的情况下，如何使用二层分解方式，在保证架构愿景的前提下，以测试驱动的方式完成复杂的功能。

最后的项目四，我们把目光投向了具有更多不确定性的强交互性系统，一个以HTML Canvas为基础的线段编辑器。也正是在项目四中，我们更多地跳出了自动化测试先行（Test First）的测试驱动框架，以 **可测试性** 先行等更基础的原则为指引，做出了稍显“离经叛道“的测试驱动开发。

然而只要铭记两点： **测试驱动开发是从软件的可测试性入手，驱动软件开发的模式**；测试驱动开发的任务分解 **是以如何测试软件而不是如何实现软件** 为切入点的任务分解。那么，看起来“离经叛道”的新手，反而又是非常传统的技法。

让我们回看一下课程的开篇词，我曾经说过，对于测试驱动开发，稍有了解而全无实践的人，会认为是天方夜谭，甚至无法想象为什么需要这样的方式来开发：

1. 为什么要开发人员来写测试？这难道不是测试人员的工作吗？难道开发写了测试，测试人员就不用再测了嘛？
2. 又要写测试，又要写生产代码，效率是不是太低了？只写生产代码效率应该更高吧？
3. 不写测试我也能写出可以工作的软件，那么写测试能给我带来什么额外的好处呢？

相信学完整个课程，这些对于测试驱动开发的常见质疑，已经不再成为你的困惑。那么我也希望你能以具有自己风格的方式，应用测试驱动开发方式，成为更加可靠、高效的职业程序员。

最后，我准备了一份 [毕业问卷](https://jinshuju.net/f/LOxsRi)，希望你能花一两分钟填写一下。

我在开篇词曾经说过，测试驱动开发伴随了我职业生涯的每一个阶段。我相信，我掌握了测试驱动开发那天，我才成为了可靠、高效的职业程序员。

当然，它也是难以掌握的。在近二十年里，我一直尝试通过引入一些实践来降低TDD的学习门槛，以及帮助我们在团队中更有效地推行TDD，包括课程中介绍的任务分解、架构愿景等。

所以这个课是我最新尝试的一个总结，希望你能为我提供一些反馈和建议，这也是我开设这门课的一个初心。就到这里了，我们再会！

![](https://static001.geekbang.org/resource/image/1f/fa/1f49dd0ca82ab7a4c8ea2c3f1102c3fa.jpg?wh=1142x801)