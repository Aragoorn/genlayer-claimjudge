# ClaimJudge – AI-Powered Decentralized Claim & Dispute Resolver

## Overview

ClaimJudge is an intelligent contract on GenLayer that enables anyone to create claims, submit evidence, receive an AI judgment, challenge the decision, and request a full reassessment.
## contract address:0xe8e1eBf97070F7d4Ccbe2a87B55Cf4bA04f0434F
https://explorer-studio.genlayer.com/address/0xe8e1eBf97070F7d4Ccbe2a87B55Cf4bA04f0434F

## live demo 


## Steward Feedback Compliance

All requested improvements have been implemented and tested:

### 1. Reassessment consumes challenge reason and prior verdict
When `resolve_claim` is called after a challenge, the AI receives:
- The previous decision
- The full challenge reason
- The latest evidence stored in the contract

### 2. Reviewable decision history
Every resolution (including reassessments) is permanently stored in `decision_history` and can be read via `get_history`.

### 3. Updated evidence is always read from the contract
The contract always reads the current `evidence_urls` from storage before making a judgment.

## Successful Test Flow (Verified on Studio)

1. **create_claim** → Claim #0 created
2. **resolve_claim** → First decision: `VALID`
3. **challenge_resolution** → Challenge submitted with detailed reason
4. **resolve_claim** (again) → Reassessment performed
5. **get_history** → Shows both decisions
6. **get_resolution** → Confirms `is_reassessment: true` and includes challenge reason

### Example Reassessment Result
```json
{
  "decision": "VALID",
  "is_reassessment": true,
  "previous_decision": "VALID",
  "challenge_reason": "The AI decision did not properly consider the police report...",
  "reasoning": "AI consensus decided the claim is VALID. Reassessment considered challenge reason: ..."
}

### Main Functions

Function                      Description  

create_claim                Create a new claim
add_evidence                Add additional evidence
resolve_claim               AI judgment (supports first resolve + reassessment)
challenge_resolution        Challenge a resolution
get_claim                   View claim details
get_resolution              View latest resolution
get_challenge               View challenge data
get_history                 View full decision history
get_stats                   Protocol statistics

### How to Test
Create a claim
Resolve it
Challenge it with a clear reason
Resolve it again (reassessment)
Check get_history and get_resolution

Repository:
https://github.com/Aragoorn/genlayer-claimjudge
