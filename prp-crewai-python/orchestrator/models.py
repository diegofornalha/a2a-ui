from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentCapability(str, Enum):
    # Estrategista
    ANALYZE_MARKET = "ANALYZE_MARKET"
    DEFINE_PERSONAS = "DEFINE_PERSONAS"
    BUDGET_PLANNING = "BUDGET_PLANNING"
    COMPETITIVE_ANALYSIS = "COMPETITIVE_ANALYSIS"
    ROI_PROJECTION = "ROI_PROJECTION"
    STRATEGY_CREATION = "STRATEGY_CREATION"
    KPI_DEFINITION = "KPI_DEFINITION"
    BRIEFING_GENERATION = "BRIEFING_GENERATION"
    
    # Criativo Visual
    IMAGE_GENERATION = "IMAGE_GENERATION"
    VISUAL_ANALYSIS = "VISUAL_ANALYSIS"
    RESPONSIVE_DESIGN = "RESPONSIVE_DESIGN"
    AB_TESTING_VISUAL = "AB_TESTING_VISUAL"
    UGC_STYLE_CREATION = "UGC_STYLE_CREATION"
    CAROUSEL_DESIGN = "CAROUSEL_DESIGN"
    VIDEO_STORYBOARD = "VIDEO_STORYBOARD"
    COLOR_OPTIMIZATION = "COLOR_OPTIMIZATION"
    
    # Copywriter
    HEADLINE_CREATION = "HEADLINE_CREATION"
    STORYTELLING = "STORYTELLING"
    VIDEO_COPYWRITING = "VIDEO_COPYWRITING"
    CTA_OPTIMIZATION = "CTA_OPTIMIZATION"
    MENTAL_TRIGGERS = "MENTAL_TRIGGERS"
    AB_TESTING_COPY = "AB_TESTING_COPY"
    HOOK_DEVELOPMENT = "HOOK_DEVELOPMENT"
    CAROUSEL_NARRATIVE = "CAROUSEL_NARRATIVE"
    
    # Otimizador
    PERFORMANCE_ANALYSIS = "PERFORMANCE_ANALYSIS"
    BUDGET_OPTIMIZATION = "BUDGET_OPTIMIZATION"
    AUDIENCE_SEGMENTATION = "AUDIENCE_SEGMENTATION"
    BID_STRATEGY = "BID_STRATEGY"
    CONVERSION_TRACKING = "CONVERSION_TRACKING"
    CREATIVE_SCORING = "CREATIVE_SCORING"
    CAMPAIGN_AUTOMATION = "CAMPAIGN_AUTOMATION"
    REPORT_GENERATION = "REPORT_GENERATION"


class AgentInfo(BaseModel):
    id: str
    name: str
    role: str
    port: int
    capabilities: List[AgentCapability]
    status: str = "offline"
    url: Optional[str] = None
    last_seen: Optional[datetime] = None


class Task(BaseModel):
    id: str
    agent_id: str
    type: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TaskResult(BaseModel):
    task_id: str
    agent_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class CampaignRequest(BaseModel):
    client_name: str
    business_type: str
    campaign_goal: str
    target_audience: Dict[str, Any]
    budget: float
    currency: str = "BRL"
    duration_days: int
    platforms: List[str] = ["Facebook", "Instagram"]
    additional_info: Optional[str] = None
    
    
class CampaignStrategy(BaseModel):
    strategy_id: str
    client_name: str
    objectives: List[str]
    target_personas: List[Dict[str, Any]]
    budget_allocation: Dict[str, float]
    kpis: Dict[str, Any]
    timeline: Dict[str, Any]
    recommendations: List[str]
    created_by: str = "Estrategista de Campanhas"
    created_at: datetime = Field(default_factory=datetime.now)


class CreativeAsset(BaseModel):
    asset_id: str
    campaign_id: str
    type: str  # image, video, carousel
    variations: List[Dict[str, Any]]
    dimensions: Dict[str, int]
    color_palette: List[str]
    style_guidelines: Dict[str, Any]
    created_by: str = "Criativo Visual"
    created_at: datetime = Field(default_factory=datetime.now)


class CopyContent(BaseModel):
    copy_id: str
    campaign_id: str
    headlines: List[str]
    primary_text: List[str]
    cta_options: List[str]
    hooks: List[str]
    mental_triggers: List[str]
    variations: Dict[str, List[str]]
    created_by: str = "Copywriter"
    created_at: datetime = Field(default_factory=datetime.now)


class OptimizationReport(BaseModel):
    report_id: str
    campaign_id: str
    performance_metrics: Dict[str, float]
    recommendations: List[Dict[str, Any]]
    budget_adjustments: Dict[str, float]
    audience_insights: Dict[str, Any]
    creative_scores: Dict[str, float]
    next_actions: List[str]
    created_by: str = "Otimizador de Performance"
    created_at: datetime = Field(default_factory=datetime.now)