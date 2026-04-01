"""Skills IA de Recursos Humanos."""

from modules.people_management.human_resources.skills.evaluator_skill import EvaluatorSkill
from modules.people_management.human_resources.skills.onboarder_skill import OnboarderSkill
from modules.people_management.human_resources.skills.predictor_skill import PredictorSkill
from modules.people_management.human_resources.skills.recruiter_skill import RecruiterSkill
from modules.people_management.human_resources.skills.trainer_skill import TrainerSkill

__all__ = [
    "RecruiterSkill",
    "TrainerSkill",
    "EvaluatorSkill",
    "PredictorSkill",
    "OnboarderSkill",
]
