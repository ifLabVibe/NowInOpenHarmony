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

import { common, ConfigurationConstant } from "@kit.AbilityKit";
import { DEFAULT_COLOR_MODE, GET_USER_CONFIG, logger, UserConfigViewModel } from "common";
import { AppStorageV2 } from "@kit.ArkUI";
import { userConfigManager } from "./UserConfigManager";

const ColorModManager_LOG_TAG = 'ColorModManager: '

/**
 * 颜色模式管理器
 */
export class ColorModManager {
  /**
   * 应用上下文对象
   */
  applicationContext: common.ApplicationContext | null = null

  /**
   * 管理器初始化，并应用初始化后的颜色应用状态
   * @param applicationContext 应用上下文对象
   * @returns 是否初始化成功
   */
  init(applicationContext: common.ApplicationContext): boolean {
    this.applicationContext = applicationContext
    if (applicationContext) {
      logger.info(`${ColorModManager_LOG_TAG}applicationContext初始化成功`)
      this.initColoModSetting();
      return true
    }
    return false
  }

  /**
   * 初始化颜色设置，仅做内部调用，外部请使用其余设置接口
   */
  private initColoModSetting() {
    switch (AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!.colorModel) {
      case 0: {
        logger.info(`${ColorModManager_LOG_TAG}initColoModSetting 0: AppStorageV2colorModel = ${AppStorageV2.connect(UserConfigViewModel,
          GET_USER_CONFIG, () => new UserConfigViewModel())!.colorModel}`)
        this.applicationContext!.setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_LIGHT);
        break
      }

      case 1: {
        logger.info(`${ColorModManager_LOG_TAG}initColoModSetting 1: AppStorageV2colorModel = ${AppStorageV2.connect(UserConfigViewModel,
          GET_USER_CONFIG, () => new UserConfigViewModel())!.colorModel}`)
        this.applicationContext!.setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_DARK);
        break
      }

      case 2: {
        logger.info(`${ColorModManager_LOG_TAG}initColoModSetting 2: AppStorageV2colorModel = ${AppStorageV2.connect(UserConfigViewModel,
          GET_USER_CONFIG, () => new UserConfigViewModel())!.colorModel}`)
        this.applicationContext!.setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_NOT_SET);
        break
      }

    }
  }

  setDarkMod(): boolean {
    if (this.applicationContext) {
      this.applicationContext.setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_DARK)
      AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!.colorModel = 1
      logger.info(`${ColorModManager_LOG_TAG}深色模式修改成功AppStoragecolorModel=${AppStorageV2.connect(UserConfigViewModel,
        GET_USER_CONFIG, () => new UserConfigViewModel())!.colorModel}开始持久化数据`)
      userConfigManager.syncDataToPreference()
      return true
    }
    logger.error(`${ColorModManager_LOG_TAG}应用上下文对象缺失`)
    return false
  }

  setLightMod(): boolean {
    if (this.applicationContext) {
      this.applicationContext.setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_LIGHT)
      AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!.colorModel = 0
      logger.info(`${ColorModManager_LOG_TAG}浅色模式修改成功AppStoragecolorModel=${AppStorageV2.connect(UserConfigViewModel,
        GET_USER_CONFIG, () => new UserConfigViewModel())!.colorModel}开始持久化数据`)
      userConfigManager.syncDataToPreference()
      return true
    }
    logger.error(`${ColorModManager_LOG_TAG}应用上下文对象缺失`)
    return false
  }

  setDefaultColorMode(): boolean {
    if (this.applicationContext) {
      this.applicationContext.setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_NOT_SET)
      AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!.colorModel = 2
      logger.info(`${ColorModManager_LOG_TAG}跟随系统模式修改成功AppStoragecolorModel=${AppStorageV2.connect(UserConfigViewModel,
        GET_USER_CONFIG, () => new UserConfigViewModel())!.colorModel}开始持久化数据`)
      userConfigManager.syncDataToPreference()
      return true
    }
    logger.error(`${ColorModManager_LOG_TAG}应用上下文对象缺失`)
    return false
  }
}

export const colorModManager = new ColorModManager()