from dataclasses import dataclass, field
from typing import Dict


# --------------------------------------------------
# Individual TRIPOD+AI Item
# --------------------------------------------------

@dataclass
class TripodItem:
    tid: str
    description: str
    score: float          # 1.0 = Adequate, 0.0 = Inadequate
    reason: str
    applicable: bool = True


# --------------------------------------------------
# Domain-Level Score
# --------------------------------------------------

@dataclass
class DomainScore:
    name: str
    score_percent: float
    applicable: int
    adequate: int


# --------------------------------------------------
# Reporting Characteristics
# --------------------------------------------------

@dataclass
class ReportingProfile:
    validation_method: str = "Not reported"
    explainability_method: str = "Not reported"
    hyperparameter_tuning: bool = False
    external_validation: bool = False
    calibration_reported: bool = False
    decision_curve_analysis: bool = False
    code_available: bool = False

# --------------------------------------------------
# Final SamTripodAI Report
# --------------------------------------------------

@dataclass
class TripodAIReport:
    paper_title: str = "Unknown Paper"
    overall_compliance: float = 0.0
    high_quality: bool = False
    total_applicable: int = 0

    items: Dict[str, TripodItem] = field(default_factory=dict)
    domain_scores: Dict[str, DomainScore] = field(default_factory=dict)
    reporting_profile: ReportingProfile = field(default_factory=ReportingProfile)

    version: str = "2.0"

    def to_markdown(self) -> str:
        """Generate a Markdown summary of the TRIPOD+AI assessment."""

        lines = []

        # -----------------------------
        # Header
        # -----------------------------

        lines.append(f"# TripodAI Report")
        lines.append(f"**Paper:** {self.paper_title}")
        lines.append(f"**Version:** {self.version}")
        lines.append("")
        lines.append(f"**Overall Compliance:** {self.overall_compliance:.1f}%")
        lines.append(f"**High-Quality Reporting (≥75%):** {'Yes' if self.high_quality else 'No'}")
        lines.append(f"**Applicable Items:** {self.total_applicable}/27")
        lines.append("")

        # -----------------------------
        # Domain Scores
        # -----------------------------

        lines.append("## Domain Scores")

        for ds in self.domain_scores.values():
            lines.append(
                f"- **{ds.name}**: "
                f"{ds.score_percent:.1f}% "
                f"({ds.adequate}/{ds.applicable})"
            )

        # -----------------------------
# Reporting Characteristics
# -----------------------------

        rp = self.reporting_profile

        lines.append("")
        lines.append("## Reporting Characteristics")

        lines.append(f"- Validation Method: {rp.validation_method}")
        lines.append(f"- Explainability: {rp.explainability_method}")
        lines.append(
            f"- Hyperparameter Tuning: "
            f"{'Yes' if rp.hyperparameter_tuning else 'No'}"
        )
        lines.append(
            f"- External Validation: "
            f"{'Yes' if rp.external_validation else 'No'}"
        )
        lines.append(
            f"- Calibration Reported: "
            f"{'Yes' if rp.calibration_reported else 'No'}"
        )
        lines.append(
            f"- Decision Curve Analysis: "
            f"{'Yes' if rp.decision_curve_analysis else 'No'}"
        )
        lines.append(
            f"- Code Available: "
            f"{'Yes' if rp.code_available else 'No'}"
        )
        # -----------------------------
        # Individual TRIPOD+AI Items
        # -----------------------------

        lines.append("")
        lines.append("## Individual TRIPOD+AI Items")

        for tid, item in self.items.items():

            if not item.applicable:
                status = "Not Applicable"
            elif item.score == 1.0:
                status = "Adequate"
            else:
                status = "Inadequate"

            lines.append(
            f"- **{tid}** ({status}) {item.description}\n"
            f"  - {item.reason}"
            )

        return "\n".join(lines)
