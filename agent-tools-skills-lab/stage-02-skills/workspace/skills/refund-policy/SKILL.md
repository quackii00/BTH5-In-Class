---
name: refund-policy
description: Determine whether a refund request is eligible by finding the applicable policy in data/policies/ based on the purchase date. Use this skill when a user asks whether a purchase can be refunded and the applicable policy period must be determined.
---

# Refund Policy

Use this skill to determine which refund policy applies to a user's purchase.

## Procedure

1. Find the relevant policy documents in `data/policies/`.
2. Read the policy documents to determine their effective date range.
3. Select the policy based on the purchase date, not the refund-request date.
4. Check the refund conditions in the selected policy.
5. Calculate the number of days between the purchase date and the refund-request date.
6. Check whether the item has been activated.

## Missing information

Before reaching a conclusion, ask the user for the missing information if any of these are unavailable:

- purchase date
- refund-request date
- activation status

Do not assume that an item is not activated when the user has not provided its activation status.

## Answer format

Use the reference template at:

`references/answer-template.md`

The answer must identify the applicable policy, calculate the number of days elapsed, state whether the request is eligible, include any applicable fee, and provide the document path used as evidence.
