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
import { AppStorageV2, promptAction, Router, window } from "@kit.ArkUI"
import {
  logger, NewsArticle, NewsListAPI, ServerHealthAPI, WINDOW_WIDTH, WinWidth
} from "common"

const START_PAGE_TAGE = 'StartPage:  '

@Entry
@ComponentV2
struct StarPage {
  uiRouter: Router = this.getUIContext().getRouter()
  @Local winWidth: number = 0
  @Local fontsize: number = 0

  async aboutToAppear(): Promise<void> {
    window.getLastWindow(this.getUIContext().getHostContext())
    const width: number = (AppStorageV2.connect(WinWidth, WINDOW_WIDTH)?.value) ?? 350
    this.winWidth = this.getUIContext().px2vp(width)
    logger.debug(`${START_PAGE_TAGE}winWidth: ${this.winWidth}`)
    this.updateFontSize()
    let isServerReady: boolean = false
    setTimeout(() => {
      logger.debug(START_PAGE_TAGE + '延时跳转')
      this.uiRouter.pushUrl({ url: "pages/Index", recoverable: false })
      // 为了能触发路由动画特此使用push
      logger.debug(START_PAGE_TAGE + '清理启动页')
      this.uiRouter.clear()
    }, 2000)
    await ServerHealthAPI.isServerReady().then((res: boolean) => {
      logger.debug(START_PAGE_TAGE + res.valueOf())
      if (res) {
        isServerReady = true
        logger.info(START_PAGE_TAGE + '服务端准备就绪isServerReady=' + isServerReady)
      } else {
        isServerReady = false
        logger.info(START_PAGE_TAGE + '服务端准备中isServerReady=' + isServerReady)
      }
    })
    if (isServerReady) {
      logger.debug(START_PAGE_TAGE + '尝试获取全部新闻列表')
      NewsListAPI.getAllNews().then((res: NewsArticle[] | null) => {
        if (res === null) {
          logger.warn(START_PAGE_TAGE + '')
        } else {
          promptAction.openToast({ message: '获取新闻列表成功', duration: 2000 })
        }
      })
    }
  }

  pageTransition() {
    PageTransitionExit({ type: RouteType.None, duration: 200, curve: Curve.EaseInOut })
      .slide(SlideEffect.Left)
  }

  updateFontSize() {
    const num = 16
    this.fontsize = (Math.floor((this.winWidth) / num)) + 20
  }

  build() {

    Column() {
      Image($r('app.media.logo'))
        .width('20%')
        .margin({ bottom: 100 })
      Text('Welcome To')
        .fontSize((this.fontsize * 0.8))
        .fontColor('#ff00be53')
      Text('NowInOpenHarmony')
        .fontSize(this.fontsize)
        .fontColor('#ff00be53')
        .fontWeight(700)
    }
    .expandSafeArea()
    .backgroundColor('#062872')
    .justifyContent(FlexAlign.Center)
    .width('100%')
    .height('100%')

  }
}