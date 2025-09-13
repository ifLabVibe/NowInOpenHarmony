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

import {
  NEWS_LIST_ITEM_ANIMATE_PARAM,
  DEVICE_TYPES,
  IS_STICKY,
  logger,
  NAV_PATH_STUCK,
  NewsArticle,
  NewsListHeaderIsSticky,
  NEWS_LIST_ANIMATION_PARAM,
  NewsListDataSource,
  NAV_DESTS
} from "common"
import { AppStorageV2, curves } from "@kit.ArkUI"
import { deviceInfo } from "@kit.BasicServicesKit"

const NewsList_LOG_TAG = 'NewsList: '

@ComponentV2
export struct NewsList {
  @Param listScroller: Scroller = new Scroller()
  @Param newsList: NewsArticle[] = []
  @Param navStuck: NavPathStack = new NavPathStack()
  @Local navPathStuck: NavPathStack = AppStorageV2.connect(NavPathStack, NAV_PATH_STUCK, () => new NavPathStack())!
  @Local deviceType: DEVICE_TYPES =
    deviceInfo.deviceType === DEVICE_TYPES.PHONE ? DEVICE_TYPES.PHONE : DEVICE_TYPES.TABLET
  @Local isNewsListSticky: NewsListHeaderIsSticky =
    AppStorageV2.connect(NewsListHeaderIsSticky, IS_STICKY, () => new NewsListHeaderIsSticky())!
  @Local headerRadius: number = 20
  @Local headerAlignItems: HorizontalAlign = HorizontalAlign.Center
  @Local headerFontSize: number = this.deviceType === DEVICE_TYPES.PHONE ? 25 : 35
  @Local isOnAreaChange: boolean = false
  @Local newsListDataSource: NewsListDataSource = new NewsListDataSource()

  @Monitor('newsList')
  resetDataSource() {
    logger.info('捕获到newsList变化' + this.newsList.length)
    this.newsListDataSource.resetData(this.newsList)
  }

  @Builder
  NewsListHeaderBuilder() {
    Column() {
      Column() {
        Row() {
          Text(`热点新闻共${this.newsList?.length}条`)
            .fontSize(this.headerFontSize)
            .fontColor($r('app.color.news_list_header_font'))
            .margin({ left: 10 })
            .animation(NEWS_LIST_ANIMATION_PARAM)
          if (this.isNewsListSticky.isSticky) {
            Image($rawfile('backToTop.svg'))
              .fillColor($r('app.color.back_to_top'))
              .width(25)
              .transition(NEWS_LIST_ITEM_ANIMATE_PARAM)
              .onClick(() => {
                this.listScroller.scrollEdge(Edge.Top, { velocity: 6000 })
                this.isNewsListSticky.isSticky = false
              })
          }
        }
        .justifyContent(this.isNewsListSticky.isSticky ? FlexAlign.SpaceBetween : FlexAlign.Center)
        .width('100%')
      }
      .width('95%')
      .padding(10)
      .backgroundColor($r('app.color.news_list_header_bg'))
      .borderRadius(this.headerRadius)
      .margin({
        bottom: 15,
        left: 5,
        right: 5
      })
      .animation(NEWS_LIST_ANIMATION_PARAM)
    }
    .animation(NEWS_LIST_ANIMATION_PARAM)
    .onAreaChange((oldValue: Area, newValue: Area) => {
      if (!this.isOnAreaChange) {
        if (oldValue.position.y == 0 && newValue.position.y == 0) {
          this.isNewsListSticky.isSticky = false
        } else {
          this.isNewsListSticky.isSticky = true
          this.isOnAreaChange = true
          setTimeout(() => {
            this.isOnAreaChange = false
          }, 200)
        }
      }

    })
    .width('100%')
  }

  @Monitor('isNewsListSticky.isSticky')
  viewChange() {
    if (this.isNewsListSticky.isSticky) {
      this.headerRadius = 0
      this.headerAlignItems = HorizontalAlign.Start
      this.headerFontSize = this.deviceType === DEVICE_TYPES.PHONE ? 15 : 20
    } else {
      this.headerRadius = 20
      this.headerAlignItems = HorizontalAlign.Center
      this.headerFontSize = this.deviceType === DEVICE_TYPES.PHONE ? 25 : 35
    }
  }

  aboutToAppear(): void {
    setTimeout(() => {
      if (this.newsList.length == 0) {
        this.getUIContext()
          .getPromptAction()
          .showToast({ message: '后端数据正在更新请稍后下拉刷新或重启应用重试', duration: 5000 })
      }
      this.newsListDataSource.pushDataArr(this.newsList)
    }, 200)
  }

  build() {
    ListItemGroup({ header: this.NewsListHeaderBuilder(), space: this.deviceType === DEVICE_TYPES.PHONE ? 15 : 25 }) {
      LazyForEach(this.newsListDataSource, (news: NewsArticle) => {
        ListItem() {
          Column() {
            Column({ space: this.deviceType === DEVICE_TYPES.PHONE ? 10 : 20 }) {
              Text(news.title)
                .fontSize(this.deviceType === DEVICE_TYPES.PHONE ? 18 : 25)
                .fontWeight(900)
              Column() {
                Text(`来自于${news.source}`)
                  .fontSize(this.deviceType === DEVICE_TYPES.PHONE ? 14 : 18)
                  .fontWeight(200)
                  .textOverflow({
                    overflow: TextOverflow.Ellipsis
                  })
                  .maxLines(1)
                Text(news.date)
                  .fontSize(this.deviceType === DEVICE_TYPES.PHONE ? 14 : 18)
                  .fontWeight(200)
                  .textOverflow({
                    overflow: TextOverflow.Ellipsis
                  })
                  .maxLines(1)
              }
              .alignItems(HorizontalAlign.Start)
            }
            .alignItems(HorizontalAlign.Start)
            .width('100%')
            .padding({
              top: 5,
              bottom: 5,
              left: 10,
              right: 10
            })
            .borderRadius(19)
            .backgroundColor($r('app.color.news_list_item_bg'))
          }
          .width('95%')
          .backgroundImage($rawfile('newsListItemBG.png'))
          .borderWidth(2)
          .borderColor($r('app.color.news_list_item_border'))
          .backgroundColor($r('app.color.news_list_item_bg'))
          .borderRadius(20)

        }
        .onClick(() => {
          this.navStuck.replacePath({
            name: NAV_DESTS.ARTICLE,
            param: news
          })
        })
        .transition(NEWS_LIST_ITEM_ANIMATE_PARAM)
        .width('100%')
        .alignSelf(ItemAlign.Center)
      }, (item: NewsArticle, i: number) => {
        return `${item.id}+${i}`
      })
    }
    .borderRadius({
      topLeft: 20,
      topRight: 20
    })
  }
}