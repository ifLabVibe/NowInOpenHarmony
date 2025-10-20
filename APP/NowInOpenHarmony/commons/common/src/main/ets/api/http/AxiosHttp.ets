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
import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from "@ohos/axios"
import { logger } from "../../utils"
import { AppStorageV2, promptAction } from "@kit.ArkUI"
import { SERVE_BASE_ADDRESS } from "../../modules/constants"
import { GetUIContext } from "../../modules/context/GetUIContext"

export const AXIOS_HTTP_LOG_TAG = 'AxiosHttp:  '

/**
 * axios请求实例
 * 配置基地址和请求超时时间
 */
export const axiosInstance = axios.create({
  baseURL: SERVE_BASE_ADDRESS,
  timeout: 10000
})

// logger.debug('请求获取UIContext')


/**
 * 设置响应拦截器拦截器
 * interceptors:    拦截器
 * response:        响应
 * 由这个axiosInstance实例发送到请求的响应都会经过它再返回
 */
// 响应拦截器
axiosInstance.interceptors.response.use((res: AxiosResponse) => {

  if (res.status === 200) {
    logger.warn(AXIOS_HTTP_LOG_TAG + 'Req Success' + JSON.stringify(res.data))
    return res.data
  }
  logger.error(AXIOS_HTTP_LOG_TAG + 'ReqCode Error' + JSON.stringify(res.data))
  promptAction.showToast({ message: 'ReqCode Error' + JSON.stringify(res.data)})
  return Promise.reject(res.data)
}, (err: AxiosError) => {
  logger.error(AXIOS_HTTP_LOG_TAG + 'AxiosReq Error' + err.message )
  promptAction.showToast({ message: 'AxiosReq Error' + err.message })
  return Promise.reject(err)
})

class AxiosHttp {
  /**
   * Axios包装过的请求函数
   * @param config 网络请求配置项
   * <res:响应数据类型
   * req:请求体参数类型 - get不需要传>
   */
  request<res, req = Object>(config: AxiosRequestConfig<req>) {
    logger.debug(AXIOS_HTTP_LOG_TAG + '进入AxiosHttp.request')
    return axiosInstance<null, res, req>(config)
  }
}

/**
 * 包装后的axios请求，添加了拦截器直接选取res.data中的字段
 */
export const axiosHttp = new AxiosHttp()