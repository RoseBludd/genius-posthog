"""Public Analyticzs landing page for unauthenticated visitors at /."""
from __future__ import annotations

from pathlib import Path

from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

LANDING_ROOT = Path("/opt/genius/landing")


def _safe_asset_path(asset: str) -> Path:
    path = (LANDING_ROOT / asset).resolve()
    if LANDING_ROOT.resolve() not in path.parents and path != LANDING_ROOT.resolve():
        raise Http404()
    if not path.is_file():
        raise Http404()
    return path


def genius_landing_static(request, asset: str) -> HttpResponse:
    del request
    path = _safe_asset_path(asset)
    content_type = "text/css" if path.suffix == ".css" else "text/html"
    return HttpResponse(path.read_text(encoding="utf-8"), content_type=content_type)


@csrf_exempt
def genius_landing_page(request) -> HttpResponse:
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        from posthog.utils import render_template

        return render_template("index.html", request)
    return genius_landing_static(request, "index.html")
