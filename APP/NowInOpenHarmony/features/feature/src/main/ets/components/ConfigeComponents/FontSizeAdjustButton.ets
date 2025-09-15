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
import { DEFAULT_FONT_SIZE, DEVICE_TYPES, GET_USER_CONFIG, logger, PreferenceEnum, preferenceDB, UserConfigViewModel } from "common"
import { AppStorageV2, promptAction } from "@kit.ArkUI"
import { deviceInfo } from "@kit.BasicServicesKit"
import { userConfigManager } from "../../managers/UserConfigManager"

const FontSizeAdjustButton_LOG_TAG = 'FontSizeAdjustButton: '

/**
 * 字体大小调整弹窗（平板专用）
 */
@CustomDialog
struct FontSizeAdjustDialog {
  deviceType: DEVICE_TYPES = DEVICE_TYPES.TABLET
  fontSize: number = DEFAULT_FONT_SIZE
  @State tempFontSize: number = DEFAULT_FONT_SIZE
  controller: CustomDialogController = new CustomDialogController({ builder: "" })
  onConfirm?: (fontSize: number) => void
  onCancel?: () => void

  aboutToAppear(): void {
    this.tempFontSize = this.fontSize
  }

  build() {
    Column() {
      Text('字体大小调整')
        .fontSize(22)
        .fontWeight(600)
        .fontColor($r('app.color.font_adjust_dialog_title'))
        .margin({ bottom: 20 })

      Text(`当前大小: ${this.tempFontSize}`)
        .fontSize(18)
        .fontColor($r('app.color.font_adjust_dialog_text'))
        .margin({ bottom: 10 })

      Text('示例文字 Example Text')
        .fontSize(this.tempFontSize)
        .fontColor($r('app.color.font_adjust_dialog_text'))
        .margin({ bottom: 20 })

      Row() {
        Text('小')
          .fontSize(12)
          .fontColor($r('app.color.font_adjust_dialog_text'))
        Slider({
          value: this.tempFontSize,
          min: 12,
          max: 24,
          step: 1
        })
          .layoutWeight(1)
          .margin({ left: 15, right: 15 })
          .trackColor($r('app.color.font_adjust_slider_track'))
          .selectedColor($r('app.color.font_adjust_slider_selected'))
          .blockColor($r('app.color.font_adjust_slider_selected'))
          .onChange((value: number) => {
            this.tempFontSize = Math.round(value)
          })
        Text('大')
          .fontSize(18)
          .fontColor($r('app.color.font_adjust_dialog_text'))
      }
      .width('100%')
      .margin({ bottom: 30 })

      Row() {
        Button('取消')
          .fontSize(16)
          .backgroundColor($r('app.color.font_adjust_cancel_bg'))
          .fontColor($r('app.color.font_adjust_cancel_text'))
          .border({ width: 1, color: $r('app.color.font_adjust_dialog_border') })
          .width(100)
          .height(40)
          .onClick(() => {
            this.onCancel?.()
            this.controller.close()
          })

        Button('确认')
          .fontSize(16)
          .backgroundColor($r('app.color.font_adjust_confirm_bg'))
          .fontColor($r('app.color.font_adjust_confirm_text'))
          .width(100)
          .height(40)
          .onClick(() => {
            this.onConfirm?.(this.tempFontSize)
            this.controller.close()
          })
      }
      .width('100%')
      .justifyContent(FlexAlign.SpaceEvenly)
    }
    .width(400)
    .padding(24)
    .backgroundColor($r('app.color.font_adjust_dialog_bg'))
    .borderRadius(12)
  }
}

/**
 * 字体大小调整按钮
 */
@ComponentV2
export struct FontSizeAdjustButton {
  @Local deviceType: DEVICE_TYPES =
    deviceInfo.deviceType === DEVICE_TYPES.PHONE ? DEVICE_TYPES.PHONE : DEVICE_TYPES.TABLET
  @Local fontSize: number = DEFAULT_FONT_SIZE
  @Local showSheet: boolean = false
  @Local tempFontSize: number = DEFAULT_FONT_SIZE

  // 平板弹窗控制器
  private dialogController: CustomDialogController = new CustomDialogController({
    builder: FontSizeAdjustDialog({
      deviceType: this.deviceType,
      fontSize: this.fontSize,
      onConfirm: (fontSize: number) => {
        this.confirmFontSizeChange(fontSize)
      },
      onCancel: () => {
        this.cancelFontSizeChange()
      }
    }),
    alignment: DialogAlignment.Center,
    customStyle: true,
    cancel: () => {
      this.cancelFontSizeChange()
    }
  })

  aboutToAppear(): void {
    this.fontSize = AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!.fontSize
    this.tempFontSize = this.fontSize

    // 更新弹窗控制器
    this.updateDialogController()
  }

  updateDialogController() {
    this.dialogController = new CustomDialogController({
      builder: FontSizeAdjustDialog({
        deviceType: this.deviceType,
        fontSize: this.fontSize,
        onConfirm: (fontSize: number) => {
          this.confirmFontSizeChange(fontSize)
        },
        onCancel: () => {
          this.cancelFontSizeChange()
        }
      }),
      alignment: DialogAlignment.Center,
      customStyle: true,
      cancel: () => {
        this.cancelFontSizeChange()
      }
    })
  }

  toggleAdjustPanel() {
    logger.debug(`${FontSizeAdjustButton_LOG_TAG}字体大小调整面板切换`)
    this.updateDialogController()

    if (this.deviceType === DEVICE_TYPES.PHONE) {
      // 手机使用半模态
      this.showSheet = !this.showSheet
      if (this.showSheet) {
        this.tempFontSize = this.fontSize
      }
    } else {
      // 平板使用自定义弹窗
      this.dialogController.open()
    }
  }

  onFontSizeChange(value: number) {
    this.tempFontSize = value
    logger.debug(`${FontSizeAdjustButton_LOG_TAG}字体大小临时调整为: ${value}`)
  }

  confirmFontSizeChange(fontSize?: number) {
    const newFontSize = fontSize || this.tempFontSize
    this.fontSize = newFontSize
    AppStorageV2.connect(UserConfigViewModel, GET_USER_CONFIG, () => new UserConfigViewModel())!.fontSize = this.fontSize
    userConfigManager.syncDataToPreference()
    this.showSheet = false
    logger.info(`${FontSizeAdjustButton_LOG_TAG}字体大小已确认更改为: ${this.fontSize}`)

    try {
      promptAction.openToast({
        message: `字体大小已调整为 ${this.fontSize}`,
        duration: 1500
      })
    } catch (error) {
      // 兼容旧版本API
      promptAction.showToast({
        message: `字体大小已调整为 ${this.fontSize}`,
        duration: 1500
      })
    }
  }

  cancelFontSizeChange() {
    this.tempFontSize = this.fontSize
    this.showSheet = false
    logger.debug(`${FontSizeAdjustButton_LOG_TAG}字体大小调整已取消，保持为: ${this.fontSize}`)
  }

  @Builder
  FontSizeSheet() {
    Column() {
      Text('字体大小调整')
        .fontSize(this.deviceType === DEVICE_TYPES.PHONE ? 18 : 22)
        .fontWeight(600)
        .fontColor($r('app.color.font_adjust_dialog_title'))
        .margin({ bottom: 20 })

      Text(`当前大小: ${this.tempFontSize}`)
        .fontSize(this.deviceType === DEVICE_TYPES.PHONE ? 14 : 18)
        .fontColor($r('app.color.font_adjust_dialog_text'))
        .margin({ bottom: 10 })

      Text('示例文字 Example Text')
        .fontSize(this.tempFontSize)
        .fontColor($r('app.color.font_adjust_dialog_text'))
        .margin({ bottom: 20 })

      Row() {
        Text('小')
          .fontSize(12)
          .fontColor($r('app.color.font_adjust_dialog_text'))
        Slider({
          value: this.tempFontSize,
          min: 12,
          max: 24,
          step: 1
        })
          .layoutWeight(1)
          .margin({ left: 10, right: 10 })
          .trackColor($r('app.color.font_adjust_slider_track'))
          .selectedColor($r('app.color.font_adjust_slider_selected'))
          .blockColor($r('app.color.font_adjust_slider_selected'))
          .onChange((value: number) => {
            this.onFontSizeChange(Math.round(value))
          })
        Text('大')
          .fontSize(18)
          .fontColor($r('app.color.font_adjust_dialog_text'))
      }
      .width('100%')
      .margin({ bottom: 30 })

      Row() {
        Button('取消')
          .fontSize(this.deviceType === DEVICE_TYPES.PHONE ? 16 : 18)
          .backgroundColor($r('app.color.font_adjust_cancel_bg'))
          .fontColor($r('app.color.font_adjust_cancel_text'))
          .border({ width: 1, color: $r('app.color.font_adjust_dialog_border') })
          .width(this.deviceType === DEVICE_TYPES.PHONE ? 80 : 100)
          .height(this.deviceType === DEVICE_TYPES.PHONE ? 40 : 45)
          .onClick(() => {
            this.cancelFontSizeChange()
          })

        Button('确认')
          .fontSize(this.deviceType === DEVICE_TYPES.PHONE ? 16 : 18)
          .backgroundColor($r('app.color.font_adjust_confirm_bg'))
          .fontColor($r('app.color.font_adjust_confirm_text'))
          .width(this.deviceType === DEVICE_TYPES.PHONE ? 80 : 100)
          .height(this.deviceType === DEVICE_TYPES.PHONE ? 40 : 45)
          .onClick(() => {
            this.confirmFontSizeChange()
          })
      }
      .width('100%')
      .justifyContent(FlexAlign.SpaceEvenly)
    }
    .width('100%')
    .padding(20)
  }

  build() {
    if (this.deviceType === DEVICE_TYPES.PHONE) {
      // 手机使用 bindSheet
      Stack({ alignContent: Alignment.Center }) {
        Image($rawfile('colorButtonBG.svg'))
          .width('90%')
          .height('90%')
          .fillColor($r('app.color.color_change_button_svg'))
        Text('字')
          .fontSize(20)
          .fontWeight(800)
          .fontColor($r('app.color.color_change_button_font'))
      }
      .width(35)
      .height(35)
      .shadow({
        color: Color.Black,
        radius: 10
      })
      .backgroundColor($r('app.color.color_change_button_background'))
      .onClick(() => {
        this.toggleAdjustPanel()
      })
      .borderRadius(99)
      .bindSheet(this.showSheet, this.FontSizeSheet(), {
        height: 300,
        dragBar: true,
        maskColor: Color.Black,
        backgroundColor: $r('app.color.font_adjust_sheet_bg'),
        onDisappear: () => {
          this.cancelFontSizeChange()
        }
      })
    } else {
      // 平板只使用按钮，不使用 bindSheet
      Stack({ alignContent: Alignment.Center }) {
        Image($rawfile('colorButtonBG.svg'))
          .width('90%')
          .height('90%')
          .fillColor($r('app.color.color_change_button_svg'))
        Text('字')
          .fontSize(30)
          .fontWeight(800)
          .fontColor($r('app.color.color_change_button_font'))
      }
      .width(45)
      .height(45)
      .shadow({
        color: Color.Black,
        radius: 10
      })
      .backgroundColor($r('app.color.color_change_button_background'))
      .onClick(() => {
        this.toggleAdjustPanel()
      })
      .borderRadius(99)
    }
  }
}