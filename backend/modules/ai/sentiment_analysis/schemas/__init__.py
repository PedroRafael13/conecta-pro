"""Sentiment Analysis Schemas."""

from modules.ai.sentiment_analysis.schemas.sentiment_schemas import (
    # Analysis
    SentimentAnalysisCreate,
    SentimentAnalysisUpdate,
    SentimentAnalysisResponse,
    SentimentAnalysisListResponse,
    SentimentAnalysisSummary,
    AnalyzeTextRequest,
    AnalyzeTextResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    # Rule
    SentimentRuleCreate,
    SentimentRuleUpdate,
    SentimentRuleResponse,
    SentimentRuleListResponse,
    RuleEvaluationResult,
    # Trend
    SentimentTrendResponse,
    SentimentTrendListResponse,
    TrendSummary,
    TrendComparisonResponse,
    # Insight
    FeedbackInsightCreate,
    FeedbackInsightUpdate,
    FeedbackInsightResponse,
    FeedbackInsightListResponse,
    InsightSummary,
    # Dashboard
    SentimentDashboardResponse,
    SentimentMetricsResponse,
    EmotionDistributionResponse,
    AspectAnalysisResponse,
    # Filters
    SentimentAnalysisFilter,
    TrendFilter,
    InsightFilter,
)

__all__ = [
    # Analysis
    "SentimentAnalysisCreate",
    "SentimentAnalysisUpdate",
    "SentimentAnalysisResponse",
    "SentimentAnalysisListResponse",
    "SentimentAnalysisSummary",
    "AnalyzeTextRequest",
    "AnalyzeTextResponse",
    "BatchAnalyzeRequest",
    "BatchAnalyzeResponse",
    # Rule
    "SentimentRuleCreate",
    "SentimentRuleUpdate",
    "SentimentRuleResponse",
    "SentimentRuleListResponse",
    "RuleEvaluationResult",
    # Trend
    "SentimentTrendResponse",
    "SentimentTrendListResponse",
    "TrendSummary",
    "TrendComparisonResponse",
    # Insight
    "FeedbackInsightCreate",
    "FeedbackInsightUpdate",
    "FeedbackInsightResponse",
    "FeedbackInsightListResponse",
    "InsightSummary",
    # Dashboard
    "SentimentDashboardResponse",
    "SentimentMetricsResponse",
    "EmotionDistributionResponse",
    "AspectAnalysisResponse",
    # Filters
    "SentimentAnalysisFilter",
    "TrendFilter",
    "InsightFilter",
]
