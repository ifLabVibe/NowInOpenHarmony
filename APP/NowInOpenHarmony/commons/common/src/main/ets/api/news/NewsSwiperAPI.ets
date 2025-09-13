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
import { NewsSwiperResModule } from "../../modules/news/NewsSwiperModules"
import { logger } from "../../utils"
import { axiosHttp } from "../http/AxiosHttp"
import { BusinessError } from "@kit.BasicServicesKit"

const NewsSwiperAPI_LOG_TAG = 'NewsSwiperAPI: '
export class NewsSwiperAPI{
  /**
   * 获取轮播图数据
   * @returns 轮播图链接列表
   */
  static async getNewsSwiperImgData():Promise<null|ResourceStr[]>{
    try {
      const res = await axiosHttp.request<NewsSwiperResModule>({
        url:'/api/banner/mobile'
      })
      logger.info(`${NewsSwiperAPI_LOG_TAG}${JSON.stringify(res)}`)
      return res.images
    }catch (e){
      let err = e as BusinessError
      logger.error(`${NewsSwiperAPI_LOG_TAG}${err.message}`)
      return null
    }
  }
}