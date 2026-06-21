from django.core.cache import cache

from datetime import date, timedelta

TOTAL_KEY = "clicks:total:{id}"
DAILY_KEY = "clicks:daily:{id}:{date}"
DAILY_TTL = 90 * 24 * 60 * 60


def track_click(redirect_identifier):
    try:
        today = date.today().isoformat()
        incr(TOTAL_KEY.format(id=redirect_identifier), ttl=None)
        incr(DAILY_KEY.format(id=redirect_identifier, date=today), ttl=DAILY_TTL)
    except Exception:
        pass


def get_stats(redirect_identifier):
    today = date.today()

    total_key = TOTAL_KEY.format(id=redirect_identifier)
    daily_keys = [
        DAILY_KEY.format(
            id=redirect_identifier,
            date=(today - timedelta(days=i)).isoformat(),
        )
        for i in range(7)
    ]

    cached = cache.get_many([total_key] + daily_keys)

    total_clicks = int(cached.get(total_key, 0))
    clicks_last_7_days = [
        {
            "date": (today - timedelta(days=i)).isoformat(),
            "count": int(cached.get(daily_keys[i], 0)),
        }
        for i in range(7)
    ]

    return {
        "redirect_identifier": redirect_identifier,
        "total_clicks": total_clicks,
        "clicks_today": clicks_last_7_days[0]["count"],
        "clicks_last_7_days": clicks_last_7_days,
    }


def incr(key, ttl):
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=ttl)
