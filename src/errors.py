"""Shared error handling for all tools."""

from __future__ import annotations

ERRORS = {
    "connection": "خطأ: تعذر الاتصال بالخدمة. حاول لاحقاً.",
    "timeout": "خطأ: انتهت مهلة الاتصال. حاول لاحقاً.",
    "parse": "خطأ: الخدمة أرجعت رداً غير صالح. حاول لاحقاً.",
    "not_found": "خطأ: لم يتم العثور على النتيجة المطلوبة.",
    "auth": "خطأ: مفتاح الواجهة البرمجية غير صالح أو مفقود.",
    "rate_limit": "خطأ: تم تجاوز الحد المسموح من الطلبات. حاول لاحقاً.",
    "unavailable": "خطأ: الخدمة غير متاحة حالياً. حاول لاحقاً.",
    "invalid_input": "خطأ: مدخلات غير صالحة.",
}


def api_error(kind: str = "connection") -> str:
    """Return a standardized Arabic error message."""
    return ERRORS.get(kind, ERRORS["connection"])


def safe_json(resp) -> dict | None:
    """Safely parse JSON from an HTTP response. Returns None on failure."""
    if resp.status_code >= 400:
        return None
    try:
        return resp.json()
    except Exception:
        return None
