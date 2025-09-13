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

import { promptAction } from '@kit.ArkUI'

/**
 * 首页上方轮播图组件
 */
@ComponentV2
export struct NewsSwiper {
  @Param swiperData: ResourceStr[] = []

  build() {
    Column() {
      Swiper(){
        ForEach(this.swiperData,(item:ResourceStr)=>{
          Image(item)
            .width('100%')
            .objectFit(ImageFit.Fill)
            .onClick(()=>{
              promptAction.showToast({message:'跳转原页面功能待开发'})
            })
            .borderRadius(20)
            .aspectRatio(2.2)
        })
      }
      .width('95%')
      .curve(Curve.EaseInOut)
      .loop(true)
      .autoPlay(true)
      .interval(2000)
    }
    .alignItems(HorizontalAlign.Center)
    .borderRadius(20)
    .width('100%')

  }
}