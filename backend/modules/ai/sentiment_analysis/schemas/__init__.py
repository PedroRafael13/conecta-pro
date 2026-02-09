"""Sentiment Analysis Schemas."""

from modules.ai.sentiment_analysis.schemas.sentiment_schemas import (
    AnalyzeTextRequest,
    AnalyzeTextResponse,
    AspectAnalysisResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    EmotionDistributionResponse,
    # Insight
    FeedbackInsightCreate,
    FeedbackInsightListResponse,
    FeedbackInsightResponse,
    FeedbackInsightUpdate,
    InsightFilter,
    InsightSummary,
    RuleEvaluationResult,
    # Analysis
    SentimentAnalysisCreate,
    # Filters
    SentimentAnalysisFilter,
    SentimentAnalysisListResponse,
    SentimentAnalysisResponse,
    SentimentAnalysisSummary,
    SentimentAnalysisUpdate,
    # Dashboard
    SentimentDashboardResponse,
    SentimentMetricsResponse,
    # Rule
    SentimentRuleCreate,
    SentimentRuleListResponse,
    SentimentRuleResponse,
    SentimentRuleUpdate,
    SentimentTrendListResponse,
    # Trend
    SentimentTrendResponse,
    TrendComparisonResponse,
    TrendFilter,
    TrendSummary,
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
