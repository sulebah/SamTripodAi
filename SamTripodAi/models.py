from dataclasses import dataclass
from typing import Dict

@dataclass
class TripodItem:
    tid: str
    description: str
    score: float        # 1.0 = Yes, 0.0 = No (Partial forced to 0)
    reason: str
    applicable: bool

@dataclass
class DomainScore:
    name: str
    score_percent: float
    applicable: int
    adequate: int       # only full 1.0 counts as adequate

@dataclass
class ArchitectureProfile:
    baseline_model: str = "Not reported"
    winning_model: str = "Not reported"
    explainability_method: str = "Not reported"

@dataclass
class SamTripodAIReport:
    paper_title: str = "Unknown Paper"
    overall_compliance: float = 0.0
    high_quality: bool = False
    total_applicable: int = 0
    items: Dict[str, TripodItem] = None
    domain_scores: Dict[str, DomainScore] = None
    architecture_profile: ArchitectureProfile = None

    def to_markdown(self) -> str:
        lines = [f"**SamTripodAi Report: {self.paper_title}**\n"]
        lines.append(f"**Overall Compliance:** {self.overall_compliance}% (Partial scored as 0)")
        lines.append(f"**High Quality Reporting:** {'Yes' if self.high_quality else 'No'} (>=75%)\n")

        lines.append("**Domain Scores:**")
        for ds in self.domain_scores.values():
            lines.append(f"* {ds.name}: {ds.score_percent}%")

        lines.append("\n**Model Architecture & Interpretability Profile**")
        lines.append(f"* Baseline Model: {self.architecture_profile.baseline_model}")
        lines.append(f"* Winning Model: {self.architecture_profile.winning_model}")
        lines.append(f"* Explainability Method: {self.architecture_profile.explainability_method}\n")

        lines.append("**Individual Items:**")
        for tid, item in self.items.items():
            status = "NA" if not item.applicable else item.score
            lines.append(f"* **{tid}**: {status} — {item.reason}")

        return "\n".join(lines)
