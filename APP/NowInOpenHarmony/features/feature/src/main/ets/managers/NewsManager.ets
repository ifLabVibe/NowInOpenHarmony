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
  APP_KV_DB as APP_KV_DB_ID,
  kvDatabase,
  KV_DB_KEYS,
  logger,
  NewsArticle,
  NewsListAPI,
  NewsSwiperAPI,
  NewsSwiperStateAPI,
  ServerHealthAPI
} from "common"
import { common } from "@kit.AbilityKit"
import { distributedKVStore } from "@kit.ArkData"
import { promptAction } from "@kit.ArkUI"
import { BusinessError } from "@kit.BasicServicesKit"

const NewsManager_LOG_TAG = 'NewsManager: '

export class NewsManager {
  /**
   * 当前应用的键值数据库实例对象
   */
  appKVDb: distributedKVStore.SingleKVStore | undefined = undefined

  /**
   * 初始化函数，获取当前应用的键值对数据库实例。
   * @param context
   * @returns
   */
  async init(context: common.UIAbilityContext): Promise<boolean> {
    kvDatabase.init(context)
    const res = await kvDatabase.getKVStoreById(APP_KV_DB_ID)
    if (res) {
      this.appKVDb = res
      logger.info(`${NewsManager_LOG_TAG}init: 获取appKVDb成功`)
      return true
    }
    logger.error(`${NewsManager_LOG_TAG}初始化失败`)
    return false
  }

  /**
   * 从后端更新新闻文章列表数据，并持久化最新的新闻列表数据。
   * @param times 递归尝试查询服务端的计数器参数，无需传入
   * @returns 是否成功获取以及持久化
   */
  async updateNewsListToDB(): Promise<boolean> {
    if (await ServerHealthAPI.isServerReady()) {
      const news: NewsArticle[] | null = (await NewsListAPI.getAllNews())
      if (news && this.appKVDb) {
        logger.info(`${NewsManager_LOG_TAG}成功获取最新新闻，总条数: ${news.length}`)
        try {
          this.appKVDb.put(KV_DB_KEYS.NEWS_ARTICLE_LIST, JSON.stringify(news))
          logger.info(`${NewsManager_LOG_TAG}数据库写入成功，无异常`)
          return true
        } catch (e) {
          let err = e as BusinessError
          logger.error(`${NewsManager_LOG_TAG}更新数据库NewsArticle数据发生异常，异常信息: ${err.message}`)
          return false
        }
      }
      logger.error(`${NewsManager_LOG_TAG}获取新闻失败,新闻数据或键值数据库为空。`)
      return false
    }
    logger.error(`${NewsManager_LOG_TAG}获取新闻失败，后端服务状态异常，返回false`)
    return false
  }

  async getNewsArticleListFromDB(): Promise<NewsArticle[] | null> {
    if (this.appKVDb) {
      try {
        const res: string = (await this.appKVDb.get(KV_DB_KEYS.NEWS_ARTICLE_LIST)) as string
        logger.info(`${NewsManager_LOG_TAG}读取到数据库新闻列表数据: ${res}`)
        const newsArticleList = JSON.parse(res) as NewsArticle[]
        return newsArticleList
      } catch (e) {
        let err = e as BusinessError
        logger.error(`${NewsManager_LOG_TAG}尝试获取数据库新闻列表数据发生异常，异常信息: ${err.message}`)
        return null
      }
    }
    return null
  }

  async updateNewsSwiperToDB(): Promise<boolean> {
    if (await NewsSwiperStateAPI.isSwiperServerReady()) {
      let swiperData: ResourceStr[] | null = await NewsSwiperAPI.getNewsSwiperImgData()
      if (swiperData && this.appKVDb) {
        logger.info(`${NewsManager_LOG_TAG}成功获取最新轮播图数据，总条数: ${swiperData.length}`)
        try {
          this.appKVDb.put(KV_DB_KEYS.NEWS_SWIPER, JSON.stringify(swiperData))
          logger.info(`${NewsManager_LOG_TAG}轮播图数据库写入成功，无异常`)
          return true
        } catch (e) {
          let err = e as BusinessError
          logger.error(`${NewsManager_LOG_TAG}更新数据库NewsSwiper数据发生异常，异常信息: ${err.message}`)
          return false
        }
      }
      logger.error(`${NewsManager_LOG_TAG}获取到的轮播图数据或键值数据库为空`)
      return false
    }
    logger.error(`${NewsManager_LOG_TAG}获取轮播图数据失败，后端轮播图服务状态异常`)
    return false
  }

  async getNewsSwiperDataFromDB(): Promise<ResourceStr[] | null> {
    if (this.appKVDb) {
      try {
        const res: string = (await this.appKVDb.get(KV_DB_KEYS.NEWS_SWIPER)) as string
        logger.info(`${NewsManager_LOG_TAG}读取到数据库轮播图数据列表数据: ${res}`)
        const newsSwiperData = JSON.parse(res) as ResourceStr[]
        return newsSwiperData
      } catch (e) {
        let err = e as BusinessError
        logger.error(`${NewsManager_LOG_TAG}尝试获取数据库轮播图数据发生异常，异常信息: ${err.message}`)
        return null
      }
    }
    return null
  }
}

export const newsManager = new NewsManager()