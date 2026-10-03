QUALITY_PROFILES = ("strong", "incomplete", "conflicting", "anonymous_only", "single_source", "multi_source")


def profile_for(index: int, configured: tuple[str, ...] = QUALITY_PROFILES) -> str:
    available = configured or QUALITY_PROFILES
    return available[index % len(available)]
