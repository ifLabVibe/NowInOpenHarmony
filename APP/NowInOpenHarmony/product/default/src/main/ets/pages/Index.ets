/**
 * Copyright (c) 2025 XBXyftx
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import { AppStorageV2, mediaquery } from '@kit.ArkUI'
import {
  BreakpointEnum,
  BreakpointState,
  BreakpointSystem,
  DEVICE_TYPES,
  logger,
  NAV_DESTS,
  NAV_PATH_STUCK,
} from 'common'
import { ColorModChoseButton } from 'feature'
import { MainPage } from './nav_pages/MainPage'
import { deviceInfo } from '@kit.BasicServicesKit'
import { ArticlePage } from './nav_pages/ArticlePage'

const Main_LOG_TAG = 'Main: '

@Entry
@ComponentV2
struct Main {
  @Local navPathStuck: NavPathStack = AppStorageV2.connect(NavPathStack, NAV_PATH_STUCK, () => new NavPathStack())!
  @Local breakpointSystem: BreakpointSystem = BreakpointSystem.getInstance(this.getUIContext())
  @Local navMod: NavigationMode = NavigationMode.Stack
  @Local deviceType: DEVICE_TYPES =
    deviceInfo.deviceType === DEVICE_TYPES.PHONE ? DEVICE_TYPES.PHONE : DEVICE_TYPES.TABLET
  @Local breakPointState: BreakpointState<string> = BreakpointState.of<string>({
    xs: 'xs',
    sm: 'sm',
    xl: 'xl',
    xxl: 'xxl',
    md: 'md',
    lg: 'lg'
  })

  /**
   * 启动页跳转至主页面入场动画
   */
  pageTransition() {
    PageTransitionEnter({ type: RouteType.None, duration: 200, curve: Curve.EaseInOut })
      .scale({ x: 0.2, y: 0.2 })
      .opacity(0)
  }

  /**
   * 横竖屏切换监听器
   */
  orientationMatch() {
    const mediaQueryListener: mediaquery.MediaQueryListener =
      this.getUIContext().getMediaQuery().matchMediaSync('(orientation: landscape)')
    mediaQueryListener.on('change', () => {
      logger.info(`${Main_LOG_TAG}横竖屏发生变化`)
      this.getNavMode()
    })
  }

  /**
   * NavMod切换器函数
   */
  @Monitor('breakPointState.value')
  getNavMode() {
    logger.info(`${Main_LOG_TAG}this.breakPointState.getCurrentBreakPointType() = ${this.breakPointState.getCurrentBreakPointType()}`)
    if (this.getUIContext().getMediaQuery().matchMediaSync('(orientation: landscape)').matches) {
      logger.info(`${Main_LOG_TAG}成功匹配横屏模式`)
      if (this.breakPointState.getCurrentBreakPointType() === BreakpointEnum.xs ||
        this.breakPointState.getCurrentBreakPointType() === BreakpointEnum.sm ||
        this.breakPointState.getCurrentBreakPointType() === BreakpointEnum.md) {
        this.navMod = NavigationMode.Stack
      } else {
        this.navMod = NavigationMode.Split
      }
    } else if (this.getUIContext().getMediaQuery().matchMediaSync('(orientation: portrait)').matches) {
      logger.info(`${Main_LOG_TAG}成功匹配竖屏模式`)
      this.navMod = NavigationMode.Stack
    }
  }

  @Builder
  NavDestMap(name: string) {
    if (name === NAV_DESTS.MAIN) {
      Main()
    }else if (name === NAV_DESTS.ARTICLE) {
      ArticlePage()
    }
  }

  aboutToAppear(): void {
    this.breakpointSystem.attach(this.breakPointState)
    this.breakpointSystem.start()
    this.orientationMatch()
    this.getNavMode()
  }

  build() {
    Stack() {
      Navigation(this.navPathStuck) {
        MainPage()
      }
      .linearGradient({
        angle: 20,
        colors: [
          [$r('app.color.index_page_background_1'), 0],
          [$r('app.color.index_page_background_2'), 0.4],
          [$r('app.color.index_page_background_3'), 0.7],
          [$r('app.color.index_page_background_4'), 1]
        ]
      })
      .title('NowInOpenHarmony')
      // .hideNavBar(true)
      .backgroundColor(Color.Transparent)
      .padding(10)
      .navDestination(this.NavDestMap)
      .hideToolBar(true)
      .height('100%')
      .width('100%')
      .hideBackButton(true)
      .titleMode(NavigationTitleMode.Mini)
      .mode(this.navMod)
      .navBarWidth('40%')

      ColorModChoseButton()
        .position({ right: this.deviceType === DEVICE_TYPES.PHONE ? 20 : 30, bottom: 100 })
    }
  }
}