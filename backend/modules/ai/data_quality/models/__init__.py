"""
Data Quality Models - Sprint 48.

Modelos para validação, limpeza e qualidade de dados.
"""

from .data_quality_rule import (
    DataQualityRule,
    RuleTypeEnum,
    RuleSeverityEnum,
    RuleStatusEnum,
    RuleCategoryEnum,
)
from .data_quality_check import (
    DataQualityCheck,
    CheckStatusEnum,
    CheckScopeEnum,
    CheckTriggerEnum,
)
from .data_quality_issue import (
    DataQualityIssue,
    IssueSeverityEnum,
    IssueStatusEnum,
    IssueTypeEnum,
)
from .duplicate_record import (
    DuplicateRecord,
    DuplicateStatusEnum,
    DuplicateTypeEnum,
    MergeStrategyEnum,
)
from .data_profile import (
    DataProfile,
    ProfileStatusEnum,
    DataTypeEnum,
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
