import time
from collections.abc import Iterable
import requests

ESCO_SKILLS_SCHEME = "http://data.europa.eu/esco/concept-scheme/skills"
# In-memory cache: survives for process lifetime and resets on app restart.
ESCO_SKILLS_CACHE_TTL_SECONDS = 86400
ESCO_API_MAX_PAGE_SIZE = 100
ESCO_SEARCH_URL = "https://ec.europa.eu/esco/api/search"
_ESCO_SKILLS_CACHE: dict[tuple[str, str, int | None, bool], dict] = {}
_ESCO_SKILLS_LABEL_INDEX_CACHE: dict[tuple[str, str, int | None, bool], dict] = {}
_ESCO_SKILL_SEARCH_CACHE: dict[tuple[str, str, str], dict] = {}

SUPPLEMENTAL_TECH_SKILLS: list[dict[str, object]] = [
	{
		"preferredLabel": {"en": "FastAPI"},
		"alternativeLabel": {"en": ["fastapi", "fast api"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "Flask"},
		"alternativeLabel": {"en": ["python flask"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "Django"},
		"alternativeLabel": {"en": ["django framework"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "Docker"},
		"alternativeLabel": {"en": ["docker containers", "containerization"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "Kubernetes"},
		"alternativeLabel": {"en": ["k8s"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "Terraform"},
		"alternativeLabel": {"en": ["iac", "infrastructure as code"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "GitHub Actions"},
		"alternativeLabel": {"en": ["github action workflows", "gh actions"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "GitLab CI/CD"},
		"alternativeLabel": {"en": ["gitlab ci", "gitlab pipeline"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "CircleCI"},
		"alternativeLabel": {"en": ["circle ci"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "Jenkins"},
		"alternativeLabel": {"en": ["jenkins pipeline"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "AWS"},
		"alternativeLabel": {"en": ["amazon web services"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "Microsoft Azure"},
		"alternativeLabel": {"en": ["azure cloud"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "Google Cloud Platform"},
		"alternativeLabel": {"en": ["gcp", "google cloud"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "GraphQL"},
		"alternativeLabel": {"en": ["graphql api"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "Microservices"},
		"alternativeLabel": {"en": ["microservice architecture"]},
		"source": "supplemental",
	},
	{
		"preferredLabel": {"en": "Jira"},
		"alternativeLabel": {"en": ["atlassian jira"]},
		"source": "supplemental",
	},
]


def _normalize_label(value: str) -> str:
	return value.strip().lower()


def _extract_skill_labels(skill: dict, language: str) -> Iterable[str]:
	preferred_raw = skill.get("preferredLabel") or skill.get("preferredLabels") or {}
	if isinstance(preferred_raw, dict):
		preferred_value = preferred_raw.get(language, "")
		if isinstance(preferred_value, str) and preferred_value.strip():
			yield _normalize_label(preferred_value)
	elif isinstance(preferred_raw, str) and preferred_raw.strip():
		yield _normalize_label(preferred_raw)

	alternatives_raw = skill.get("alternativeLabel") or skill.get("altLabels") or {}
	if isinstance(alternatives_raw, dict):
		alternatives_value = alternatives_raw.get(language, [])
		if isinstance(alternatives_value, str) and alternatives_value.strip():
			yield _normalize_label(alternatives_value)
		elif isinstance(alternatives_value, list):
			for alt in alternatives_value:
				if isinstance(alt, str) and alt.strip():
					yield _normalize_label(alt)
	elif isinstance(alternatives_raw, list):
		for alt in alternatives_raw:
			if isinstance(alt, str) and alt.strip():
				yield _normalize_label(alt)


def _merge_esco_with_supplemental(
	esco_skills: list[dict],
	supplemental_skills: list[dict],
	language: str,
) -> list[dict]:
	"""Merge ESCO and supplemental skills, deduplicating by preferred label."""
	merged: list[dict] = []
	seen_preferred: set[str] = set()

	for skill in esco_skills + supplemental_skills:
		preferred_raw = skill.get("preferredLabel") or skill.get("preferredLabels") or {}
		preferred_value = ""
		if isinstance(preferred_raw, dict):
			candidate = preferred_raw.get(language, "")
			if isinstance(candidate, str):
				preferred_value = candidate
		elif isinstance(preferred_raw, str):
			preferred_value = preferred_raw

		normalized_preferred = _normalize_label(preferred_value) if preferred_value else ""
		if normalized_preferred and normalized_preferred in seen_preferred:
			continue

		if normalized_preferred:
			seen_preferred.add(normalized_preferred)
		merged.append(skill)

	return merged


def _build_skill_label_index(skills: list[dict], language: str) -> dict[str, object]:
	"""Build a fast lookup structure for ESCO skill matching."""
	exact_labels: set[str] = set()
	all_labels: list[str] = []

	for skill in skills:
		for label in _extract_skill_labels(skill, language):
			exact_labels.add(label)
			all_labels.append(label)

	return {
		"exact_labels": exact_labels,
		"all_labels": all_labels,
	}


def _extract_esco_results(payload: dict) -> list[dict]:
	"""Handle different ESCO/HAL payload shapes and return concept rows."""
	embedded = payload.get("_embedded", {})

	# ESCO commonly returns references in top-level 'concepts' and full rows in
	# '_embedded' keyed by concept URI.
	concept_refs = payload.get("concepts")
	if isinstance(concept_refs, list):
		rows: list[dict] = []
		for ref in concept_refs:
			if not isinstance(ref, dict):
				continue
			uri = ref.get("uri")
			embedded_row = embedded.get(uri) if isinstance(uri, str) else None
			if isinstance(embedded_row, dict):
				rows.append({**ref, **embedded_row})
			else:
				rows.append(ref)
		if rows:
			return rows

	for key in ("results", "concepts", "items"):
		value = embedded.get(key)
		if isinstance(value, list):
			return value

	if isinstance(embedded, dict):
		mapped_rows = [v for v in embedded.values() if isinstance(v, dict)]
		if mapped_rows:
			return mapped_rows

	if isinstance(payload.get("concepts"), list):
		return payload["concepts"]

	if isinstance(payload.get("results"), list):
		return payload["results"]
	return []


def get_esco_concepts_by_scheme(
	concept_scheme: str,
	language: str = "en",
	limit: int = 20,
	offset: int = 0,
	selected_version: str = "latest",
):
	"""Query ESCO directly via REST without a generated swagger client."""
	url = "https://ec.europa.eu/esco/api/resource/concept"
	params = {
		"isInScheme": concept_scheme,
		"language": language,
		"limit": limit,
		"offset": offset,
		"selectedVersion": selected_version,
		"viewObsolete": "false",
	}
	response = requests.get(url, params=params, timeout=30)
	response.raise_for_status()
	return response.json()


def get_all_esco_skills(
	language: str = "en",
	selected_version: str = "latest",
	page_size: int = ESCO_API_MAX_PAGE_SIZE,
	max_records: int | None = None,
) -> list[dict]:
	"""Fetch all ESCO skills by paging through the skills concept scheme."""
	skills: list[dict] = []
	offset = 0
	page_size = min(page_size, ESCO_API_MAX_PAGE_SIZE)

	while True:
		payload = get_esco_concepts_by_scheme(
			concept_scheme=ESCO_SKILLS_SCHEME,
			language=language,
			limit=page_size,
			offset=offset,
			selected_version=selected_version,
		)
		page = _extract_esco_results(payload)
		if not page:
			break

		count = payload.get("count")
		total = payload.get("total")

		skills.extend(page)
		if max_records and len(skills) >= max_records:
			return skills[:max_records]

		if isinstance(count, int) and isinstance(total, int):
			if offset + count >= total:
				break

		if len(page) < page_size:
			break

		offset += count if isinstance(count, int) and count > 0 else page_size

	return skills


def get_all_esco_skills_cached(
	language: str = "en",
	selected_version: str = "latest",
	max_records: int | None = None,
	ttl_seconds: int = ESCO_SKILLS_CACHE_TTL_SECONDS,
	force_refresh: bool = False,
	include_supplemental: bool = True,
) -> list[dict]:
	"""Return cached ESCO skills, refreshing only when cache is stale or forced."""
	cache_key = (language, selected_version, max_records, include_supplemental)
	now = time.time()
	cached = _ESCO_SKILLS_CACHE.get(cache_key)

	if not force_refresh and cached and now < cached["expires_at"]:
		return cached["data"]

	data = get_all_esco_skills(
		language=language,
		selected_version=selected_version,
		max_records=max_records,
	)
	if include_supplemental:
		data = _merge_esco_with_supplemental(data, SUPPLEMENTAL_TECH_SKILLS, language)
	if max_records and len(data) > max_records:
		data = data[:max_records]
	_ESCO_SKILLS_CACHE[cache_key] = {
		"data": data,
		"expires_at": now + ttl_seconds,
	}
	return data


def get_esco_skill_label_index_cached(
	language: str = "en",
	selected_version: str = "latest",
	max_records: int | None = None,
	ttl_seconds: int = ESCO_SKILLS_CACHE_TTL_SECONDS,
	force_refresh: bool = False,
	include_supplemental: bool = True,
) -> dict[str, object]:
	"""Return cached ESCO label index for fast phrase-to-skill matching."""
	cache_key = (language, selected_version, max_records, include_supplemental)
	now = time.time()
	cached = _ESCO_SKILLS_LABEL_INDEX_CACHE.get(cache_key)

	if not force_refresh and cached and now < cached["expires_at"]:
		return cached["data"]

	skills = get_all_esco_skills_cached(
		language=language,
		selected_version=selected_version,
		max_records=max_records,
		ttl_seconds=ttl_seconds,
		force_refresh=force_refresh,
		include_supplemental=include_supplemental,
	)
	index = _build_skill_label_index(skills, language)
	_ESCO_SKILLS_LABEL_INDEX_CACHE[cache_key] = {
		"data": index,
		"expires_at": now + ttl_seconds,
	}
	return index


def phrase_matches_esco_skill(phrase_text: str, label_index: dict[str, object]) -> bool:
	"""Check if a phrase matches any ESCO label using exact or substring match."""
	normalized = _normalize_label(phrase_text)
	if not normalized:
		return False

	exact_labels = label_index.get("exact_labels", set())
	if isinstance(exact_labels, set) and normalized in exact_labels:
		return True

	all_labels = label_index.get("all_labels", [])
	if isinstance(all_labels, list):
		return any(normalized in label for label in all_labels)

	return False


def search_esco_skill_exists_cached(
	phrase_text: str,
	language: str = "en",
	selected_version: str = "latest",
	ttl_seconds: int = ESCO_SKILLS_CACHE_TTL_SECONDS,
	force_refresh: bool = False,
) -> bool:
	"""Search ESCO by phrase and cache whether a matching skill exists."""
	normalized = _normalize_label(phrase_text)
	if not normalized:
		return False

	cache_key = (normalized, language, selected_version)
	now = time.time()
	cached = _ESCO_SKILL_SEARCH_CACHE.get(cache_key)
	if not force_refresh and cached and now < cached["expires_at"]:
		return bool(cached["data"])

	params = {
		"text": normalized,
		"language": language,
		"type": "skill",
		"limit": 1,
		"offset": 0,
		"selectedVersion": selected_version,
	}
	response = requests.get(ESCO_SEARCH_URL, params=params, timeout=30)
	response.raise_for_status()
	payload = response.json()
	exists = isinstance(payload.get("total"), int) and payload["total"] > 0

	_ESCO_SKILL_SEARCH_CACHE[cache_key] = {
		"data": exists,
		"expires_at": now + ttl_seconds,
	}
	return exists

print("Loaded ESCO skills service.")