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
import { distributedKVStore } from "@kit.ArkData";
import { BusinessError } from "@kit.BasicServicesKit";
import { logger } from "../../utils/logger/logger";
import { common } from '@kit.AbilityKit';

const KVDatabase_LOG_TAG = 'KVDatabase: '

/**
 * 键值型数据库管理接口
 */
export class KVDatabase {
  /**
   * 数据库管理对象，应用启动后需要先行创建并进行数据库的创建。
   */
  kvManager: distributedKVStore.KVManager | undefined = undefined;
  appId: string = 'com.xbxyftx.NowInOpenHarmony';

  /**
   * 初始化方法，创建数据库管理对象KVManager，需在应用启动阶段进行调用。
   * @param context 当前应用上下文
   * @returns 是否成功初始化
   */
  init(context: common.UIAbilityContext): boolean {
    const kvManagerConfig: distributedKVStore.KVManagerConfig = {
      context: context,
      bundleName: this.appId
    };
    try {
      // 创建KVManager实例
      this.kvManager = distributedKVStore.createKVManager(kvManagerConfig);
      console.info(KVDatabase_LOG_TAG + 'Succeeded in creating KVManager.');
      // 继续创建获取数据库
      if (this.kvManager !== undefined) {
        logger.info(KVDatabase_LOG_TAG+'数据库管理对象创建成功。')
        return true
      }
      logger.error(KVDatabase_LOG_TAG + '数据库管理对象创建失败')
      return false
    } catch (e) {
      let error = e as BusinessError;
      logger.error(KVDatabase_LOG_TAG + `Failed to create KVManager. Code:${error.code},message:${error.message}`);
      return false
    }
  }

  /**
   * 通过ID获取数据库实例对象，需在init后使用。
   * @param storeId 数据库实例对象ID
   * @returns 单版本数据库实例对象
   */
  async getKVStoreById(storeId:string):Promise<distributedKVStore.SingleKVStore|null>{
    if (this.kvManager) {
      try {
        const options:distributedKVStore.Options = {
          createIfMissing: true,
          securityLevel: distributedKVStore.SecurityLevel.S1,
          kvStoreType:distributedKVStore.KVStoreType.SINGLE_VERSION
        }
        const kVStore:distributedKVStore.SingleKVStore = await this.kvManager.getKVStore(storeId,options)
        if (kVStore) {
          logger.info(`${KVDatabase_LOG_TAG}成功获取storeId:${storeId}数据库实例对象`)
          this.kvManager.on('distributedDataServiceDie',()=>{
            logger.warn(`${KVDatabase_LOG_TAG}数据库服务订阅发生变更`)
          })
          return kVStore
        }
      }catch (e){
        let err = e as BusinessError
        logger.error(`${KVDatabase_LOG_TAG}获取KV数据库实例对象异常，异常信息: ${err.message}`)
      }
    }
    return null
  }


}

export const kvDatabase: KVDatabase = new KVDatabase()