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
  CONTENT_TYPE_ENUM, DEVICE_TYPES, NewsArticle, NewsContentBlock
} from "common"
import { deviceInfo } from "@kit.BasicServicesKit"
import { LvMarkdownIn } from '@luvi/lv-markdown-in'

/**
 * 文章内容渲染组件
 * @param article 带渲染文章内容
 * @param baseFontSize 基准字体大小
 */
@ComponentV2
export struct NewsArticleView {
  @Param article: NewsArticle = {
    id: "",
    title: "",
    date: "",
    url: "",
    content: [],
    source: ''
  }
  @Param baseFontSize: number = 0
  @Local deviceType: DEVICE_TYPES =
    deviceInfo.deviceType === DEVICE_TYPES.PHONE ? DEVICE_TYPES.PHONE : DEVICE_TYPES.TABLET

  @Builder
  articleInfoBuilder() {
    Row() {
      Text(`日期：${this.article.date} ${this.article.source ? '来源：' : ''}${this.article.source}`)
        .fontSize(this.baseFontSize+(this.deviceType === DEVICE_TYPES.PHONE ? 8 : 12))
    }
    .alignSelf(ItemAlign.Start)
    .width('95%')
  }

  build() {
    // 根组件
    Scroll() {
      Column({space:10+(this.baseFontSize*(this.deviceType === DEVICE_TYPES.PHONE ?0.3:0.5))}) {
        Text(this.article.title)
          .width('95%')
          .fontSize(this.baseFontSize + (this.deviceType === DEVICE_TYPES.PHONE ? 12 : 16))
          .fontWeight(900)
          .alignSelf(ItemAlign.Center)
        // 日期来源行
        this.articleInfoBuilder()

        ForEach(this.article.content, (item: NewsContentBlock, i: number) => {
          if (item.type === CONTENT_TYPE_ENUM.TEXT) {
            Text(`        ${item.value}`)
              .fontSize(this.baseFontSize+ (this.deviceType === DEVICE_TYPES.PHONE ? 0 : 6))
              .width('90%')
              .alignSelf(ItemAlign.Center)
          } else if (item.type === CONTENT_TYPE_ENUM.IMAGE) {
            Image(item.value)
              .width('90%')
              .alignSelf(ItemAlign.Center)
          } else if (item.type === CONTENT_TYPE_ENUM.VIDEO) {
            Video({
              src: item.value
            })
              .width('90%')
              .alignSelf(ItemAlign.Center)
          } else if (item.type === CONTENT_TYPE_ENUM.CODE) {
            LvMarkdownIn({
              text: `        ${item.value}`
            })
              .width('90%')
              .alignSelf(ItemAlign.Center)
          }
        })
      }
      .padding(5)
      .borderRadius(20)
      .alignItems(HorizontalAlign.Start)
      .backgroundColor($r('app.color.article_info_builder_bg'))

    }
    .scrollBar(BarState.Off)
    .borderRadius(20)
    .width('100%')
    .height('100%')

  }
}