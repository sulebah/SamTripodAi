from TripodAI import TripodAIExtractor

extractor = TripodAIExtractor()

# Paste the full paper text between the triple quotes
paper_text = """






"""

report = extractor.analyze(paper_text, paper_title="")

# ============================================================
# 1. Overall Summary
# ============================================================
print("=" * 70)
print(f"Paper               : {report.paper_title}")
print(f"Overall Compliance  : {report.overall_compliance}%")
print(f"High Quality (≥75%) : {report.high_quality}")
print(f"Total Applicable    : {report.total_applicable}")
print("=" * 70)

# ============================================================
# 2. Domain Scores
# ============================================================
# ============================================================
# 2. Domain Scores
# ============================================================
print("\nDOMAIN SCORES")
print("-" * 70)

for domain, ds in report.domain_scores.items():
    print(f"{domain}: {ds}")# ============================================================
# 3. Full Item-Level Results
# ============================================================
print("\nITEM-LEVEL RESULTS")
print("-" * 70)
print(f"{'Item':<6} {'Score':<8} {'Status':<18} Description")
print("-" * 70)

for tid in sorted(report.items.keys(), key=lambda x: int(x[1:])):
    item = report.items[tid]
    
    if not item.applicable:
        status = "Not Applicable"
    else:
        status = "Adequate" if item.score == 1.0 else "Inadequate"
    
    print(f"{tid:<6} {item.score:<8} {status:<18} {item.description}")

print("-" * 70)
