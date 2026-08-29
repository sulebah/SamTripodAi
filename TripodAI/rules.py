"""
TripodAi Rule Definitions

Contains:
- TRIPOD+AI keyword rules
- Not Applicable rules
- Shared keyword groups
- Context-aware regex patterns (T8, T24, T25 - tightened per peer review)

Version: 2.2
Last updated: 19 August 2026
"""

import re

# NOTE:
# These keyword rules were developed and refined using manually
# assessed TRIPOD+AI reporting from a corpus of published
# AI prediction model studies.
#
# CHANGE LOG:
# v2.0 -> v2.1: Converted T8, T24, T25 to proximity-based regex
# v2.1 -> v2.2: Increased window, improved URL patterns, removed
#               dangerous negative match in T8, strengthened
#               availability language detection.

# ------------------------------------------------------------------
# Not Applicable (NA) Rules
# ------------------------------------------------------------------

NA_RULES = {
    "T11": lambda t: (
    "retrospective" in t
    or "anonymized" in t
    or "anonymised" in t
    or "de-identified" in t
    or "electronic clinical records" in t
    or "electronic health records" in t
    or "medical records" in t and "retrospective" in t
),
    "T17": lambda t: any(
        k in t.lower()
        for k in [
            "balanced dataset",
            "no class imbalance",
            "weighted loss",
        ]
    ),
}

# ------------------------------------------------------------------
# Shared Keyword Groups
# ------------------------------------------------------------------

CODE_REPOSITORIES = [
    "github",
    "gitlab",
    "bitbucket",
    "zenodo",
    "figshare",
    "hugging face",
]

ML_ALGORITHMS = [
    "xgboost",
    "random forest",
    "svm",
    "neural network",
    "cnn",
    "rnn",
    "lstm",
    "transformer",
    "logistic regression",
    "lasso",
]

VALIDATION_METHODS = [
    "cross-validation",
    "cross validation",
    "bootstrap",
    "k-fold",
    "hold-out",
    "holdout",
    "nested cross-validation",
    "loocv",
    "leave-one-out",
    "split-sample",
]

# ------------------------------------------------------------------
# Context-aware regex rules (T8, T24, T25)
# ------------------------------------------------------------------

WINDOW = 120          # increased from 60
NEGATION_WINDOW = 30
FORWARD_NEGATION_WINDOW = 80  # chars to look ahead past the match, e.g. for
                              # "Data Availability Statement\n\nNot applicable."
                              # where the negation follows a heading-style match
                              # rather than preceding it.

NEGATION_CUES = (
    r"\bnot\b|\bno\b|\bnever\b|\bwithout\b|\bunavailable\b|\bcannot\b|"
    r"\bcan\'?t\b|\bunable\b|\bproprietary\b|\brestricted\b|\bn\'?t\b|"
    r"\bneither\b|\bnor\b|\bfails? to\b|\bdid not\b|\bwas not\b|\bwere not\b|"
    r"\bare not\b|\bis not\b|\bnot made available\b|\bnot publicly\b|"
    r"\bnot applicable\b|\bn\/a\b"
)

def _proximity_pattern(concept_alt, verb_alt, window=WINDOW):
    """Require concept and verb within `window` characters,
    without crossing a sentence boundary."""
    gap = rf"[^.;\n]{{0,{window}}}"
    return re.compile(
        rf"\b({concept_alt})\b{gap}\b({verb_alt})\b"
        rf"|\b({verb_alt})\b{gap}\b({concept_alt})\b",
        re.IGNORECASE,
    )

def _is_negated(text: str, match_start: int, match_text: str) -> bool:
    """Return True if the match is negated.

    Checks three places for a negation cue:
      1. Within the matched text itself.
      2. In a backward window before the match (same sentence only).
      3. In a forward window after the match (bounded by a blank line or
         sentence terminator). This handles heading-style matches such as
         "Data Availability Statement" / "Code Availability" where the
         actual answer ("Not applicable", "N/A") appears on the following
         line rather than being adjacent to the heading text itself.
    """
    if re.search(NEGATION_CUES, match_text, re.IGNORECASE):
        return True

    pre_start = max(0, match_start - NEGATION_WINDOW)
    preceding = text[pre_start:match_start]
    boundary = max(
        preceding.rfind("."), preceding.rfind(";"), preceding.rfind("\n")
    )
    if boundary != -1:
        preceding = preceding[boundary + 1:]
    if re.search(NEGATION_CUES, preceding, re.IGNORECASE) is not None:
        return True

    match_end = match_start + len(match_text)
    fwd_end = min(len(text), match_end + FORWARD_NEGATION_WINDOW)
    following = text[match_end:fwd_end]
    # Stop at the first sentence terminator. Deliberately do NOT stop at a
    # blank line: headings are commonly followed by a blank line and then
    # the actual statement, e.g. "Data Availability Statement\n\nNot
    # applicable." — stopping at the blank line would hide the negation.
    boundary_candidates = [
        p for p in (following.find("."), following.find(";"))
        if p != -1
    ]
    if boundary_candidates:
        following = following[: min(boundary_candidates) + 1]
    return re.search(NEGATION_CUES, following, re.IGNORECASE) is not None

def context_rule_matches(patterns, text) -> bool:
    """Return True if any non-negated pattern matches."""
    for pattern in patterns:
        for m in pattern.finditer(text):
            if not _is_negated(text, m.start(), m.group(0)):
                return True
    return False

# --- T8: Sample size justification ---------------------------------
T8_CONCEPT = r"sample[- ]size|events per variable|epv|power calculation"
T8_VERB = (
    r"justif\w*|calculat\w*|determin\w*|deriv\w*|rationale|"
    r"based on|estimat\w*|required a minimum|minimum (?:of )?\d|"
    r"was calculated|were calculated|we calculated|we estimated"
)

T8_PATTERNS = [
    _proximity_pattern(T8_CONCEPT, T8_VERB, window=100),
    # Explicit common phrases
    re.compile(
        r"\b(?:sample[- ]size|power)\s+(?:calculation|estimation|justification)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bevents[- ]per[- ]variable\b|\bepv\b",
        re.IGNORECASE,
    ),
]

# --- T24: Code availability ----------------------------------------
T24_CODE_CONCEPT = (
    r"(?:source )?code|scripts?|our (?:analysis|research) code|"
    r"analysis pipeline|software code|computer code|code base"
)
T24_AVAIL_VERB = (
    r"available|deposited|archived|hosted|accessible|"
    r"can be (?:found|accessed|obtained|downloaded)|"
    r"is provided|has been (?:made )?(?:publicly )?available|"
    r"open[- ]source|released|shared|published"
)

T24_PATTERNS = [
    _proximity_pattern(T24_CODE_CONCEPT, T24_AVAIL_VERB, window=120),

    # Direct repository / DOI patterns
    re.compile(
        r"(?:code|scripts?|repository|source|code base).{0,80}"
        r"(?:https?://)?(?:www\.)?(?:github\.com|gitlab\.com|bitbucket\.org|"
        r"zenodo\.org|figshare\.com|huggingface\.co|osf\.io)/\S+",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:https?://)?(?:www\.)?(?:github\.com|gitlab\.com|bitbucket\.org|"
        r"zenodo\.org|figshare\.com|huggingface\.co|osf\.io)/\S+"
        r".{0,60}(?:code|scripts?|repository|source)",
        re.IGNORECASE,
    ),

    # Common strong statements
    re.compile(r"\bcode availability\b\s*[:\-]", re.IGNORECASE),
    re.compile(
        r"\b(?:the )?code (?:is|are|was|were) (?:publicly )?available\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bsource code (?:is|are|was|were) (?:publicly )?available\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bcode (?:has been|have been) deposited\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:code|source code|code base) (?:is|are) available on (?:github|gitlab|zenodo)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bavailable on github at https?://github\.com/\S+",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bopen-source version of the code\b",
        re.IGNORECASE,
    ),
]

# --- T25: Data availability (improved v2.2) --------------------------
T25_PATTERNS = [
    # 1. Explicit "data availability" heading / statement
    re.compile(r"\bdata availability\b", re.IGNORECASE),
    re.compile(r"\bavailability of (?:the )?data\b", re.IGNORECASE),

    # 2. Core positive statements (high precision)
    # NOTE: "obtained"/"accessed"/"downloaded" are deliberately excluded here.
    # Those verbs overwhelmingly describe where the STUDY's source data came from
    # (e.g. "data were obtained from NHANES", "the dataset was downloaded from
    # UK Biobank") rather than a statement that the paper's data is available to
    # readers, and were causing false positives. Only genuine availability/sharing
    # verbs are matched directly; "obtained"/"accessed"/"downloaded" are still
    # caught, but only when paired with explicit sharing language (see pattern 2b).
    re.compile(
        r"\b(?:the )?(?:data|dataset|datasets) (?:are|is|were|was|can be) "
        r"(?:publicly )?(?:available|shared)\b",
        re.IGNORECASE,
    ),
    # 2b. Provenance verbs (obtained/accessed/downloaded) only count as an
    # availability statement when paired with explicit "can be" / "may be" /
    # "upon request"-style sharing language, not a bare past-tense description.
    re.compile(
        r"\b(?:data|dataset|datasets) (?:can|may) be "
        r"(?:obtained|accessed|downloaded)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bdata (?:are|is|can be) (?:made )?available "
        r"(?:upon|on|from|to|via|through)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:data|dataset)s? (?:have|has) been (?:deposited|archived|made available)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:anonymi[sz]ed|de-?identified|deidentified) data\b.{0,100}"
        r"\b(?:available|shared|provided|can be (?:obtained|shared|accessed))\b",
        re.IGNORECASE,
    ),

    # 3. "upon (reasonable) request" family – very common in journals
    re.compile(
        r"\b(?:data|datasets?) .{0,60}\b(?:available|provided|shared) "
        r"(?:upon|on) (?:reasonable )?request\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bavailable (?:from|by contacting) the (?:corresponding )?author\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:data|datasets?) (?:are|is) available from the (?:corresponding )?author\b",
        re.IGNORECASE,
    ),

    # 4. Supporting information / supplementary material
    re.compile(
        r"\b(?:data|datasets?) (?:are|is) available (?:in|within) "
        r"(?:the )?(?:article|manuscript|supporting information|supplementary)\b",
        re.IGNORECASE,
    ),

    # 5. Repository / DOI style (keep the good ones)
    re.compile(
        r"\bdata\b.{0,60}(?:zenodo|figshare|dryad|osf\.io|github\.com|doi\.org)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?:zenodo|figshare|dryad|osf\.io).{0,40}\bdata\b",
        re.IGNORECASE,
    ),
]

# --- T23: External validation - Not Applicable detection -------------
# T23 assesses whether EXTERNAL validation results are reported. Per
# TRIPOD+AI, this item is Not Applicable to development-only studies and
# internal-validation-only studies, i.e. studies that never actually
# performed external validation. Merely *mentioning* external validation
# (as a limitation, as future/planned work, or as something "warranted")
# is not the same as having performed it, and must not be scored as
# either adequately reported (1) or inadequately reported (0) - it should
# be excluded from the denominator entirely (Not Applicable).

EXTERNAL_VALIDATION_KEYWORDS = [
    "external validation",
    "externally validated",
    "independent cohort",
    "independent dataset",
    "external dataset",
    "external test set",
    "external cohorts",
    "temporal validation",
    "geographical validation",
    "geographic validation",
    "validated on an independent",
    "held out as external",
    "external test sets",
    "two external",
    "independent external",
    "external evaluation",
]

_T23_EV_CONCEPT = (
    r"external(?:ly)? validat\w*|external (?:cohorts?|datasets?|"
    r"test sets?|evaluation)|independent (?:cohorts?|datasets?)|"
    r"temporal validation|geographic(?:al)? validation"
)

# Cues indicating external validation was NOT actually carried out in
# this study (absent, planned/future, or a stated limitation).
_T23_ABSENCE_CUE = (
    r"was not (?:performed|conducted|undertaken|available|done)|"
    r"were not (?:performed|conducted|undertaken|available|done)|"
    r"is not (?:available|performed|yet available)|"
    r"has not (?:yet )?been (?:performed|conducted|done)|"
    r"did not (?:perform|conduct|undertake|include)|"
    r"does not (?:include|involve)|"
    r"no external validation|not externally validated|"
    r"without external validation|lack(?:s|ing)? of external validation|"
    r"absence of external validation|"
    r"future (?:work|study|studies|research|direction)|"
    r"further (?:external )?(?:validation|studies|work|research)|"
    r"prospective(?:ly)? validat\w*|"
    r"(?:is|remains?|are) (?:needed|required|warranted|necessary)|"
    r"warrants?|should be (?:conducted|performed|validated)|"
    r"remains? to be (?:performed|conducted|done|validated)|"
    r"has yet to be|have yet to be|"
    r"is planned|are planned|will be (?:conducted|performed|undertaken)|"
    r"beyond the scope|out of (?:the )?scope|"
    r"limitation\w*|single[- ]cent(?:er|re) (?:study|design)|"
    r"single[- ]institution"
)

T23_ABSENCE_PATTERNS = [
    _proximity_pattern(_T23_EV_CONCEPT, _T23_ABSENCE_CUE, window=150),
    re.compile(
        r"\bno external validation\s+(?:was|has been|is|were)\s+"
        r"(?:performed|conducted|available|done)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:this|the|our)\s+(?:current\s+)?study\s+(?:did not|does not)\s+"
        r"(?:include|perform|involve|undertake)\s+external validation\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bwithout external validation\b", re.IGNORECASE),
    re.compile(
        r"\bexternal validation\s+(?:is|remains?|was)\s+"
        r"(?:needed|required|warranted|lacking|absent|"
        r"not\s+(?:performed|available|conducted))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\binternal(?:ly)?\s+validat\w*\s+only\b|"
        r"\bonly\s+internal(?:ly)?\s+validat\w*\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:lack|absence)\s+of\s+external validation\b", re.IGNORECASE),
    re.compile(
        r"\bexternal validation\s*(?:studies|cohorts?|datasets?)?\s*"
        r"(?:is|are|will be)?\s*planned\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bno\s+(?:independent|external)\s+(?:cohort|dataset|test set)\s+"
        r"(?:was|is)\s+(?:available|used)\b",
        re.IGNORECASE,
    ),
]


def _t23_not_applicable(text: str) -> bool:
    """
    T23 (reporting of external validation results) is Not Applicable when
    the study did not actually perform external validation - e.g. a
    development-only or internal-validation-only study that merely
    *mentions* external validation as a limitation or as future work.

    Two-part check, either of which is sufficient to mark NA:
      1. Explicit "not performed / future work / limitation" language
         anchored near an external-validation concept.
      2. No external-validation-related phrase appears anywhere in the
         text at all, so there is nothing to report on.

    Whitespace is normalized first (real-world text extracted from PDFs/
    HTML is often hard-wrapped mid-sentence), so a wrapped line break
    between e.g. "external validation" and "is planned" doesn't hide an
    otherwise-adjacent match.
    """
    norm = re.sub(r"\s+", " ", text)

    if any(pattern.search(norm) for pattern in T23_ABSENCE_PATTERNS):
        return True

    if not any(keyword in norm for keyword in EXTERNAL_VALIDATION_KEYWORDS):
        return True

    return False

# ------------------------------------------------------------------
# TRIPOD+AI Keyword Rules (flat keyword items)
# ------------------------------------------------------------------

ADEQUATE_KEYWORDS = {
    "T1": [
    # Core prediction terms
    "prediction", "predict", "predictive", "predicted",
    "prognostic", "prognosis",
    "diagnostic model", "diagnostic algorithm",
    "risk score", "risk prediction", "risk model",
    "model development", "prediction model", "predictive model",
    "machine learning model", "ml model",
    "artificial intelligence model", "ai model",
    "deep learning model",
    
    # Common alternative phrasings
    "to predict", "for predicting", "predicting",
    "identification of", "detect the disease",
    "early identification", "early detection",
    "screening model", "classification model",
    "developed a model", "we developed",
    "algorithm that", "learning algorithm",
],
    "T2": [
        "abstract", "summary", "background",
        "results", "conclusions", "auroc", "brier",
    ],
    "T3": [
        "clinical", "clinical context", "public health", "healthcare",
        "health care", "medical", "patient", "patients", "disease",
        "condition", "diagnosis", "treatment", "screening", "prognosis",
        "risk prediction", "prediction model", "decision support",
        "drug-drug interaction", "mortality", "outcome", "burden",
        "epidemiology",
    ],
    "T4": [
    # Direct objective/aim words
    "objective", "objectives", "aim", "aims", "aimed", "purpose", "goal", "goals",
    
    # Common study aim phrases
    "this study aimed", "this study aims", "this study investigates",
    "this study evaluates", "this study develops", "this study sought",
    "this study was designed", "the aim of this study", "the purpose of this study",
    "the objective of this study", "our objective", "our aim",
    
    # Author action phrases
    "we aimed", "we aim", "we sought", "we developed", "we develop",
    "we evaluated", "we investigated", "we validated", "we designed",
    "we proposed", "we present", "we introduce",
    
    # Other common formulations
    "to develop", "to evaluate", "to investigate", "to validate",
    "to predict", "to identify", "to assess", "to determine",
    "the goal of", "in this study we",
],
    "T5": [
        "cohort", "retrospective", "prospective", "cross-sectional",
        "case-control", "randomized", "registry", "multicenter",
        "single center", "development cohort", "validation cohort",
        "training cohort", "test cohort", "study population",
        "dataset", "electronic health records", "ehr", "observational study",
    ],
    "T6": [
        "setting", "location", "multicenter", "recruitment site",
        "hospitals", "countries", "international", "national dataset",
        "databank", "wales", "primary care", "general practice",
    ],
    "T7": [
        "inclusion", "exclusion", "eligibility", "enrolled",
        "recruited", "participants", "elective", "adults", "eligible",
    ],
    # T8 is handled by context-aware rules
    "T9": [
        "outcome", "endpoint", "gold standard", "definition of",
        "ascertained", "composite", "pneumonia", "ards",
        "ventilation", "ppc",
    ],
    "T10": [
        "predictor", "variable", "feature engineering",
        "feature extraction", "input feature", "feature",
        "covariate", "input", "candidate", "routinely available",
    ],
    "T11": [
        "blinded", "blinding", "masked", "masking",
        "outcome assessor", "predictor assessor",
        "independent assessor", "independent review",
        "outcome assessment", "blinded to outcome",
        "blinded to outcomes", "blinded to predictor",
        "blinded to predictors", "outcome assessors",
        "predictor assessors", "outcome assessment was blinded",
        "predictor assessment was blinded", "assessors were blinded",
        "masked outcome assessment", "masked predictor assessment",
    ],
    "T12": [
        "imputation", "multiple imputation", "mice", "knn",
        "missforest", "median imputation", "mean imputation",
        "mode imputation", "complete-case", "dropped",
        "missingness", "incomplete", "excluded patients without",
        "missing data",
    ],
    "T13": [
        "logistic regression", "linear regression", "lasso", "ridge",
        "elastic net", "decision tree", "random forest", "extra trees",
        "gradient boosting", "xgboost", "lightgbm", "catboost",
        "svm", "support vector machine", "naive bayes", "knn",
        "k-nearest neighbor", "neural network", "deep learning",
        "cnn", "convolutional neural network", "rnn", "lstm", "gru",
        "transformer", "bert", "autoencoder", "graph neural network",
        "gcn", "attention",
        *ML_ALGORITHMS,
    ],
    "T14": [
        "tuning", "hyperparameter", "grid search",
        "bayesian optimization", "optuna", "hyperopt", "random search",
    ],
    "T15": [
        "feature selection", "variable importance", "rfe",
        "shrinkage", "lasso", "bootstrap resampling",
    ],
    "T16": [
        "internal validation", "five-times cross", "five times cross",
        "5-times cross", "five-fold", "5-fold",
        *VALIDATION_METHODS,
    ],
    "T17": [
        "imbalance", "smote", "undersampling", "oversampling",
        "class weight", "stratified", "class imbalance",
    ],
    "T18": [
        "python", "r software", "r version", "rstudio", "r packages",
        "glmnet", "tidymodels", "tensorflow", "keras", "pytorch",
        "scikit-learn", "sklearn", "xgboost", "lightgbm", "catboost",
        "matlab", "weka", "rapidminer", "orange", "cuda",
        "anaconda", "jupyter", "google colab",
    ],
    "T19": [
        "discrimination", "roc curve", "precision-recall", "pr-auc",
        "average precision", "auc", "roc",
        "receiver operating characteristic", "auroc", "c-index",
        "sensitivity", "specificity",
    ],
    "T20": [
        "calibration", "hosmer", "calibration curve",
        "calibration-in-the-large", "calibration belt", "slope",
        "intercept", "calibration plot", "reliability", "citl",
        "brier score", "expected calibration error",
        "observed/expected", "o/e ratio",
    ],
    "T21": ["95% ci"],
    "T22": [
        "utility", "decision curve", "dca",
        "net benefit", "clinical impact", "treat-all",
    ],
   # Positive indicators that external validation was performed.
   # Kept in sync with EXTERNAL_VALIDATION_KEYWORDS (used for NA detection)
   # so a phrase never counts as "adequate" under one list but not the other.
   "T23": list(EXTERNAL_VALIDATION_KEYWORDS),
    # T24 and T25 are handled by context-aware rules
    "T26": [
        "equation", "formula", "regression equation", "model equation",
        "coefficients", "beta coefficients", "intercept", "risk score",
        "point-score", "nomogram", "online calculator", "web calculator",
        "architecture", "model architecture", "network architecture",
        "neural network architecture", "hyperparameters",
    ],
    "T27": [
        "funding", "grant", "funded by", "financial support",
        "supported by", "sponsor", "conflict of interest",
        "conflicts of interest", "competing interests",
        "disclosure", "declaration of interest",
    ],
}

# Items evaluated by context-aware regex instead of flat keywords
CONTEXT_RULE_ITEMS = {
    "T8": T8_PATTERNS,
    "T24": T24_PATTERNS,
    "T25": T25_PATTERNS,
}

# T23 (external validation) needs its own NA rule, defined further up the
# file once EXTERNAL_VALIDATION_KEYWORDS / _t23_not_applicable exist.
# Registered here, after NA_RULES has been created, to avoid reordering
# the rest of the file.
NA_RULES["T23"] = _t23_not_applicable
