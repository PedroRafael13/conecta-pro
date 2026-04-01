"""
Data Quality Models - Sprint 48.

Modelos para validação, limpeza e qualidade de dados.
"""

from .data_profile import (
    DataProfile,
    DataTypeEnum,
    ProfileStatusEnum,
)
from .data_quality_check import (
    CheckScopeEnum,
    CheckStatusEnum,
    CheckTriggerEnum,
    DataQualityCheck,
)
from .data_quality_issue import (
    DataQualityIssue,
    IssueSeverityEnum,
    IssueStatusEnum,
    IssueTypeEnum,
)
from .data_quality_rule import (
    DataQualityRule,
    RuleCategoryEnum,
    RuleSeverityEnum,
    RuleStatusEnum,
    RuleTypeEnum,
)
from .duplicate_record import (
    DuplicateRecord,
    DuplicateStatusEnum,
    DuplicateTypeEnum,
    MergeStrategyEnum,
)

__all__ = [
    # Models
    "DataQualityRule",
    "DataQualityCheck",
    "DataQualityIssue",
    "DuplicateRecord",
    "DataProfile",
    # Rule Enums
    "RuleTypeEnum",
    "RuleSeverityEnum",
    "RuleStatusEnum",
    "RuleCategoryEnum",
    # Check Enums
    "CheckStatusEnum",
    "CheckScopeEnum",
    "CheckTriggerEnum",
    # Issue Enums
    "IssueSeverityEnum",
    "IssueStatusEnum",
    "IssueTypeEnum",
    # Duplicate Enums
    "DuplicateStatusEnum",
    "DuplicateTypeEnum",
    "MergeStrategyEnum",
    # Profile Enums
    "ProfileStatusEnum",
    "DataTypeEnum",
]
