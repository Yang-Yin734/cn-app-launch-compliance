# cn-app-launch-compliance

> 中文说明：[README.zh-CN.md](README.zh-CN.md)

A reusable agent **skill** that decomposes "getting a mobile app (Android / iOS / mini-program, including AI features) compliant and live on the China mainland" into independently executable, partly automatable stages — and strictly respects one iron rule: **the agent never performs real-name verification, contract signing, face checks, or government/platform form submissions on your behalf.** It only drafts materials, scans code behavior, lists ordered to-dos, and runs a read-only health-check script, while making crystal clear what a human must do.

## What it does

- Walks through **9 stages**: entity consistency → domain & filing → servers & network → privacy compliance → payment integration → app-store submission → SMS → generative-AI filing → pre-launch health check.
- Enforces the **highest-priority principle of entity consistency**: the entity behind the domain real-name, ICP filing, public-security filing, merchant account, mini-program, SMS qualification, and software copyright / store developer must all be the same (typically the business license entity).
- Clearly labels **what the agent can automate** vs **what the human must do** (real-name, signing, face checks, form submission).
- Surfaces **high-frequency rejection reasons** with fixes and official source links.
- Runs a **read-only compliance health-check script** against a public URL.

## When to use

- "Launch in China" / "submit to app stores" / "integrate WeChat Pay / Alipay" / "do the filing" / "compliant release"
- Preparing to publish an app with AI features in China (algorithm / large-model filing)
- Needing a China launch checklist, rejection debugging, or a pre-launch health check

## Repository layout

```
cn-app-launch-compliance/
├── SKILL.md                      # Skill definition: triggers + workflow + hard rules
├── references/
│   ├── checklist.md             # Stage-by-stage checklist + official sources + dependency order
│   └── rejection-reasons.md     # Common rejection reasons (filing/payment/store/SMS) + fixes
├── scripts/
│   └── compliance-check.py      # Read-only pre-launch health check
└── README.md
```

## Install

Copy the skill folder into your agent's skills directory:

```bash
# project-scoped
cp -r cn-app-launch-compliance <project>/.workbuddy/skills/

# user-global
cp -r cn-app-launch-compliance ~/.workbuddy/skills/
```

The agent triggers it when you ask about China-mainland launch / compliance.

## Usage

1. **Entity first.** Confirm a single unified entity before any step; inconsistent entities cause cascading failures at filing / signing / review.
2. **Work the stages in order** (see `references/checklist.md`). The agent drafts, scans, and lists; you do real-name / signing / submission.
3. **Run the read-only health check** on your live URL:

   ```bash
   python scripts/compliance-check.py https://your-site.example.com --timeout 10
   ```

   It checks, without modifying anything:
   - HTTPS enabled
   - ICP filing number present (e.g. `京ICP备XXXXXXXX号`)
   - Public-security filing number present (e.g. `京公网安备XXXXXXXX号`)
   - Privacy policy link present
   - Overseas dependencies detected (Google Fonts / Analytics / gstatic / firebase / cloudflare)
   - AI-generated-content marker (only relevant if the app uses generative AI)

   Output is a JSON report. Exit code `1` if any required check FAILs.
4. **Fix FAILs** by returning to the relevant stage, then re-run until clean.

## Agent / human split (always followed)

| Type | Agent can | Human must |
|---|---|---|
| Draft | privacy policy / agreement drafts, filing forms, store copy, SMS templates | — |
| Code | remove overseas deps, callback signature verification, footer filing numbers, AI markers | — |
| Scan | permission / SDK collection behavior, health-check script | — |
| Qualification | — | real-name, signing, corporate account, face check |
| Submit | — | government / platform forms, review responses |

## Important notes

- This skill **does not fabricate fees or timelines**; it cites only what official pages state and flags anything uncertain with "⚠️ verify against the latest official notice".
- It **never substitutes for real-name or signing**, and the health-check script is strictly read-only.
- Official sources (MIIT, Ministry of Public Security, CAC, WeChat / Alipay open platforms) take precedence; record the verification date.

## License

MIT — see [LICENSE](LICENSE).
