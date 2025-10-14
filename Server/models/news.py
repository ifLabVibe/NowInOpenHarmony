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
from enum import Enum

class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    CODE = "code"

class NewsContentBlock(BaseModel):
    type: ContentType
    value: str

class NewsArticle(BaseModel):
    id: Optional[str] = None
    title: str
    date: str
    url: str
    content: List[NewsContentBlock]
    category: Optional[str] = None
    summary: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class NewsResponse(BaseModel):
    articles: List[NewsArticle]
    total: int
    page: int
    page_size: int
    has_next: bool = Field(False, description="是否有下一页")
    has_prev: bool = Field(False, description="是否有上一页")

class SearchRequest(BaseModel):
    keyword: str
    category: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class TopicArticle(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    author: str
    reply_count: int = 0
    view_count: int = 0
    tags: List[str] = []
    created_at: Optional[datetime] = None
    url: str

class ReleaseInfo(BaseModel):
    id: Optional[str] = None
    version: str
    title: str
    release_date: str
    description: str
    features: List[str] = []
    bug_fixes: List[str] = []
    compatibility: Optional[str] = None
    download_url: Optional[str] = None
    created_at: Optional[datetime] = None