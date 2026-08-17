# ClaimJudge – AI-Powered Decentralized Claim & Dispute Resolver

**An advanced Intelligent Contract on GenLayer that uses AI consensus to fairly judge real-world claims and disputes.**

Built for the GenLayer Builders Program – August 2026.

## Overview

ClaimJudge demonstrates the core power of GenLayer as the **adjudication layer** for the agentic economy.  
Anyone can submit a claim (freelance work, bounty completion, delivery disputes, etc.). The network reaches consensus using LLMs via the Equivalence Principle (`prompt_non_comparative`) and stores a transparent, on-chain judgment.

### Key Features
- Create claims with title, description and optional evidence
- Add extra evidence after creation
- AI resolution using GenLayer’s non-deterministic LLM consensus
- Challenge existing resolutions
- Full on-chain history + statistics
- Clean, production-ready Python code with proper storage patterns

## Contract Address
`0x112f563F4DE1d981f0538A456Ea58C81cF93B73C`

## How to Use (GenLayer Studio)

1. **create_claim(title, description, evidence_urls)**  
   Creates a new claim and returns the claim_id.

2. **add_evidence(claim_id, extra_urls)** (optional)  
   Adds more evidence to an open claim.

3. **resolve_claim(claim_id)**  
   Triggers AI judgment. Uses `prompt_non_comparative` for reliable consensus.

4. **challenge_resolution(claim_id, reason)**  
   Allows anyone to formally challenge a decision.

### View Methods
- `get_claim(claim_id)`
- `get_resolution(claim_id)`
- `get_challenge(claim_id)`
- `get_claim_count()`
- `get_resolved_count()`
- `get_stats()`

## Example Flow
```text
create_claim(
  "Freelance website redesign completed",
  "I fully completed the website redesign as agreed...",
  ""
)
→ claim_id = 0

resolve_claim(0)
→ AI returns VALID / PARTIALLY_VALID / INVALID with reasoning

Technical HighlightsUses gl.eq_principle.prompt_non_comparative for stable LLM consensus
TreeMap storage with JSON serialization (best practice)
Deterministic timestamps via transaction context
Proper error handling and status management
Fully typed and ready for production use

Future MilestonesFrontend dApp
Payable escrow integration
Multi-party disputes
Reputation system based on past judgments

Built with  for GenLayer
This project showcases real adjudication use-cases that were previously impossible on traditional blockchains.