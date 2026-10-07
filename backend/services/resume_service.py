import spacy
from pypdf import PdfReader
from spacy_layout import spaCyLayout
from pathlib import Path
from rake_spacy import Rake
from esco_service import (
	get_esco_skill_label_index_cached,
	phrase_matches_esco_skill,
	search_esco_skill_exists_cached,
)

nlp = spacy.load("en_core_web_sm")
rake_model = Rake(nlp=nlp)
layout = spaCyLayout(nlp)
backend_dir = Path(__file__).resolve().parents[1]
esco_label_index = get_esco_skill_label_index_cached()

def extract_section(text: str, heading: str, next_headings: list[str]) -> str:
	"""Return section text from heading up to the next heading, if present."""
	upper = text.upper()
	heading_upper = heading.upper()
	start = upper.find(heading_upper)
	if start == -1:
		return ""

	section_start = start + len(heading)
	section_end = len(text)
	upper_from_start = upper[section_start:]
	for next_heading in next_headings:
		idx = upper_from_start.find(next_heading.upper())
		if idx != -1:
			section_end = min(section_end, section_start + idx)

	return text[section_start:section_end].strip()

# Resolve the uploads path relative to backend/, not the current working directory.
resume_path = backend_dir / "uploads" / "buckley_Robert_Buckley_Resume_06-29-2026.pdf"
resume = layout(str(resume_path))

keywords = rake_model.apply_to_doc(resume)
print("\nKEYWORDS:")
print([(score, phrase.text) for score, phrase in keywords])

# Fallback for table-heavy resume sections that may be collapsed in layout output.
reader = PdfReader(str(resume_path))
raw_text = "\n".join(page.extract_text() or "" for page in reader.pages)
education_text = extract_section(raw_text, "EDUCATION", ["CERTIFICATIONS", "PROJECTS", "EXPERIENCE"])

for score, phrase in keywords:
	phrase_text = phrase.text.lower()
	matched = phrase_matches_esco_skill(phrase_text, esco_label_index)
	if not matched:
		matched = search_esco_skill_exists_cached(phrase_text)

	if matched:
		print(f"Matched ESCO skill: {phrase.text}")

	if not matched:
		print(f"No match for: {phrase.text}")