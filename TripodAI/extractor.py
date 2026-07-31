import re
from .rules import NA_RULES, ADEQUATE_KEYWORDS
from .models import (
    TripodItem,
    DomainScore,
    ReportingProfile,
    TripodAIReport,
)

ITEM_SECTION = {
    "T1": "abstract",
    "T2": "abstract",

    "T3": "introduction",
    "T4": "introduction",

    "T5": "methods",
    "T6": "methods",
    "T7": "methods",
    "T8": "methods",
    "T9": "methods",
    "T10": "methods",
    "T11": "methods",
    "T12": "methods",
    "T13": "methods",
    "T14": "methods",
    "T15": "methods",
    "T16": "methods",
    "T17": "methods",
    "T18": "methods",

    "T19": "results",
    "T20": "results",
    "T21": "results",
    "T22": "results",
    "T23": "results",

    "T24": "discussion",
    "T25": "discussion",
    "T26": "discussion",
    "T27": "discussion",
}
class TripodAIExtractor:
    def __init__(self):
        self.items = self._define_items()
        self.domains = self._define_domains()

    def _define_items(self):
        return {
            "T1": "T1  Study identified as prediction model",
            "T2": "Title and Abstract - Structured abstract with performance metrics",
            "T3": "Introduction - Clinical or public health context",
            "T4": "Introduction - Objective specification",
            "T5": "Methods - Study design",
            "T6": "Methods - Setting and recruitment",
            "T7": "Methods - Eligibility criteria",
            "T8": "Methods - Sample size justification",
            "T9": "Methods - Outcome definition",
            "T10": "Methods - Predictor description",
            "T11": "Methods - Blinding procedures",
            "T12": "Methods - Handling of missing data",
            "T13": "Methods - Algorithm type specified",
            "T14": "Methods - Hyperparameter tuning described",
            "T15": "Methods - Feature selection method",
            "T16": "Methods - Internal validation method",
            "T17": "Methods - Class imbalance handling",
            "T18": "Methods - Software/framework specified",
            "T19": "Results - Discrimination metrics",
            "T20": "Results - Calibration metrics",
            "T21": "Results - Confidence intervals",
            "T22": "Results - Decision-curve analysis",
            "T23": "Results - External validation",
            "T24": "Discussion - Code availability",
            "T25": "Discussion - Data availability",
            "T26": "Discussion - Model equation/architecture",
            "T27": "Discussion - Funding/conflict disclosure",
        }

    def _define_domains(self):
        return {
            "Title & Abstract": ["T1", "T2"],
            "Introduction": ["T3", "T4"],
            "Methods": ["T5", "T6", "T7", "T8"],
            "Model Development": [
                "T9", "T10", "T11", "T12",
                "T13", "T14", "T15", "T16",
                "T17", "T18",
            ],
            "Model Performance": [
                "T19", "T20", "T21", "T22", "T23",
            ],
            "Transparency & Reproducibility": [
                "T24", "T25", "T26", "T27",
            ],
        }

    



    def _extract_sections(self, text):
        """
        Robust section extraction for real-world full-text (HTML scrapes, PDFs, PMC).

        - "summary" treated as abstract alias.
        - Prefers heading-like matches (start of line, short lines).
        - Prefers mid-document structural headings; penalises very-late TOC/nav.
        - Rejects short nav fragments.
        - Extends discussion through data-sharing / COI / funding to References.
        """
        text_lower = text.lower()
        n = len(text_lower)

        heading_aliases = {
            "abstract": ["abstract", "summary"],
            "introduction": ["introduction"],
            "methods": ["methods", "materials and methods", "materials & methods"],
            "results": ["results", "findings"],
            "discussion": ["discussion"],
            "conclusion": ["conclusion", "conclusions"],
            "references": ["references", "bibliography"],
        }

        def _find_heading_candidates(heading: str):
            candidates = []
            pattern = re.compile(
                r"(?:^|[\n\r])\s*(" + re.escape(heading) + r")\s*(?:[\n\r.:]|$)",
                re.MULTILINE,
            )
            for m in pattern.finditer(text_lower):
                pos = m.start(1)
                line_start = text_lower.rfind("\n", 0, pos) + 1
                line_end = text_lower.find("\n", pos)
                if line_end < 0:
                    line_end = n
                line = text_lower[line_start:line_end]
                score = 10
                if len(line.strip()) < 40:
                    score += 5
                else:
                    score -= 8  # mid-sentence

                if heading in (
                    "methods", "results", "materials and methods", "findings"
                ):
                    relative = pos / max(n, 1)
                    if 0.05 < relative < 0.85:
                        score += 15  # mid-document structural
                    elif relative >= 0.85:
                        score -= 25  # footer / TOC / nav
                    else:
                        score += min(pos // 500, 8)

                if heading in ("conclusion", "conclusions") and len(line.strip()) > 30:
                    score -= 15
                candidates.append((pos, score))

            if not candidates and heading not in ("conclusion", "conclusions"):
                for m in re.finditer(r"\b" + re.escape(heading) + r"\b", text_lower):
                    candidates.append((m.start(), 1))
            return candidates

        starts = {}
        for canonical, aliases in heading_aliases.items():
            best_pos, best_score = None, -1
            for alias in aliases:
                for pos, score in _find_heading_candidates(alias):
                    if score > best_score:
                        best_score = score
                        best_pos = pos
            if best_pos is not None and (
                canonical != "conclusion" or best_score >= 10
            ):
                starts[canonical] = best_pos

        sections = {}
        ordered_starts = sorted(
            ((name, pos) for name, pos in starts.items()),
            key=lambda x: x[1],
        )

        nav_keys = (
            "download icon", "follow ncbi", "view on publisher",
            "resources", "on this page", "actions", "skip to main",
        )

        for i, (name, start) in enumerate(ordered_starts):
            end = n
            if i + 1 < len(ordered_starts):
                end = ordered_starts[i + 1][1]
            section_text = text_lower[start:end]
            nav_hits = sum(1 for k in nav_keys if k in section_text[:500])
            if len(section_text) > 200 and nav_hits < 2:
                sections[name] = section_text

        if "abstract" not in sections:
            m = re.search(r"(?:^|[\n\r])\s*summary\b", text_lower, re.MULTILINE)
            if m:
                s = m.start()
                e = starts.get("introduction", starts.get("methods", n))
                sections["abstract"] = text_lower[s:e]

        if "discussion" in sections and "references" in starts:
            disc_start = starts["discussion"]
            ref_start = starts["references"]
            current_end = disc_start + len(sections["discussion"])
            if current_end < ref_start - 100:
                sections["discussion"] = text_lower[disc_start:ref_start]

        return sections


    def analyze(
        self,
        paper_text: str,
        paper_title: str = "Unknown Paper",
) -> TripodAIReport:

    # Extract paper sections once
        sections = self._extract_sections(paper_text)

        results = {}

    # Evaluate every TRIPOD item
        for tid, desc in self.items.items():

            section_name = ITEM_SECTION.get(tid, "")

            # Search the appropriate section; fall back to full text if section missing
            section_text = sections.get(section_name, paper_text)

            score, reason, applicable = self._evaluate_item(
                tid,
                desc,
                section_text,
            )

            # For items frequently described outside the strict section
            # (e.g. external validation in Methods, code/funding after Discussion),
            # retry on full text if the section search failed.
            if score == 0 and applicable and tid in {
                "T5", "T6", "T7", "T8", "T9", "T10", "T12", "T13",
                "T14", "T15", "T16", "T18", "T23", "T24", "T25", "T27"
            }:
                score2, reason2, applicable2 = self._evaluate_item(
                    tid, desc, paper_text
                )
                if score2:
                    score, reason, applicable = score2, reason2, applicable2

            results[tid] = TripodItem(
                tid,
                desc,
                1.0 if score else 0.0,
                reason,
                applicable,
            )

        domain_scores = {}

        for domain, items in self.domains.items():

            applicable = sum(
                results[item].applicable
                for item in items
            )

            adequate = sum(
                results[item].score == 1.0
                for item in items
                if results[item].applicable
            )

            compliance = (
                round(adequate / applicable * 100, 1)
                if applicable
                else 0.0
            )

            domain_scores[domain] = DomainScore(
                domain,
                compliance,
                applicable,
                adequate,
            )

        total_applicable = sum(
            item.applicable
            for item in results.values()
        )

        total_adequate = sum(
            item.score == 1.0
            for item in results.values()
            if item.applicable
        )

        overall = (
            round(total_adequate / total_applicable * 100, 1)
            if total_applicable
            else 0.0
        )

        reporting_profile = self._extract_reporting_profile(
            paper_text
        )

        return TripodAIReport(
            paper_title=paper_title,
            overall_compliance=overall,
            high_quality=overall >= 75,
            total_applicable=total_applicable,
            items=results,
            domain_scores=domain_scores,
            reporting_profile=reporting_profile,
        )

    def _evaluate_item(
        self,
        tid: str,
        desc: str,
        text: str,
    ):

        text_lower = text.lower()

        # ---------------------------------
        # Not Applicable Rules
        # ---------------------------------

        if tid in NA_RULES and NA_RULES[tid](text_lower):
            return 0, f"Not Applicable - {desc}", False

        # ---------------------------------
        # Special rule for T26
        # ---------------------------------

        if tid == "T26":

            equation = any(
                k in text_lower
                for k in [
                    "equation",
                    "formula",
                    "regression equation",
                    "coefficients",
                    "beta coefficients",
                    "risk score",
                    "nomogram",
                    "online calculator",
                    "web calculator",
                ]
            )

            architecture = any(
                k in text_lower
                for k in [
                    "model architecture",
                    "network architecture",
                    "neural network architecture",
                    "number of layers",
                    "hidden layers",
                    "convolutional layer",
                    "fully connected layer",
                    "dense layer",
                    "input layer",
                    "output layer",
                    "pooling layer",
                    "attention layer",
                    "embedding layer",]
                )

            if equation or architecture:
                return 1, "Adequately reported", True

            return 0, "Inadequately reported", True

        # ---------------------------------
        # Generic keyword engine
        # ---------------------------------

        keywords = ADEQUATE_KEYWORDS.get(tid, [])

        for keyword in keywords:
            if keyword in text_lower:
                return 1, "Adequately reported", True

        return 0, "Inadequately reported", True
        

        
      

    def _extract_reporting_profile(
        self,
        text: str,
    ) -> ReportingProfile:

        text_lower = text.lower()
        profile = ReportingProfile()

        # -----------------------------
        # Validation Method
        # -----------------------------

        if any(
            k in text_lower
            for k in [
                "cross-validation",
                "cross validation",
                "k-fold",
                "five-fold",
                "5-fold",
                "10-fold",
                "bootstrap",
                "hold-out",
                "holdout",
                "split-sample",
            ]
        ):
            profile.validation_method = "Internal validation"

        elif any(
            k in text_lower
            for k in [
                "external validation",
                "external cohort",
                "independent cohort",
                "temporal validation",
                "geographical validation",
            ]
        ):
            profile.validation_method = "External validation"

        # -----------------------------
        # Explainability
        # -----------------------------

        if "shap" in text_lower:
            profile.explainability_method = "SHAP"

        elif "lime" in text_lower:
            profile.explainability_method = "LIME"

        elif "grad-cam" in text_lower:
            profile.explainability_method = "Grad-CAM"

        elif "partial dependence" in text_lower:
            profile.explainability_method = "Partial Dependence Plot"

        elif "feature importance" in text_lower:
            profile.explainability_method = "Feature Importance"

        # -----------------------------
        # Hyperparameter Tuning
        # -----------------------------

        profile.hyperparameter_tuning = any(
            k in text_lower
            for k in [
                "hyperparameter",
                "grid search",
                "random search",
                "bayesian optimization",
                "optuna",
                "learning rate",
            ]
        )

        # -----------------------------
        # External Validation
        # -----------------------------

        profile.external_validation = any(
            k in text_lower
            for k in [
                "external validation",
                "independent cohort",
                "temporal validation",
                "geographical validation",
            ]
        )

        # -----------------------------
        # Calibration
        # -----------------------------

        profile.calibration_reported = any(
            k in text_lower
            for k in [
                "calibration",
                "calibration plot",
                "calibration curve",
                "calibration slope",
                "calibration intercept",
                "hosmer-lemeshow",
            ]
        )

        # -----------------------------
        # Decision Curve Analysis
        # -----------------------------

        profile.decision_curve_analysis = any(
            k in text_lower
            for k in [
                "decision curve",
                "decision-curve",
                "decision curve analysis",
                "net benefit",
            ]
        )

        # -----------------------------
        # Code Availability
        # -----------------------------

        profile.code_available = any(
            k in text_lower
            for k in [
                "github",
                "gitlab",
                "figshare",
                "zenodo",
                "source code",
                "code available",
                "code availability",
                "research code",
            ]
        )

        return profile
