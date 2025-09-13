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

/**
 * 新闻源信息接口
 * 描述不同来源的新闻平台信息
 */
export interface NewsSource {
  /** 新闻源标识（如：openharmony、csdn） */
  source: string;
  /** 新闻源名称（如：OpenHarmony官网、CSDN） */
  name: string;
  /** 新闻源描述信息 */
  description: string;
  /** 新闻源基础URL */
  base_url: string;
}

/**
 * 缓存服务状态接口
 * 描述缓存服务的当前状态信息
 */
export interface CacheService {
  /** 缓存服务状态（如：preparing、ready、error） */
  status: string;
  /** 缓存数量 */
  cache_count: number;
  /** 最后更新时间（null表示未更新过） */
  last_update: number | null;
  /** 错误信息（无错误时可能为null或空字符串） */
  error_message: string;
}

/**
 * 服务集合接口
 * 包含系统中所有可用的服务信息
 */
export interface Services {
  /** 缓存服务信息 */
  cache: CacheService;
  /** 新闻源列表 */
  news_sources: NewsSource[];
}

/**
 * 接口端点集合接口
 * 描述系统提供的所有API接口端点
 */
export interface Endpoints {
  /** OpenHarmony新闻接口 */
  openharmony_news: string;
  /** CSDN新闻接口 */
  csdn_news: string;
  /** 所有新闻聚合接口 */
  all_news: string;
  /** 手动爬取接口 */
  manual_crawl: string;
  /** 服务状态查询接口 */
  service_status: string;
}

/**
 * 系统状态根接口
 * 包含整个系统的状态信息和可用接口
 */
export interface SystemStatus {
  /** 系统整体状态（如：preparing、ready） */
  status: string;
  /** 时间戳（状态生成的时间） */
  timestamp: number;
  /** 系统版本号 */
  version: string;
  /** 系统包含的服务集合 */
  services: Services;
  /** 系统提供的API接口端点集合 */
  endpoints: Endpoints;
}

/**
 * 服务端状态枚举类
 */
export enum ServerStatus{
  preparing="preparing",
  healthy="healthy"
}