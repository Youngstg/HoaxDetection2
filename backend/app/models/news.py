from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal
from enum import Enum


class LabeledByEnum(str, Enum):
    SYSTEM = "system"      # Auto-labeled by ML/rule-based
    ADMIN = "admin"        # Manually labeled by admin
    USER = "user"          # Checked by user (NOT for training)


class NewsItem(BaseModel):
    id: Optional[str] = None
    title: str
    link: str
    content: str
    source: str
    published_time: Optional[datetime] = None
    hoax_label: Optional[str] = None  # "hoax" or "non-hoax"
    confidence: Optional[float] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

    # New fields for admin/user distinction
    labeled_by: Optional[str] = "system"  # "system", "admin", "user"
    manual_label: Optional[str] = None    # Admin's manual label (overrides hoax_label)
    is_verified: Optional[bool] = False   # Has been verified by admin
    can_use_for_training: Optional[bool] = False  # Only admin-labeled data = True
    trained: Optional[bool] = False       # Has been used in training
    labeled_at: Optional[datetime] = None # When the label was applied


class NewsResponse(BaseModel):
    id: str
    title: str
    link: str
    content: str
    source: str
    published_time: Optional[str] = None
    hoax_label: Optional[str] = None
    confidence: Optional[float] = None
    created_at: str

    # New fields
    labeled_by: Optional[str] = "system"
    manual_label: Optional[str] = None
    is_verified: Optional[bool] = False
    can_use_for_training: Optional[bool] = False
    trained: Optional[bool] = False
    labeled_at: Optional[str] = None


class NewsListResponse(BaseModel):
    total: int
    news: list[NewsResponse]


class HoaxPrediction(BaseModel):
    label: str
    confidence: float


# ==========================================
# Admin Label Models
# ==========================================

class AdminLabelRequest(BaseModel):
    """Request model for admin to label news"""
    news_id: str
    label: Literal["hoax", "non-hoax"]
    notes: Optional[str] = None


class AdminLabelResponse(BaseModel):
    """Response after admin labels news"""
    success: bool
    message: str
    news_id: str
    label: str
    can_use_for_training: bool


# ==========================================
# User Checker Models
# ==========================================

class UserCheckRequest(BaseModel):
    """Request model for user to check news"""
    title: Optional[str] = None
    content: str
    url: Optional[str] = None


class UserCheckResponse(BaseModel):
    """Response for user hoax check"""
    prediction: str  # "hoax" or "non-hoax"
    confidence: float
    message: str
    warning: Optional[str] = None


# ==========================================
# Training Queue Models
# ==========================================

class TrainingDataItem(BaseModel):
    """Item in training queue"""
    id: str
    text: str
    label: int  # 0 = non-hoax, 1 = hoax
    source: str
    url: str
    labeled_by: str
    labeled_at: datetime
    trained: bool = False


class TrainingQueueStatus(BaseModel):
    """Status of training queue"""
    total_pending: int
    total_trained: int
    ready_for_training: bool  # True if pending >= 50
    threshold: int = 50


class RetrainResponse(BaseModel):
    """Response after retraining"""
    success: bool
    message: str
    samples_used: int
    accuracy: Optional[float] = None
    f1_score: Optional[float] = None
