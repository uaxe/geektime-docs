你好，我是大圣。

上一讲我们学习了下一代Vuex框架Pinia的原理，今天我来带你分析Vue生态中另外一个重要的框架vue-router的源码。

课程中我们也实现过一个迷你的router，我们通过监听路由的变化，把路由数据包裹成响应式对象后，一旦路由发生变化，我们就去定义好的路由数据中查询当前路由对应的组件，在router-view中渲染即可。今天我们就进入到vue-router源码的内部，看一下实际的vue-router和我们实现的迷你版本有什么区别。

## vue-router入口分析

vue-router提供了createRouter方法来创建路由配置，我们传入每个路由地址对应的组件后，使用app.use在Vue中加载vue-router插件，并且给Vue注册了两个内置组件，router-view负责渲染当前路由匹配的组件，router-link负责页面的跳转。

**我们先来看下createRouter如何实现**，完整的代码你可以在 [GitHub](https://github.com/vuejs/vue-router-next/blob/master/src/router.ts#L355) 上看到。这个函数比较长，还好我们有TypeScript，我们先看下createRouter的参数。

在下面的代码中，参数RouterOptions是规范我们配置的路由对象，主要包含history、routes等数据。routes就是我们需要配置的路由对象，类型是RouteRecordRaw组成的数组，并且RouteRecordRaw的类型是三个类型的合并。然后返回值的类型Router就是包含了addRoute、push、beforeEnter、install方法的一个对象， **并且维护了currentRoute和options两个属性**。

并且每个类型方法还有详细的注释，这也极大降低了阅读源码的门槛，可以帮助我们在看到函数的类型时就知道函数大概的功能。我们知道Vue中app.use实际上执行的就是router对象内部的install方法，我们先进入到install方法看下是如何安装的。

```javascript
// createRouter传递参数的类型
export interface RouterOptions extends PathParserOptions {
  history: RouterHistory
  routes: RouteRecordRaw[]
  scrollBehavior?: RouterScrollBehavior
  ...
}
// 每个路由配置的类型
export type RouteRecordRaw =
  | RouteRecordSingleView
  | RouteRecordMultipleViews
  | RouteRecordRedirect

//... other config
// Router接口的全部方法和属性
export interface Router {
  readonly currentRoute: Ref<RouteLocationNormalizedLoaded>
  readonly options: RouterOptions

  addRoute(parentName: RouteRecordName, route: RouteRecordRaw): () => void
  addRoute(route: RouteRecordRaw): () => void
  Route(name: RouteRecordName): void
  hasRoute(name: RouteRecordName): boolean

  getRoutes(): RouteRecord[]
  resolve(
    to: RouteLocationRaw,
    currentLocation?: RouteLocationNormalizedLoaded
  ): RouteLocation & { href: string }
  push(to: RouteLocationRaw): Promise<NavigationFailure | void | undefined>
  replace(to: RouteLocationRaw): Promise<NavigationFailure | void | undefined>
  back(): ReturnType<Router['go']>
  forward(): ReturnType<Router['go']>
  go(delta: number): void
  beforeEach(guard: NavigationGuardWithThis<undefined>): () => void
  beforeResolve(guard: NavigationGuardWithThis<undefined>): () => void
  afterEach(guard: NavigationHookAfter): () => void
  onError(handler: _ErrorHandler): () => void
  isReady(): Promise<void>
  install(app: App): void
}

export function createRouter(options: RouterOptions): Router {

}

```

## 路由安装

从下面的代码中我们可以看到，在createRouter的最后，创建了包含addRoute、push等方法的对象，并且install方法内部注册了RouterLink和RouterView两个组件。所以我们可以在任何组件内部直接使用<router-view>和<router-link>组件，然后注册全局变量 $router 和 $route，其中 $router就是我们通过createRouter返回的路由对象，包含addRoute、push等方法，$route使用defineProperty的形式返回currentRoute的值，可以做到和currentRoute值同步。

然后使用computed把路由变成响应式对象，存储在reactiveRoute对象中，再通过app.provide给全局注册了route和reactive包裹后的reactiveRoute对象。我们之前介绍provide函数的时候也介绍了，provide提供的数据并没有做响应式的封装， **需要响应式的时候需要自己使用ref或者reactive封装为响应式对象**，最后注册unmount方法实现vue-router的安装。

```javascript
export function createRouter(options: RouterOptions): Router {
....
  let started: boolean | undefined
  const installedApps = new Set<App>()
  // 路由对象
  const router: Router = {
    currentRoute,

    addRoute,
    removeRoute,
    hasRoute,
    getRoutes,
    resolve,
    options,

    push,
    replace,
    go,
    back: () => go(-1),
    forward: () => go(1),

    beforeEach: beforeGuards.add,
    beforeResolve: beforeResolveGuards.add,
    afterEach: afterGuards.add,

    onError: errorHandlers.add,
    isReady,
    // 插件按章
    install(app: App) {
      const router = this
      // 注册全局组件 router-link和router-view
      app.component('RouterLink', RouterLink)
      app.component('RouterView', RouterView)

      app.config.globalProperties.$router = router
      Object.defineProperty(app.config.globalProperties, '$route', {
        enumerable: true,
        get: () => unref(currentRoute),
      })
      if (
        isBrowser &&
        !started &&
        currentRoute.value === START_LOCATION_NORMALIZED
      ) {
        // see above
        started = true
        push(routerHistory.location).catch(err => {
          if (__DEV__) warn('Unexpected error when starting the router:', err)
        })
      }

      const reactiveRoute = {} as {
        [k in keyof RouteLocationNormalizedLoaded]: ComputedRef<
          RouteLocationNormalizedLoaded[k]
        >
      }
      for (const key in START_LOCATION_NORMALIZED) {
        // @ts-expect-error: the key matches
        reactiveRoute[key] = computed(() => currentRoute.value[key])
      }
      // 提供全局配置
      app.provide(routerKey, router)
      app.provide(routeLocationKey, reactive(reactiveRoute))
      app.provide(routerViewLocationKey, currentRoute)

      const unmountApp = app.unmount
      installedApps.add(app)
      app.unmount = function () {
        installedApps.delete(app)
        // ...
        unmountApp()
      }

      if ((__DEV__ || __FEATURE_PROD_DEVTOOLS__) && isBrowser) {
        addDevtools(app, router, matcher)
      }
    },
  }

  return router
}

```

路由对象创建和安装之后，我们 **下一步需要了解的就是router-link和router-view两个组件的实现方式**。

通过下面的代码我们可以看到，RouterView的setup函数返回了一个函数，这个函数就是RouterView组件的render函数。大部分我们使用的方式就是一个<router-view />组件，没有slot情况下返回的就是component变量。component使用h函数返回ViewComponent的虚拟DOM，而ViewComponent是根据matchedRoute.components\[props.name\]计算而来。

matchedRoute依赖的matchedRouteRef的计算逻辑在如下代码的第12～15行，数据来源injectedRoute就是上面我们注入的currentRoute对象。

```javascript
export const RouterViewImpl = /*#__PURE__*/ defineComponent({
  name: 'RouterView',
  props: {
    name: {
      type: String as PropType<string>,
      default: 'default',
    },
    route: Object as PropType<RouteLocationNormalizedLoaded>,
  },
  // router-view组件源码
  setup(props, { attrs, slots }) {
    // 全局的reactiveRoute对象注入
    const injectedRoute = inject(routerViewLocationKey)!

    const routeToDisplay = computed(() => props.route || injectedRoute.value)
    const depth = inject(viewDepthKey, 0)
    const matchedRouteRef = computed<RouteLocationMatched | undefined>(
      () => routeToDisplay.value.matched[depth]
    )
    // 嵌套层级
    provide(viewDepthKey, depth + 1)
    // 匹配的router对象
    provide(matchedRouteKey, matchedRouteRef)
    provide(routerViewLocationKey, routeToDisplay)

    const viewRef = ref<ComponentPublicInstance>()
    // 返回的render函数
    return () => {
      const route = routeToDisplay.value
      const matchedRoute = matchedRouteRef.value
      const ViewComponent = matchedRoute && matchedRoute.components[props.name]
      const currentName = props.name

      if (!ViewComponent) {
        return normalizeSlot(slots.default, { Component: ViewComponent, route })
      }

      // props from route configuration
      const routePropsOption = matchedRoute!.props[props.name]
      const routeProps = routePropsOption
        ? routePropsOption === true
          ? route.params
          : typeof routePropsOption === 'function'
          ? routePropsOption(route)
          : routePropsOption
        : null

      const onVnodeUnmounted: VNodeProps['onVnodeUnmounted'] = vnode => {
        // remove the instance reference to prevent leak
        if (vnode.component!.isUnmounted) {
          matchedRoute!.instances[currentName] = null
        }
      }
      // 创建需要渲染组件的虚拟dom
      const component = h(
        ViewComponent,
        assign({}, routeProps, attrs, {
          onVnodeUnmounted,
          ref: viewRef,
        })
      )

      return (
        // pass the vnode to the slot as a prop.
        // h and <component :is="..."> both accept vnodes
        normalizeSlot(slots.default, { Component: component, route }) ||
        component
      )
    }
  },
})

```

## 路由更新

到这我们可以看出，RouterView渲染的组件是由当前匹配的路由变量matchedRoute决定的。接下来我们回到createRouter函数中，可以看到matcher对象是由createRouterMatcher创建，createRouterMatcher函数传入routes配置的路由数组，并且返回创建的RouterMatcher对象，内部遍历routes数组，通过addRoute挨个处理路由配置。

```javascript
export function createRouter(options: RouterOptions): Router {
  const matcher = createRouterMatcher(options.routes, options)
  ///....
}
export function createRouterMatcher(
  routes: RouteRecordRaw[],
  globalOptions: PathParserOptions
): RouterMatcher {
  // matchers数组
  const matchers: RouteRecordMatcher[] = []
  // matcher对象
  const matcherMap = new Map<RouteRecordName, RouteRecordMatcher>()
  globalOptions = mergeOptions(
    { strict: false, end: true, sensitive: false } as PathParserOptions,
    globalOptions
  )
  function addRoute(){}
  function remoteRoute(){}
  function getRoutes(){
    return matchers
  }
  function insertMatcher(){}
  function resolve(){}
  // add initial routes
  routes.forEach(route => addRoute(route))

  return { addRoute, resolve, removeRoute, getRoutes, getRecordMatcher }
}

```

在下面的代码中我们可以看到，addRoute函数内部通过createRouteRecordMatcher创建扩展之后的matcher对象，包括了record、parent、children等树形，可以很好地描述路由之间的嵌套父子关系。这样整个路由对象就已经创建完毕，那我们如何在路由切换的时候寻找到正确的路由对象呢？

```javascript
function addRoute(
  record: RouteRecordRaw,
  parent?: RouteRecordMatcher,
  originalRecord?: RouteRecordMatcher
){
  if ('alias' in record) {
    // 标准化alias
  }
  for (const normalizedRecord of normalizedRecords) {
    // ...
    matcher = createRouteRecordMatcher(normalizedRecord, parent, options)
    insertMatcher(matcher)

  }
  return originalMatcher
    ? () => {
        // since other matchers are aliases, they should be removed by the original matcher
        removeRoute(originalMatcher!)
      }
    : noop

}

export function createRouteRecordMatcher(
  record: Readonly<RouteRecord>,
  parent: RouteRecordMatcher | undefined,
  options?: PathParserOptions
): RouteRecordMatcher {
  const parser = tokensToParser(tokenizePath(record.path), options)
  const matcher: RouteRecordMatcher = assign(parser, {
    record,
    parent,
    // these needs to be populated by the parent
    children: [],
    alias: [],
  })

  if (parent) {
    if (!matcher.record.aliasOf === !parent.record.aliasOf)
      parent.children.push(matcher)
  }

  return matcher
}

```

在vue-router中，路由更新可以通过router-link渲染的链接实现，也可以使用router对象的push等方法实现。下面的代码中，router-link组件内部也是渲染一个a标签，并且注册了a标签的onClick函数，内部也是通过router.replace或者router.push来实现。

```javascript

export const RouterLinkImpl = /*#__PURE__*/ defineComponent({
  name: 'RouterLink',
  props: {
    to: {
      type: [String, Object] as PropType<RouteLocationRaw>,
      required: true,
    },
      ...
  },
  // router-link源码
  setup(props, { slots }) {
    const link = reactive(useLink(props))
    const { options } = inject(routerKey)!

    const elClass = computed(() => ({
      ...
    }))

    return () => {
      const children = slots.default && slots.default(link)
      return props.custom
        ? children
        : h(
            'a',
            {
              href: link.href,
              onClick: link.navigate,
              class: elClass.value,
            },
            children
          )
    }
  },
})
//  跳转
  function navigate(
    e: MouseEvent = {} as MouseEvent
  ): Promise<void | NavigationFailure> {
    if (guardEvent(e)) {
      return router[unref(props.replace) ? 'replace' : 'push'](
        unref(props.to)
        // avoid uncaught errors are they are logged anyway
      ).catch(noop)
    }
    return Promise.resolve()
  }

```

现在我们回到createRouter函数中，可以看到push函数直接调用了pushWithRedirect函数来实现，内部通过resolve(to)生成targetLocation变量。这个变量会赋值给toLocation，然后执行navigate(toLocation)函数。而 **这个函数内部会执行一系列的导航守卫函数**，最后会执行finalizeNavigation函数完成导航。

```javascript
function push(to: RouteLocationRaw | RouteLocation) {
  return pushWithRedirect(to)
}

function replace(to: RouteLocationRaw | RouteLocationNormalized) {
  return push(assign(locationAsObject(to), { replace: true }))
}
// 路由跳转函数
function pushWithRedirect(
  to: RouteLocationRaw | RouteLocation,
  redirectedFrom?: RouteLocation
): Promise<NavigationFailure | void | undefined> {
  const targetLocation: RouteLocation = (pendingLocation = resolve(to))
  const from = currentRoute.value
  const data: HistoryState | undefined = (to as RouteLocationOptions).state
  const force: boolean | undefined = (to as RouteLocationOptions).force
  // to could be a string where `replace` is a function
  const replace = (to as RouteLocationOptions).replace === true

  const toLocation = targetLocation as RouteLocationNormalized


  return (failure ? Promise.resolve(failure) : navigate(toLocation, from))
    .catch((error: NavigationFailure | NavigationRedirectError) =>
      isNavigationFailure(error)
        ? error
        : // reject any unknown error
          triggerError(error, toLocation, from)
    )
    .then((failure: NavigationFailure | NavigationRedirectError | void) => {

        failure = finalizeNavigation(
          toLocation as RouteLocationNormalizedLoaded,
          from,
          true,
          replace,
          data
        )

      triggerAfterEach(
        toLocation as RouteLocationNormalizedLoaded,
        from,
        failure
      )
      return failure
    })
}

```

在下面的代码中我们可以看到，finalizeNavigation函数内部通过routerHistory.push或者replace实现路由跳转，并且更新currentRoute.value。

currentRoute就是我们在install方法中注册的全局变量 $route，每次页面跳转currentRoute都会更新为toLocation，在任意组件中都可以通过 $route变量来获取当前路由的数据， **最后在handleScroll设置滚动行为**。

routerHistory在createRouter中通过option.history获取，就是我们创建vue-router应用时通过createWebHistory或者createWebHashHistory创建的对象。createWebHistory返回的是HTML5的history模式路由对象，createWebHashHistory是Hash模式的路由对象。

```javascript
  function finalizeNavigation(
    toLocation: RouteLocationNormalizedLoaded,
    from: RouteLocationNormalizedLoaded,
    isPush: boolean,
    replace?: boolean,
    data?: HistoryState
  ): NavigationFailure | void {

    const isFirstNavigation = from === START_LOCATION_NORMALIZED
    const state = !isBrowser ? {} : history.state

    if (isPush) {

      if (replace || isFirstNavigation)
        routerHistory.replace(
          toLocation.fullPath
        )
      else routerHistory.push(toLocation.fullPath, data)
    }

    // accept current navigation
    currentRoute.value = toLocation
    handleScroll(toLocation, from, isPush, isFirstNavigation)

    markAsReady()
  }

  function markAsReady(err?: any): void {
    if (ready) return
    ready = true
    setupListeners()
    readyHandlers
      .list()
      .forEach(([resolve, reject]) => (err ? reject(err) : resolve()))
    readyHandlers.reset()
  }

```

下面的代码中我们可以看到，createWebHashHistory和createWebHistory的实现，内部都是通过useHistoryListeners实现路由的监听，通过useHistoryStateNavigation实现路由的切换。useHistoryStateNavigation会返回push或者replace方法来更新路由，这两个函数你可以在 [GitHub](https://github.com/vuejs/router/blob/main/packages/router/src/history/html5.ts) 上自行学习。

```javascript
export function createWebHashHistory(base?: string): RouterHistory {
  base = location.host ? base || location.pathname + location.search : ''
  // allow the user to provide a `#` in the middle: `/base/#/app`
  if (!base.includes('#')) base += '#'
  return createWebHistory(base)
}

export function createWebHistory(base?: string): RouterHistory {
  base = normalizeBase(base)

  const historyNavigation = useHistoryStateNavigation(base)
  const historyListeners = useHistoryListeners(
    base,
    historyNavigation.state,
    historyNavigation.location,
    historyNavigation.replace
  )
  function go(delta: number, triggerListeners = true) {
    if (!triggerListeners) historyListeners.pauseListeners()
    history.go(delta)
  }

  const routerHistory: RouterHistory = assign(
    {
      // it's overridden right after
      location: '',
      base,
      go,
      createHref: createHref.bind(null, base),
    },

    historyNavigation,
    historyListeners
  )

  Object.defineProperty(routerHistory, 'location', {
    enumerable: true,
    get: () => historyNavigation.location.value,
  })

  Object.defineProperty(routerHistory, 'state', {
    enumerable: true,
    get: () => historyNavigation.state.value,
  })

  return routerHistory
}

```

## 总结

以上就是今天的主要内容，我们来总结一下。

这节课我们进入到vue-router的源码中分析了vue-router内部的执行逻辑，其实我们之前课上已经实现了迷你的vue-router，在掌握了前端路由实现的原理后，再来看实际的vue-router源码难度会下降不少。

首先我们分析了createRouter函数入口函数，createRouter函数返回了router对象，router对象提供了addRoute、push等方法，并且在install方法中实现了路由，注册了组件router-link和router-view。

然后通过createRouterMatcher创建路由匹配对象，并且在路由变化的时候维护currentRoute，让你可以在每个组件内部$router和$route获取路由匹配的数据，并且动态渲染当前路由匹配的组件到router-view组件内部，实现了前端的路由系统。

这一讲我们也能感受到，一个玩具的router和实际的vue-router的距离，也能体会到TypeScript在我们阅读代码时的好处。我们阅读源码的目的之一，就是要学习和模仿优秀框架内部的设计思路，然后去优化自己项目中的代码，学会模仿也是一个优秀程序员的优秀品质。

## 思考

最后留给你一个思考题，navigate函数负责执行路由守卫的功能，你知道它的内部是如何实现的吗？

欢迎在评论区分享你的答案，我们下一讲再见！