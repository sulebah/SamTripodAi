from TripodAi import TripodAIExtractor

extractor = TripodAIExtractor()
report = extractor.analyze(paper_text, paper_title="My Paper")
print(report.to_markdown())
