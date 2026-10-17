#!/usr/bin/env python3
"""Read-only compliance health check for China-mainland app launch.

Given a public URL, checks the most common launch blockers without
modifying anything:
  - HTTPS enabled
  - ICP filing number present (e.g. 京ICP备XXXXXXXX号)
  - Public security filing number present (e.g. 京公网安备XXXXXXXX号)
  - Privacy policy link present
  - Overseas dependencies detected (Google Fonts/Analytics, gstatic, etc.)
  - AI-generated content marker present (when app uses generative AI)

Usage:
    python compliance-check.py https://example.com [--timeout 10]

Exit code 0 = all checks pass, 1 = at least one FAIL.
This script only reads public pages; it never writes to the target.
"""
import argparse
import json
import re
import sys
import urllib.request
import urllib.error

ICP_RE = re.compile(r"[\u4e00-\u9fa5]{2,}ICP[备备]?\d{6,12}号")
GONGAN_RE = re.compile(r"[\u4e00-\u9fa5]{2,}公网安备\d{12,18}号")
PRIVACY_RE = re.compile(r"隐私政策|隐私协议|privacy", re.IGNORECASE)
OVERSEAS_PATTERNS = [
    "fonts.googleapis.com", "fonts.gstatic.com", "googleapis.com",
    "google-analytics.com", "googletagmanager.com", "firebase",
    "cloudflare",  # flag for manual review (may be acceptable)
]
AI_MARKER_RE = re.compile(r"AI\s*生成|由\s*AI|人工智能生成", re.IGNORECASE)


def fetch(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace"), resp.geturl()


def main():
    ap = argparse.ArgumentParser(description="China app-launch compliance health check.")
    ap.add_argument("url")
    ap.add_argument("--timeout", type=int, default=10)
    args = ap.parse_args()

    result = {"url": args.url, "checks": {}}
    try:
        html, final_url = fetch(args.url, args.timeout)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError) as e:
        result["error"] = f"fetch failed: {e}"
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(1)

    https = final_url.lower().startswith("https://")
    icp = bool(ICP_RE.search(html))
    gongan = bool(GONGAN_RE.search(html))
    privacy = bool(PRIVACY_RE.search(html))
    overseas = [p for p in OVERSEAS_PATTERNS if p in html]
    ai_marker = bool(AI_MARKER_RE.search(html))

    def verdict(ok):
        return "PASS" if ok else "FAIL"

    result["checks"] = {
        "https_enabled": {"value": https, "verdict": verdict(https)},
        "icp_filing_number": {"value": icp, "verdict": verdict(icp)},
        "public_security_filing": {"value": gongan, "verdict": verdict(gongan)},
        "privacy_policy_link": {"value": privacy, "verdict": verdict(privacy)},
        "overseas_dependencies": {
            "value": overseas,
            "verdict": "WARN" if overseas else "PASS",
            "note": "cloudflare may be acceptable; review manually" if "cloudflare" in overseas and len(overseas) == 1 else "",
        },
        "ai_content_marker": {
            "value": ai_marker,
            "verdict": "INFO",
            "note": "Only relevant if the app provides generative AI; mark AI-generated content.",
        },
    }
    failed = any(c["verdict"] == "FAIL" for c in result["checks"].values())
    result["summary"] = "FAIL" if failed else "PASS"
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
