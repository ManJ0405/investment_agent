"""Patch twikit User parsing when X API omits optional legacy fields."""
def _normalize_user_data(data: dict) -> dict:
    data = dict(data)
    legacy = dict(data.get("legacy") or {})
    entities = dict(legacy.get("entities") or {})
    description = dict(entities.get("description") or {})
    description.setdefault("urls", [])
    entities["description"] = description
    url_entities = entities.get("url")
    if not isinstance(url_entities, dict):
        url_entities = {}
    url_entities.setdefault("urls", [])
    entities["url"] = url_entities
    legacy["entities"] = entities
    legacy.setdefault("pinned_tweet_ids_str", [])
    legacy.setdefault("withheld_in_countries", [])
    data["legacy"] = legacy
    return data
def apply_twikit_user_patch() -> None:
    import twikit.guest.user as guest_user
    import twikit.user as twikit_user
    for module in (twikit_user, guest_user):
        original_init = module.User.__init__
        def patched_init(self, client, data, _original_init=original_init):
            return _original_init(self, client, _normalize_user_data(data))
        module.User.__init__ = patched_init
