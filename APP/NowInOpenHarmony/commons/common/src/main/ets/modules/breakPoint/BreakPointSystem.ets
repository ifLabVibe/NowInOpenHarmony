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

import { mediaquery } from "@kit.ArkUI"

/**
 * 定义断点名称的联合类型，规范断点命名规则
 * xs: 超小屏幕（如手机竖屏）
 * sm: 小屏幕（如手机横屏）
 * md: 中等屏幕（如平板）
 * lg: 大屏幕（如PC）
 */
export type BreakpointType = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl'

/**
 * 断点配置接口，描述每个断点的特征
 * @property name 断点名称，对应BreakpointType
 * @property size 断点触发的最小宽度（单位：vp）
 * @property mediaQueryListener 媒体查询监听器实例
 */
export interface Breakpoint {
  /**name 断点名称，对应BreakpointType*/
  name: BreakpointType
  /**size 断点触发的最小宽度（单位：vp）*/
  size: number
  /**mediaQueryListener 媒体查询监听器实例*/
  mediaQueryListener?: mediaquery.MediaQueryListener
}