<img width="1920" height="881" alt="Screenshot (2777)" src="https://github.com/user-attachments/assets/0d50a60f-3960-4857-a809-04bce50f4eea" />
<img width="1920" height="854" alt="Screenshot (2776)" src="https://github.com/user-attachments/assets/596b41c7-faed-4360-af91-821e607f8bd0" />
<img width="1920" height="884" alt="Screenshot (2781)" src="https://github.com/user-attachments/assets/fcf67771-e0c3-4503-9741-7da9b95dfd10" />
<img width="1920" height="878" alt="Screenshot (2780)" src="https://github.com/user-attachments/assets/f2f489d8-ef21-4181-a2ef-df345ac75b0f" />
<img width="1920" height="888" alt="Screenshot (2779)" src="https://github.com/user-attachments/assets/fff77032-0b1d-405f-b7cc-90b4e3c16326" />
<img width="1920" height="869" alt="Screenshot (2778)" src="https://github.com/user-attachments/assets/d20d7157-9ee3-4fa0-a73e-4ec1a93d74e3" />
<img width="1920" height="890" alt="Screenshot (2796)" src="https://github.com/user-attachments/assets/a1945e4e-1cf8-4786-8bd8-5495e386cb06" />
# ClaimJudge – AI-Powered Decentralized Claim & Dispute Resolver

**Final version – Fully compliant with steward feedback**

## Overview

ClaimJudge is an intelligent contract on GenLayer that enables anyone to create claims, submit evidence, receive an AI judgment, challenge the decision, and request a full reassessment.
## contract address:0x8A8B387C84552863c077C3085dF719E6DA42d673
http://explorer-studio.genlayer.com/address/0x8A8B387C84552863c077C3085dF719E6DA42d673
https://explorer-studio.genlayer.com/tx/0x38c1fea49cb5c9aeeea1e16f7320ec65ae9d217041290d5d8d53cc76c431e14b
https://explorer-studio.genlayer.com/tx/0xf9fab74f4827f03bfc4c891d85b89141212ede63e51d535dcb5b6164ac0bfe13
https://explorer-studio.genlayer.com/tx/0xf830d907987c58994814400366ae9655e6f415a5f5aebafa0c32fd5222c77816

## live demo 
https://aesthetic-longma-6e391d.netlify.app/


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
https://github.com/Aragoorn/genlayer-claimjudge-dapp
