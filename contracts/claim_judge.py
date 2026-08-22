# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json
from datetime import datetime, timezone

class ClaimJudge(gl.Contract):
    """
    ClaimJudge v3 – Enterprise AI-Powered Decentralized Claim & Dispute Resolver
    Maximum consensus reliability • Full evidence acquisition • Meaningful re-adjudication
    """

    # Storage
    claim_counter: u256
    resolved_count: u256
    claims: TreeMap[u256, str]
    resolutions: TreeMap[u256, str]
    challenges: TreeMap[u256, str]
    decision_history: TreeMap[u256, str]
    normalized_evidence: TreeMap[u256, str]

    def __init__(self):
        self.claim_counter = u256(0)
        self.resolved_count = u256(0)
        self.claims = TreeMap[u256, str]()
        self.resolutions = TreeMap[u256, str]()
        self.challenges = TreeMap[u256, str]()
        self.decision_history = TreeMap[u256, str]()
        self.normalized_evidence = TreeMap[u256, str]()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe_loads(self, data: str, default):
        try:
            return json.loads(data) if data else default
        except Exception:
            return default

    def _normalize(self, text: str, max_len: int = 2600) -> str:
        if not text:
            return ""
        # Extremely aggressive normalization for perfect consensus
        t = str(text)
        t = t.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        t = " ".join(t.split())
        return t[:max_len].strip()

    # ================================================================
    # WRITE METHODS
    # ================================================================

    @gl.public.write
    def create_claim(self, title: str, description: str, evidence_urls: str) -> u256:
        title = title.strip()
        description = description.strip()
        evidence_urls = evidence_urls.strip()

        assert 3 <= len(title) <= 150, "Title length invalid"
        assert 12 <= len(description) <= 1500, "Description length invalid"
        assert len(evidence_urls) <= 700, "Evidence URLs too long"

        claim_id = self.claim_counter
        self.claim_counter += u256(1)

        claim = {
            "id": int(claim_id),
            "title": title,
            "description": description,
            "evidence_urls": evidence_urls,
            "creator": str(gl.message.sender_address),
            "status": "open",
            "created_at": self._now(),
            "updated_at": self._now(),
            "evidence_version": 1,
            "contract_version": "3.0"
        }
        self.claims[claim_id] = json.dumps(claim, sort_keys=True)
        self.decision_history[claim_id] = "[]"
        return claim_id

    @gl.public.write
    def add_evidence(self, claim_id: u256, extra_urls: str) -> str:
        claim_str = self.claims.get(claim_id, "")
        if not claim_str:
            return json.dumps({"error": "Claim not found"})

        claim = self._safe_loads(claim_str, {})
        if claim.get("status") not in ("open", "challenged"):
            return json.dumps({"error": "Cannot add evidence in current status"})

        extra = extra_urls.strip()
        if not extra or len(extra) < 5 or len(extra) > 400:
            return json.dumps({"error": "Invalid extra evidence"})

        existing = claim.get("evidence_urls", "")
        combined = f"{existing},{extra}" if existing else extra
        if len(combined) > 850:
            return json.dumps({"error": "Total evidence URLs exceed limit"})

        claim["evidence_urls"] = combined
        claim["updated_at"] = self._now()
        claim["evidence_version"] = int(claim.get("evidence_version", 1)) + 1
        self.claims[claim_id] = json.dumps(claim, sort_keys=True)

        # Invalidate normalized evidence
        self.normalized_evidence[claim_id] = ""

        return json.dumps({"success": True, "claim_id": int(claim_id)})

    @gl.public.write
    def resolve_claim(self, claim_id: u256) -> str:
        claim_str = self.claims.get(claim_id, "")
        if not claim_str:
            return json.dumps({"error": "Claim does not exist"})

        claim = self._safe_loads(claim_str, {})
        status = claim.get("status", "")

        if status not in ("open", "challenged"):
            if claim_id in self.resolutions:
                return self.resolutions[claim_id]
            return json.dumps({"error": "Claim already finalized"})

        # Context
        is_reassessment = False
        challenge_reason = ""
        previous_decision = ""

        if claim_id in self.challenges:
            ch = self._safe_loads(self.challenges[claim_id], {})
            challenge_reason = ch.get("reason", "")
            previous_decision = ch.get("previous_decision", "")
            is_reassessment = True

        title = claim.get("title", "")
        description = claim.get("description", "")
        raw_urls = claim.get("evidence_urls", "")

        # ---------- 1. Contract acquires & normalizes evidence ----------
        def acquire_evidence() -> str:
            if not raw_urls or not raw_urls.strip():
                return "NO_EVIDENCE_PROVIDED"

            urls = [u.strip() for u in raw_urls.split(",") if u.strip()][:3]  # hard safety limit
            parts = []

            for url in urls:
                try:
                    raw_content = gl.nondet.web.render(url, mode="text")
                    content = str(raw_content) if raw_content is not None else ""
                    if len(content.strip()) > 40:
                        parts.append(f"SRC:{url}::{self._normalize(content, 800)}")
                    else:
                        parts.append(f"SRC:{url}::[EMPTY]")
                except Exception:
                    parts.append(f"SRC:{url}::[FAILED]")

            if not parts:
                return "ALL_EVIDENCE_FAILED"

            return self._normalize(" ||| ".join(parts), 2800)

        normalized = gl.eq_principle.strict_eq(acquire_evidence)
        self.normalized_evidence[claim_id] = normalized

        # ---------- 2. AI Adjudication ----------
        def build_prompt() -> str:
            p = f"""TITLE: {title}
DESCRIPTION: {description}

NORMALIZED_EVIDENCE:
{normalized}
"""
            if is_reassessment:
                p += f"""
RE_ADJUDICATION
Previous decision: {previous_decision}
Challenge reason: {challenge_reason}
"""
            return p

        raw_output = gl.eq_principle.prompt_non_comparative(
            build_prompt,
            task=(
                "You are a professional, impartial claims adjudicator. "
                "Judge ONLY from the title, description and normalized evidence. "
                "Respond with exactly one of these words: VALID, PARTIALLY_VALID, INVALID."
            ),
            criteria="Output must be exactly one word: VALID or PARTIALLY_VALID or INVALID. No other characters."
        )

        decision = str(raw_output).strip().upper()
        decision = "".join(c for c in decision if c.isalpha() or c == "_")
        if decision not in ("VALID", "PARTIALLY_VALID", "INVALID"):
            decision = "INVALID"

        now = self._now()
        confidence = 93 if decision == "VALID" else (70 if decision == "PARTIALLY_VALID" else 18)

        resolution = {
            "claim_id": int(claim_id),
            "decision": decision,
            "confidence": confidence,
            "reasoning": f"Consensus decision {decision} based on contract-normalized evidence v{claim.get('evidence_version', 1)}"
                         + (f" | Re-adjudication triggered by: {challenge_reason[:100]}" if is_reassessment else ""),
            "summary": f"Claim judged {decision}",
            "resolved_at": now,
            "resolved_by": "GenLayer AI Consensus",
            "is_reassessment": is_reassessment,
            "previous_decision": previous_decision,
            "challenge_reason": challenge_reason,
            "evidence_normalized": True,
            "evidence_version": claim.get("evidence_version", 1),
            "adjudication_method": "strict_eq + prompt_non_comparative",
            "contract_version": "3.0"
        }

        self.resolutions[claim_id] = json.dumps(resolution, sort_keys=True)

        # History – keep only last 10
        hist = self._safe_loads(self.decision_history.get(claim_id, "[]"), [])
        hist.append({
            "decision": decision,
            "resolved_at": now,
            "is_reassessment": is_reassessment,
            "previous_decision": previous_decision,
            "challenge_reason": challenge_reason[:150],
            "evidence_version": claim.get("evidence_version", 1)
        })
        if len(hist) > 10:
            hist = hist[-10:]
        self.decision_history[claim_id] = json.dumps(hist, sort_keys=True)

        # Status transition
        was_resolved = status == "resolved"
        claim["status"] = "resolved"
        claim["updated_at"] = now
        self.claims[claim_id] = json.dumps(claim, sort_keys=True)

        if not was_resolved:
            self.resolved_count += u256(1)

        return json.dumps(resolution, sort_keys=True)

    @gl.public.write
    def challenge_resolution(self, claim_id: u256, reason: str) -> str:
        reason = reason.strip()
        assert 25 <= len(reason) <= 900, "Challenge reason length invalid"

        if claim_id not in self.resolutions:
            return json.dumps({"error": "No resolution exists"})

        claim_str = self.claims.get(claim_id, "")
        if not claim_str:
            return json.dumps({"error": "Claim not found"})

        claim = self._safe_loads(claim_str, {})
        if claim.get("status") != "resolved":
            return json.dumps({"error": "Only resolved claims can be challenged"})

        hist = self._safe_loads(self.decision_history.get(claim_id, "[]"), [])
        if len(hist) >= 7:
            return json.dumps({"error": "Maximum number of re-adjudications reached"})

        prev = self._safe_loads(self.resolutions[claim_id], {})
        previous_decision = prev.get("decision", "")

        claim["status"] = "challenged"
        claim["updated_at"] = self._now()
        self.claims[claim_id] = json.dumps(claim, sort_keys=True)

        challenge = {
            "claim_id": int(claim_id),
            "challenger": str(gl.message.sender_address),
            "reason": reason,
            "challenged_at": self._now(),
            "previous_decision": previous_decision
        }
        self.challenges[claim_id] = json.dumps(challenge, sort_keys=True)

        # Force complete re-fetch
        self.normalized_evidence[claim_id] = ""

        return json.dumps({
            "success": True,
            "message": "Challenge accepted. Next resolve will perform full re-adjudication with freshly acquired evidence.",
            "claim_id": int(claim_id)
        })

    # ================================================================
    # VIEW METHODS
    # ================================================================

    @gl.public.view
    def get_claim(self, claim_id: u256) -> str:
        return self.claims.get(claim_id, "{}")

    @gl.public.view
    def get_resolution(self, claim_id: u256) -> str:
        return self.resolutions.get(claim_id, "{}")

    @gl.public.view
    def get_challenge(self, claim_id: u256) -> str:
        return self.challenges.get(claim_id, "{}")

    @gl.public.view
    def get_history(self, claim_id: u256) -> str:
        return self.decision_history.get(claim_id, "[]")

    @gl.public.view
    def get_normalized_evidence(self, claim_id: u256) -> str:
        return self.normalized_evidence.get(claim_id, "")

    @gl.public.view
    def get_claim_count(self) -> u256:
        return self.claim_counter

    @gl.public.view
    def get_resolved_count(self) -> u256:
        return self.resolved_count

    @gl.public.view
    def get_stats(self) -> str:
        total = int(self.claim_counter)
        resolved = int(self.resolved_count)
        return json.dumps({
            "total_claims": total,
            "resolved_claims": resolved,
            "open_or_challenged": max(0, total - resolved)
        }, sort_keys=True)
