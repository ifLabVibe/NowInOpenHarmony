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
import { IS_STICKY, NAV_PATH_STUCK, NewsArticle, NewsListHeaderIsSticky } from "common"
import { NewsList, newsManager, NewsSwiper } from "feature"
import { AppStorageV2 } from "@kit.ArkUI"

const MainPage_TAG = 'MainPage: '

@Preview
@ComponentV2
export struct MainPage {
  @Local navPathStuck: NavPathStack = AppStorageV2.connect(NavPathStack, NAV_PATH_STUCK, () => new NavPathStack())!
  @Local newsList: NewsArticle[] | null = null
  @Local isNewsListSticky: NewsListHeaderIsSticky =
    AppStorageV2.connect(NewsListHeaderIsSticky, IS_STICKY, () => new NewsListHeaderIsSticky())!
  @Local listScroller: Scroller = new Scroller()
  @Local isLoading: boolean = false
  @Local newsSwiperData: ResourceStr[] | null = []

  async aboutToAppear(): Promise<void> {
    this.newsList = await newsManager.getNewsArticleListFromDB()
    if (!this.newsList) {
      this.getUIContext().getPromptAction().showToast({ message: `当前数据库新闻数据为空,请连接后端服务以更新数据` })
    } else if (this.newsList) {
      this.getUIContext().getPromptAction().showToast({ message: `从数据库查询到${this.newsList.length}条新闻数据` })
    }
    this.newsSwiperData = await newsManager.getNewsSwiperDataFromDB()
    if (!this.newsSwiperData) {
      this.getUIContext().getPromptAction().showToast({ message: `当前数据库轮播图数据为空,请连接后端服务以更新数据` })
    } else if (this.newsSwiperData) {
      this.getUIContext()
        .getPromptAction()
        .showToast({ message: `从数据库查询到${this.newsSwiperData.length}条轮播图数据` })
    }
  }

  async reloadAllData() {
    this.getUIContext().getPromptAction().showToast({ message: '刷新数据' })
    if (await newsManager.updateNewsListToDB() && await newsManager.updateNewsSwiperToDB()) {
      this.newsList = await newsManager.getNewsArticleListFromDB()
      this.newsSwiperData = await newsManager.getNewsSwiperDataFromDB()
      return true
    }
    this.getUIContext().getPromptAction().showToast({ message: '获取新数据失败请稍后再试。' })
    return false
  }

  build() {
    Column() {
      Refresh({ refreshing: $$this.isLoading }) {
        List({ space: 20, scroller: this.listScroller }) {
          ListItemGroup() {
            ListItem() {
              NewsSwiper({ swiperData: this.newsSwiperData ?? [] })
            }
          }

          NewsList({ newsList: this.newsList ?? [], listScroller: this.listScroller, navStuck: this.navPathStuck })
        }
        .onReachStart(() => {
          this.isNewsListSticky.isSticky = false
        })
        .edgeEffect(EdgeEffect.Spring, { alwaysEnabled: true })
        .chainAnimation(true)
        .sticky(StickyStyle.Header)
        .width('100%')
        .height('100%')
      }
      .onRefreshing(async () => {
        await this.reloadAllData()
        this.isLoading = false
      })
    }
    .width('100%')
    .height('100%')
  }
}