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
import { common } from '@kit.AbilityKit';
import { preferences } from '@kit.ArkData';
import { logger } from '../../utils';
import { promptAction } from '@kit.ArkUI';

const PreferenceDB_LOG_TAG = 'PreferenceDB: '
/**
 * 用户首选项数据持久化接口
 */
class PreferenceDB {
  private dataPreference: preferences.Preferences | null = null;

  init(context: common.BaseContext): boolean {
    const option: preferences.Options = { name: 'jyt' };
    this.dataPreference = preferences.getPreferencesSync(context, option);
    this.dataPreference.on("change", (key: string) => {
      logger.warn(`${PreferenceDB_LOG_TAG}The key ${key} changed`);
    });
    if (this.dataPreference) {
      return true
    }
    return false
  }

  release(): void {
    if (this.dataPreference) {
      this.dataPreference.off("change", (key: string) => {
        logger.warn(`${PreferenceDB_LOG_TAG}UnSubscribe the key ${key}`);
      });
    }
  }

  hasData(key: string): boolean {
    if (this.dataPreference) {
      const dataExist: boolean = this.dataPreference.hasSync(key);
      logger.info(`${PreferenceDB_LOG_TAG}Has ${key} data: ${dataExist}`);
      return dataExist;
    }
    return false;
  }

  pushData(key: string, value: Object): void {
    if (this.dataPreference) {
      logger.warn(`${PreferenceDB_LOG_TAG}push data: key=${key},value=${value}`)
      this.dataPreference.putSync(key, value);
      this.dataPreference.flush();
    }
  }

  deleteData(key: string): void {
    if (this.dataPreference) {
      this.dataPreference.deleteSync(key);
      logger.warn(`${PreferenceDB_LOG_TAG}Delete data ${key}`);
    }
  }

  getData<T>(key: string): T | null {
    try {
      if (this.dataPreference) {
        const obj: preferences.ValueType = this.dataPreference.getSync(key, 'default');
        logger.warn(`${PreferenceDB_LOG_TAG}Get data ${key}: ${JSON.stringify(obj)}`);
        return obj as T;
      }
      return null;
    }catch (e){
      promptAction.openToast({message:`${PreferenceDB_LOG_TAG}获取数据异常，异常信息为${JSON.stringify(e)}`})
      logger.error(`${PreferenceDB_LOG_TAG}获取数据异常，异常信息为${JSON.stringify(e)}`)
    }
    return null
  }
}

export const preferenceDB: PreferenceDB = new PreferenceDB();