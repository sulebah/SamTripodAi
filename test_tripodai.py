from TripodAI import TripodAIExtractor

extractor = TripodAIExtractor()

paper_text = """




"""

report = extractor.analyze(paper_text, paper_title=" ")
print(report.to_markdown())
