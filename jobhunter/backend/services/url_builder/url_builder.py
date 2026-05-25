from .filters import base, cities as CITY_MAP, categories as CATEGORY_MAP, working_hours as WH_MAP


def build_url(keyword=None, cities=None, categories=None, min_salary=None, working_hours=None):
    parts = [base.rstrip("?") + "?"]

    query_parts = []

    if keyword:
        query_parts.append(f"keyw={keyword}")

    if cities:
        for city in cities:
            city_key = city.lower()
            if city_key in CITY_MAP:
                query_parts.append(CITY_MAP[city_key])

    if categories:
        for cat in categories:
            cat_key = cat.lower()
            if cat_key in CATEGORY_MAP:
                query_parts.append(CATEGORY_MAP[cat_key])

    if working_hours:
        for wh in working_hours:
            wh_key = wh.lower()
            if wh_key in WH_MAP:
                query_parts.append(WH_MAP[wh_key])

    if min_salary is not None:
        query_parts.append(f"&min_salary={min_salary}")
    
    query_parts.append("&save_locale=1&translate_ads=1")

    return parts[0] + "&".join(query_parts)