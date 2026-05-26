# Governance FAQ

## Q. Why isn't CI success enough?
CI tests verify that code works as expected.
They do not verify that the change is safe to deploy to production,
that the blast radius is acceptable,
or that the right stakeholders have approved the action.
CI success = code is correct. Production authorization = separate governance decision.

## Q. Why is production blocked by default?
Production deployment affects real users and real data.
A staging approval is scoped to staging only.
Production requires a separate, explicit approval with wider stakeholder consensus.

## Q. Is this autonomous AI?
No. This project prepares human decision contracts.
It does not autonomously approve, deploy, pay, or execute anything.
Human approval is always required before controlled execution.

## Q. What is a Human Decision Contract?
A Human Decision Contract defines:
- what the human is approving
- what actions become allowed after approval
- what actions remain blocked even after approval
- what happens if the human rejects or requests rework

It is not a button. It is a scoped execution contract.

## Q. Why not allow automatic deployment after tests pass?
Tests verify correctness. They do not verify:
- blast radius
- rollback readiness
- organizational approval
- production impact
- escalation requirements
Automatic deployment would bypass these governance checks.

## Q. What is the Remediation Verification Gate?
It checks whether an AI-generated fix is ready for human review.
It verifies evidence, test results, security retest, regression risk, rollback readiness, and blast radius.
It does not apply patches or authorize deployment.

## Q. What is the Approval Unit Builder?
It generates a minimal human decision contract from a verified remediation candidate.
It defines approval_question, allowed_actions, still_blocked_actions, and recommended_human_action.
It does not execute the approval or deploy anything.

## Q. What does "scoped approval" mean?
Scoped approval means the human approval only allows specific actions.
Example: staging merge is allowed, production deployment remains blocked.
Approval does not grant unrestricted execution permission.
