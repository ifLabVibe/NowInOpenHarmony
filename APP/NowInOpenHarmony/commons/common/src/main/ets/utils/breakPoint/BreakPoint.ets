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

import { Breakpoint, BreakpointType } from "../../modules/breakPoint/BreakPointSystem"
import { BreakpointState } from "../../modules/breakPoint/BreakpointState"
import { logger } from ".."

const BREAK_POINT_SYSTEM_LOG_TAG = 'BreakpointSystem:  '
/**
 * 断点系统核心类（单例模式）
 * 负责管理设备断点状态及监听逻辑
 */
export class BreakpointSystem {
  // 单例实例引用，确保全局唯一性[1](@ref)
  private static instance: BreakpointSystem
  uiContext:UIContext
  /** 预定义断点范围配置（可扩展）*/
  private readonly breakpoints: Breakpoint[] = [
    { name: 'xs', size: 0 },     // 0vp <= width < 320vp
    { name: 'sm', size: 320 },   // 320vp <= width < 600vp
    { name: 'md', size: 600 },   // 700vp <= width < 1040vp
    { name: 'lg', size: 780 }    // 1040vp <= width
  ]

  /** 使用Set存储状态观察者（自动去重）[1](@ref)*/
  private _states: Set<BreakpointState<Object>>

  public get states(): Set<BreakpointState<Object>> {
    return this._states
  }

  // 私有构造器（单例模式）
  private constructor(uiContext:UIContext) {
    this._states = new Set()  // 初始化观察者集合
    this.uiContext=uiContext
  }

  /** 获取单例实例 */
  public static getInstance(uiContext:UIContext): BreakpointSystem {
    if (!BreakpointSystem.instance) {
      BreakpointSystem.instance = new BreakpointSystem(uiContext)
    }
    return BreakpointSystem.instance
  }

  /** 注册状态观察者 */
  public attach(state: BreakpointState<Object>): void {
    logger.info(`${BREAK_POINT_SYSTEM_LOG_TAG}注册状态观察者`)
    this._states.add(state)  // 添加新观察者到集合
  }

  /** 注销状态观察者 */
  public detach(state: BreakpointState<Object>): void {
    this._states.delete(state)  // 从集合中移除观察者
  }

  /** 启动断点监听系统 */
  public start() {
    this.breakpoints.forEach((breakpoint: Breakpoint, index) => {
      /**
       * 查询条件
       */
      let condition: string
      // 动态生成媒体查询条件：
      if (index === this.breakpoints.length - 1) {
        // 最后一个断点使用 >= 条件
        condition = `(${breakpoint.size}vp<=width)`
      } else {
        // 中间断点使用区间条件
        condition = `(${breakpoint.size}vp<=width<${this.breakpoints[index + 1].size}vp)`
      }

      // 创建媒体查询监听器[1](@ref)
      breakpoint.mediaQueryListener = this.uiContext.getMediaQuery().matchMediaSync(condition)

      // 初始化匹配状态检查
      if (breakpoint.mediaQueryListener.matches) {
        logger.warn(`${BREAK_POINT_SYSTEM_LOG_TAG}初始化匹配成功breakpoint.name=${breakpoint.name}`)
        this.updateAllState(breakpoint.name)
      }

      // 注册尺寸变化监听回调
      breakpoint.mediaQueryListener.on('change', (mediaQueryResult) => {
        logger.warn(`${BREAK_POINT_SYSTEM_LOG_TAG}触发断点状态变化回调`)
        if (mediaQueryResult.matches) {
          logger.warn(`${BREAK_POINT_SYSTEM_LOG_TAG}匹配成功breakpoint.name=${breakpoint.name}`)
          this.updateAllState(breakpoint.name)  // 触发状态更新
        }
      })
      logger.info(BREAK_POINT_SYSTEM_LOG_TAG+`第${index}个断点状态对象启动完成`)
    })
  }

  /** 更新所有观察者状态 */
  private updateAllState(type: BreakpointType): void {
    this._states.forEach(state => state.update(type))  // 遍历执行更新
    logger.info(BREAK_POINT_SYSTEM_LOG_TAG+'全部断点状态更新完成')
  }

  /** 停止监听并清理资源 */
  public stop() {
    this.breakpoints.forEach(breakpoint => {
      if (breakpoint.mediaQueryListener) {
        breakpoint.mediaQueryListener.off('change')  // 注销监听器
      }
    })
    this._states.clear()  // 清空观察者集合
    logger.info(BREAK_POINT_SYSTEM_LOG_TAG+'断点状态对象全部关闭')
  }
}

// /**
//  * 获取当前设备断点系统的包装类
//  * 调用getBreakPointSystem获取当前断点系统
//  */
// export class GetBreakPointSystem{
//   uiContext:UIContext
//
//
//   private breakPointSystem:BreakpointSystem=BreakpointSystem.getInstance(this.uiContext)
//   /**
//    * 获取当前断点系统
//    * @returns 当前断点系统
//    */
//   getBreakPointSystem(uiContext:UIContext){
//     return this.breakPointSystem
//   }
//   constructor(uiContext: UIContext) {
//     this.uiContext = uiContext
//   }
// }

// export const breakpointSystem = BreakpointSystem.getInstance()

