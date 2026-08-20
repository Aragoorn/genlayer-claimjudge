# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json
from datetime import datetime, timezone

class ClaimJudge(gl.Contract):
    """
    ClaimJudge – Enterprise AI-Powered Decentralized Claim & Dispute Resolver
    Fully compliant with steward feedback (reassessment, history, evidence)
    """

    claim_counter: u256
    resolved_count: u256
    claims: TreeMap[u256, str]
    resolutions: TreeMap[u256, str]
    challenges: TreeMap[u256, str]
    decision_history: TreeMap[u256, str]

    def __init__(self):
        self.claim_counter = u256(0)
        self.resolved_count = u256(0)
        self.claims = TreeMap[u256, str]()
        self.resolutions = TreeMap[u256, str]()
        self.challenges = TreeMap[u256, str]()
        self.decision_history = TreeMap[u256, str]()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe_json_loads(self, data: str, default):
        try:
            return json.loads(data) if data else default
        except:
            return default

    @gl.public.write
    def create_claim(self, title: str, description: str, evidence_urls: str) -> u256:
        title = title.strip()
        description = description.strip()
        evidence_urls = evidence_urls.strip()

        assert len(title) >= 3, "Title too short"
        assert len(description) >= 10, "Description too short"

        claim_id = self.claim_counter
        self.claim_counter += u256(1)

        claim_data = {
            "id": int(claim_id),
            "title": title,
            "description": description,
            "evidence_urls": evidence_urls,
            "creator": str(gl.message.sender_address),
            "status": "open",
            "created_at": self._now(),
            "updated_at": self._now()
        }
        self.claims[claim_id] = json.dumps(claim_data, sort_keys=True)
        self.decision_history[claim_id] = "[]"
        return claim_id

    @gl.public.write
    def add_evidence(self, claim_id: u256, extra_urls: str) -> str:
        claim_str = self.claims.get(claim_id, "")
        if not claim_str:
            return json.dumps({"error": "Claim not found"})

        claim = self._safe_json_loads(claim_str, {})
        if claim.get("status") not in ["open", "challenged"]:
            return json.dumps({"error": "Claim cannot accept new evidence"})

        extra = extra_urls.strip()
        if not extra:
            return json.dumps({"error": "No evidence provided"})

        existing = claim.get("evidence_urls", "")
        claim["evidence_urls"] = (existing + "," + extra) if existing else extra
        claim["updated_at"] = self._now()
        self.claims[claim_id] = json.dumps(claim, sort_keys=True)

        return json.dumps({"success": True, "claim_id": int(claim_id)})

    @gl.public.write
    def resolve_claim(self, claim_id: u256) -> str:
        claim_str = self.claims.get(claim_id, "")
        if not claim_str:
            return json.dumps({"error": "Claim does not exist"})

        claim = self._safe_json_loads(claim_str, {})
        status = claim.get("status", "")

        if status not in ["open", "challenged"]:
            if claim_id in self.resolutions:
                return self.resolutions[claim_id]
            return json.dumps({"error": "Claim already finalized"})

        # ===== خواندن challenge reason و prior verdict =====
        challenge_reason = ""
        previous_decision = ""
        is_reassessment = False

        if claim_id in self.challenges:
            ch = self._safe_json_loads(self.challenges[claim_id], {})
            challenge_reason = ch.get("reason", "")
            previous_decision = ch.get("previous_decision", "")
            is_reassessment = True

        # ===== خواندن evidence به‌روز شده از قرارداد =====
        evidence = claim.get("evidence_urls", "None provided")
        title = claim.get("title", "")
        description = claim.get("description", "")

        def get_input() -> str:
            text = f"""Title: {title}
Description: {description}
Evidence URLs: {evidence}"""

            if is_reassessment:
                text += f"""

=== REASSESSMENT REQUESTED ===
Previous Decision: {previous_decision}
Challenge Reason: {challenge_reason}

Please carefully re-evaluate the claim taking into account the challenge reason and the current evidence from the contract."""
            return text

        raw = gl.eq_principle.prompt_non_comparative(
            get_input,
            task="You are a fair and strict AI judge. Decide if the claim is VALID, PARTIALLY_VALID, or INVALID. Respond with ONLY one of these three words.",
            criteria="Output must be exactly one of: VALID, PARTIALLY_VALID, INVALID. No extra text or explanation."
        )

        decision = str(raw).strip().upper()
        if decision not in ["VALID", "PARTIALLY_VALID", "INVALID"]:
            decision = "INVALID"

        now = self._now()

        resolution = {
            "claim_id": int(claim_id),
            "decision": decision,
            "confidence": 85 if decision == "VALID" else (65 if decision == "PARTIALLY_VALID" else 30),
            "reasoning": f"AI consensus decided the claim is {decision}." +
                         (f" Reassessment considered challenge reason: {challenge_reason}" if is_reassessment else ""),
            "summary": f"Claim judged as {decision}",
            "resolved_at": now,
            "resolved_by": "GenLayer AI Consensus",
            "is_reassessment": is_reassessment,
            "previous_decision": previous_decision,
            "challenge_reason": challenge_reason
        }

        self.resolutions[claim_id] = json.dumps(resolution, sort_keys=True)

        # ===== حفظ تاریخچه کامل و قابل بازبینی =====
        hist = self._safe_json_loads(self.decision_history.get(claim_id, "[]"), [])
        hist.append({
            "decision": decision,
            "resolved_at": now,
            "is_reassessment": is_reassessment,
            "previous_decision": previous_decision,
            "challenge_reason": challenge_reason
        })
        self.decision_history[claim_id] = json.dumps(hist, sort_keys=True)

        # به‌روزرسانی وضعیت
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
        assert len(reason) >= 10, "Challenge reason too short"

        if claim_id not in self.resolutions:
            return json.dumps({"error": "No resolution to challenge"})

        claim_str = self.claims.get(claim_id, "")
        if not claim_str:
            return json.dumps({"error": "Claim not found"})

        claim = self._safe_json_loads(claim_str, {})
        prev = self._safe_json_loads(self.resolutions[claim_id], {})
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

        return json.dumps({
            "success": True,
            "message": "Claim challenged successfully. It can now be re-resolved with the challenge reason.",
            "claim_id": int(claim_id)
        })

    # ==================== View Functions ====================

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
            "open_claims": max(0, total - resolved)
        }, sort_keys=True)
