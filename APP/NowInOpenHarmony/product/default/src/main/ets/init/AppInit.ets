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
  GET_USER_CONFIG, logger, preferenceDB, UserConfigViewModel
} from "common";
import { common } from "@kit.AbilityKit";
import { AppStorageV2, promptAction } from "@kit.ArkUI";
import { colorModManager, newsManager, userConfigManager } from "feature";
import { lvCode, lvText } from "@luvi/lv-markdown-in";


const AppInit_LOG_TAG = 'AppInit: '

/**
 * 应用初始化接口
 */
export class AppInit {
  /**
   * 用户配置项初始化
   */
  configInit(context: common.UIAbilityContext) {
    const isPreferenceDBInitSuccess: boolean = preferenceDB.init(context)
    if (isPreferenceDBInitSuccess) {
      logger.info(`${AppInit_LOG_TAG}首选项数据对象初始化成功`)
      if (userConfigManager.syncDataToAppStorage()) {
        return true
      }
      return false
    } else {
      promptAction.openToast({ message: `${AppInit_LOG_TAG}首选项数据对象初始化错误` })
      logger.error(`${AppInit_LOG_TAG}首选项数据对象初始化错误`)
      return false
    }
  }

  async initAll(uiAbilityContext: common.UIAbilityContext, applicationContext: common.ApplicationContext) {
    await newsManager.init(uiAbilityContext)
    this.configInit(uiAbilityContext)
    colorModManager.init(applicationContext)
    await newsManager.updateNewsListToDB()
    await newsManager.updateNewsSwiperToDB()
  }
  markDownConfigInit(){
    let baseFontSize =  AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!.fontSize
    lvCode.setIndexState(true)
    lvText.setTextSize(baseFontSize)
    logger.info(`${AppInit_LOG_TAG}Markdown初始化成功`)
  }

}

export const appInit = new AppInit()