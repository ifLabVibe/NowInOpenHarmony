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
import { CACHE_STATUS, SwiperState } from "../../modules/server/SwiperState"
import { logger } from "../../utils"
import { axiosHttp } from "../http/AxiosHttp"
import { BusinessError } from "@kit.BasicServicesKit"
import { promptAction } from "@kit.ArkUI"

const SwiperStateAPI_LOG_TAG = 'SwiperStateAPI: '

export class NewsSwiperStateAPI {
  /**
   * 检测轮播图状态
   * @returns
   */
  static async isSwiperServerReady(): Promise<boolean> {
    try {
      const res = await axiosHttp.request<SwiperState>({
        url: '/api/banner/status',
      })
      logger.info(SwiperStateAPI_LOG_TAG + JSON.stringify(res))
      if (res.cache_status.status === CACHE_STATUS.preparing) {

        logger.warn(`${SwiperStateAPI_LOG_TAG}轮播图尚未准备完毕`)
        return false
      } else if (res.cache_status.status === CACHE_STATUS.error) {
        promptAction.showToast({ message: `轮播图服务内部出现异常${res.cache_status.error_message}` })
        logger.error(`${SwiperStateAPI_LOG_TAG}轮播图服务内部出现异常${res.cache_status.error_message}`)
        return false
      } else if (res.cache_status.status === CACHE_STATUS.ready) {
        return true
      }
    } catch (e) {
      let err = e as BusinessError
      logger.error(`${SwiperStateAPI_LOG_TAG}${err.message}`)
      return false
    }
    return false
  }
}