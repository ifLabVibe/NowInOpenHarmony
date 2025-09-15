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
  DEFAULT_COLOR_MODE,
  DEFAULT_FONT_SIZE,
  GET_USER_CONFIG,
  logger,
  preferenceDB,
  PreferenceEnum,
  UserConfigViewModel
} from "common";
import { AppStorageV2, promptAction } from "@kit.ArkUI";

const UserConfigManager_LOG_TAG = 'UserConfigManager: '

/**
 * 用户配置项管理器，提供全局变量和持久化数据之间的交互接口。
 */
export class UserConfigManager {
  /**
   * 持久化当前应用配置数据
   * @returns 是否成功
   */
  syncDataToPreference(): boolean {
    const UserConfig = AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!
    const colorMode = UserConfig.colorModel
    preferenceDB.pushData(PreferenceEnum.COLOR_MODE, colorMode)
    const fontSize = UserConfig.fontSize
    preferenceDB.pushData(PreferenceEnum.FONT_SIZE, fontSize)
    if (preferenceDB.getData<0 | 1 | 2>(PreferenceEnum.COLOR_MODE) === colorMode &&
      preferenceDB.getData<number>(PreferenceEnum.FONT_SIZE) === fontSize) {
      logger.warn(`${UserConfigManager_LOG_TAG}数据持久化成功,colorMode=${preferenceDB.getData<0 | 1 | 2>(PreferenceEnum.COLOR_MODE)},fontSize=${preferenceDB.getData<number>(PreferenceEnum.FONT_SIZE)}`)
      return true
    }
    return false
  }

  /**
   * 获取应用配置持久化数据,若无持久化数据则设置默认数据
   * @returns 是否成功
   */
  syncDataToAppStorage(): boolean {
    if (preferenceDB.hasData(PreferenceEnum.COLOR_MODE)) {
      logger.info(`${UserConfigManager_LOG_TAG}检测到COLOR_MODE = ${preferenceDB.getData<number>(PreferenceEnum.COLOR_MODE)}`)
      AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!.colorModel = preferenceDB.getData<0 | 1 | 2>(PreferenceEnum.COLOR_MODE)!
    }
    if (preferenceDB.hasData(PreferenceEnum.FONT_SIZE)) {
      logger.info(`${UserConfigManager_LOG_TAG}检测到FONT_SIZE = ${preferenceDB.getData<number>(PreferenceEnum.FONT_SIZE)}`)
      AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!.fontSize = preferenceDB.getData<number>(PreferenceEnum.FONT_SIZE)!
    }
    if (!preferenceDB.hasData(PreferenceEnum.FONT_SIZE) || !preferenceDB.hasData(PreferenceEnum.COLOR_MODE)) {
      logger.warn(`${UserConfigManager_LOG_TAG}无用户配置持久化数据，执行默认配置设置`)
      this.setConfigToDefault()
    }
    const fontSize = AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!.fontSize
    const colorMode = AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!.colorModel
    if (preferenceDB.getData<0 | 1 | 2>(PreferenceEnum.COLOR_MODE) === colorMode &&
      preferenceDB.getData<number>(PreferenceEnum.FONT_SIZE) === fontSize) {
      logger.warn(`${UserConfigManager_LOG_TAG}用户首选项持久化数据读取成功,colorMode=${colorMode},fontSize=${fontSize}`)
      return true
    }
    logger.error(`${UserConfigManager_LOG_TAG}用户首选项持久化数据获取发生异常`)
    return false
  }

  /**
   * 将全局状态变量以及持久化数据更改为默认状态
   */
  async setConfigToDefault() {

    logger.debug(`${UserConfigManager_LOG_TAG}preferenceDB.hasData(PreferenceEnum.COLOR_MODE)=${preferenceDB.hasData(PreferenceEnum.COLOR_MODE)}`)
    AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!.colorModel =
      DEFAULT_COLOR_MODE
    preferenceDB.pushData(PreferenceEnum.COLOR_MODE, DEFAULT_COLOR_MODE)

    logger.debug(`${UserConfigManager_LOG_TAG}preferenceDB.hasData(PreferenceEnum.FONT_SIZE)=${preferenceDB.hasData(PreferenceEnum.FONT_SIZE)}`)
    AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!.fontSize =
      DEFAULT_FONT_SIZE
    preferenceDB.pushData(PreferenceEnum.FONT_SIZE, DEFAULT_FONT_SIZE)

  }
}

export const userConfigManager = new UserConfigManager()