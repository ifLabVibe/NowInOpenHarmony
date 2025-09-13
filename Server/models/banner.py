# Copyright (c) 2025 XBXyftx
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class BannerImage(BaseModel):
    """Banner图片简化模型 - 只包含核心路径信息"""
    url: str = Field(..., description="图片URL路径")
    alt: Optional[str] = Field(None, description="图片描述")

class BannerResponse(BaseModel):
    """Banner API响应模型"""
    success: bool = Field(..., description="是否成功")
    images: List[str] = Field(default=[], description="图片URL列表")
    total: int = Field(0, description="图片总数")
    message: str = Field(..., description="响应消息")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="响应时间")
