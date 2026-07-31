"""
TripodAi Rule Definitions

Contains:
- TRIPOD+AI keyword rules
- Not Applicable rules
- Shared keyword groups

Version: 2.0
Last updated: 2026-07-23
"""

# NOTE:
# These keyword rules were developed and refined using manually
# assessed TRIPOD+AI reporting from a corpus of published
# AI prediction model studies.

# ------------------------------------------------------------------
# Not Applicable (NA) Rules
# ------------------------------------------------------------------

NA_RULES = {
    "T11": lambda t: any(
        k in t.lower()
        for k in [
            "retrospective",
            "de-identified",
            "historical",
            "ehr-based",
            "secondary data",
            "registry-based",
            "administrative database",
            "routine clinical data",
        ]
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

CODE_REPOSITORIES = ["github", "gitlab", "bitbucket", "zenodo", "figshare", "hugging face",]

ML_ALGORITHMS = ["xgboost", "random forest", "svm", "neural network", "cnn", "rnn", "lstm", "transformer", "logistic regression", "lasso"]
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
# TRIPOD+AI Keyword Rules
# ------------------------------------------------------------------

ADEQUATE_KEYWORDS = {
    "T1": ["prediction", "prognostic", "diagnostic", "risk score", "model development", "predictive model"],
    "T2": ["abstract", "summary", "background", "results", "conclusions", "auroc", "brier"],
    
    "T3": ["clinical", "clinical context", "public health", "healthcare",
    "health care",
    "medical",
    "patient",
    "patients",
    "disease",
    "condition",
    "diagnosis",
    "treatment",
    "screening",
    "prognosis",
    "risk prediction",
    "prediction model",
    "decision support",
    "drug-drug interaction",
    "mortality",
    "outcome",
    "burden",
    "epidemiology",
],
    
    "T4": [
    "objective",
    "objectives",
    "aim",
    "aimed",
    "purpose",
    "this study aimed",
    "this study investigates",
    "this study evaluates",
    "this study develops",
    "we developed",
    "we develop",
    "we sought",
    "we evaluated",
    "we investigated",
    "we validated",
    "we designed",
],
    "T5": [
    "cohort",
    "retrospective",
    "prospective",
    "cross-sectional",
    "case-control",
    "randomized",
    "registry",
    "multicenter",
    "single center",
    "development cohort",
    "validation cohort",
    "training cohort",
    "test cohort",
    "study population",
    "dataset",
    "electronic health records",
    "ehr",
    "observational study",
],
    "T6": ["setting", "location", "multicenter", "recruitment site", "hospitals", "countries", "international", "national dataset", "databank", "wales", "primary care", "general practice"],
    
    
    "T7": ["inclusion", "exclusion", "eligibility", "enrolled", "recruited", "participants", "elective", "adults", "eligible",],
    
    "T8": ["sample size", "power calculation", "sample size calculation", "events per variable", "epv", "justification", "minimum patients", "n=", "derivation n=", "sample size requirement", "minimum sample size", "adequacy of our sample size"],
    
    
    "T9": ["outcome", "endpoint", "gold standard", "definition of", "ascertained", "composite", "pneumonia", "ards", "ventilation", "ppc"],
    
    "T10": ["predictor", "variable", "feature engineering", "feature extraction", "input feature", "feature", "covariate", "input", "candidate", "routinely available"],
    "T11": [
    "blinded",
    "blinding",
    "masked",
    "masking",
    "outcome assessor",
    "predictor assessor",
    "independent assessor",
    "independent review",
    "outcome assessment",
"blinded to outcome", "blinded to outcomes", "blinded to predictor", "blinded to predictors", "outcome assessor", "outcome assessors", "predictor assessor", "predictor assessors", "outcome assessment was blinded", "predictor assessment was blinded", "assessors were blinded", "masked outcome assessment", "masked predictor assessment",],
    "T12": ["imputation", "multiple imputation", "mice", "knn", "missforest", "median imputation", "mean imputation", "mode imputation", "complete-case", "dropped", "missingness", "incomplete", "excluded patients without", "missing data"],
    "T13": [
    "logistic regression",
    "linear regression",
    "lasso",
    "ridge",
    "elastic net",
    "decision tree",
    "random forest",
    "extra trees",
    "gradient boosting",
    "xgboost",
    "lightgbm",
    "catboost",
    "svm",
    "support vector machine",
    "naive bayes",
    "knn",
    "k-nearest neighbor",
    "neural network",
    "deep learning",
    "cnn",
    "convolutional neural network",
    "rnn",
    "lstm",
    "gru",
    "transformer",
    "bert",
    "autoencoder",
    "graph neural network",
    "gcn",
    "attention",
*ML_ALGORITHMS,],
    "T14": ["tuning", "hyperparameter", "grid search", "bayesian optimization", "optuna", "hyperopt", "random search",],
    "T15": ["feature selection", "variable importance", "rfe", "shrinkage", "lasso", "bootstrap resampling"],
    "T16": ["internal validation", "five-times cross", "five times cross", "5-times cross", "five-fold", "5-fold", *VALIDATION_METHODS,],
    "T17": ["imbalance", "smote", "undersampling", "oversampling", "class weight", "stratified", "class imbalance"],
    "T18": [
    "python",
    "r software",
    "r version",
    "rstudio",
    "r packages",
    "glmnet",
    "tidymodels",
    "tensorflow",
    "keras",
    "pytorch",
    "scikit-learn",
    "sklearn",
    "xgboost",
    "lightgbm",
    "catboost",
    "matlab",
    "weka",
    "rapidminer",
    "orange",
    "cuda",
    "anaconda",
    "jupyter",
    "google colab",
],
    "T19": ["discrimination", "roc curve", "precision-recall", "pr-auc", "average precision", "auc", "roc", "receiver operating characteristic", "auroc", "c-index", "sensitivity", "specificity",],
    "T20": ["calibration", "hosmer", "calibration curve", "calibration-in-the-large", "calibration belt", "slope", "intercept", "calibration plot", "reliability", "citl", "brier score", "expected calibration error", "observed/expected", "o/e ratio"],
    "T21": ["95% ci"],
    "T22": ["utility", "decision curve", "dca",  "net benefit", "clinical impact", "treat-all"],
    "T23": ["external validation", "externally validated", "independent cohort", "independent dataset", "external dataset", "external test set", "temporal validation", "geographical validation", "validated on an independent dataset", "regional groups", "testing cohort", "external cohorts"],
    "T24": [ *CODE_REPOSITORIES, "source code", "python package", "r package", "git repository", "source repository", "source available", "code available", "code availability", "software availability", "public repository", "research code", "our research code"],
    "T25": ["data sharing", "anonymised data", "available on request", "data used in this study are available", "data are available", "data availability", "available in the sail", "available via"],
    "T26":  ["equation", "formula", "regression equation", "model equation", "coefficients", "beta coefficients", "intercept", "risk score", "point-score", "nomogram", "online calculator", "web calculator","architecture", "model architecture", "network architecture", "neural network architecture", "hyperparameters",],
    "T27": ["funding", "grant", "funded by", "financial support", "supported by", "sponsor", "conflict of interest", "conflicts of interest", "competing interests", "disclosure", "declaration of interest",]
}
