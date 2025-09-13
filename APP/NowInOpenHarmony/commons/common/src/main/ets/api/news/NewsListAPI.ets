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
import { NewsArticle, NewsResponse } from "../../modules/news/NewsListModules";
import { logger } from "../../utils/logger/logger";
import { axiosHttp } from "../http/AxiosHttp";
import { BusinessError } from "@kit.BasicServicesKit";

const NewsListAPI_TAG = 'NewsListAPI: '

export class NewsListAPI{
  /**
   * 获取全部新闻列表接口，在调用前请先调用isServerReady接口
   * @returns 若是出现异常则为空正常则为全部新闻列表NewsArticle[]
   */
  static async getAllNews(): Promise<NewsArticle[] | null>{
    try {
      const res = await axiosHttp.request<NewsResponse>({
        url:'/api/news/?all=true'
      })
      return res.articles
    }catch (e){
      let err = e as BusinessError
      logger.error(`${NewsListAPI_TAG}${err.message}`)
      return null
    }
  }
}