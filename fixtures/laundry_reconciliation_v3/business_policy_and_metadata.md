# Laundry reconciliation V3 — business policy and data catalog

Version V3 | Authority: demonstration policy, not actual WASH policy.
Evaluation snapshot: end of November 20, 2026. All monetary values are in a single demo currency; use exact decimal arithmetic. Source and reporting dates: Oct 31–Nov 19, 2026. The bank statement is complete for the fixture through the snapshot. Do not use today's date to evaluate this snapshot.

## Business definitions

- **Gross Revenue:** sum completed customer payments, grouped by the payment's location and payment date. Cancelled payments are excluded.
- **Net Revenue:** Gross Revenue less processed refunds recognized on the refund date at the original payment's location. Pending refunds are excluded. A refund-only day can have negative Net Revenue. Multiple refunds can reference one payment; avoid duplicating payments. The combined event dates must be preserved before aggregation. Daily reporting grain is location/date. Reports exist for all observed source event dates, including dates with no eligible activity; there is no requirement for an entirely inactive date outside that coverage.
- **Expected settlement:** eligible payments less processed refunds less the processor fee, at payout grain. The fixture uses a flat $2 fee per payout. Payouts batch two consecutive calendar days of events by location and vendor, with the payout initiated on the second day. A refund belongs to the batch containing its refund date. Each eligible event is assigned exactly once; cancelled payments and pending refunds are never included. Compare source values to components and component totals to the processor's stated payout.
- **Bank amount:** sum all positively valued, confirmed linked bank entries posted on or before the investigation date. No confirmed deposit means zero received; do not invent a match.
- **Settlement deadline:** payout date plus two calendar days for both vendors. A deposit on the due date counts as timely. This is distinct from the two-day batching interval.
- **Amount status:** PASS if cumulative actual equals expected; FAIL if overpaid, or underpaid at/after the end of the deadline; PENDING if underpaid before the deadline.
- **Timeliness status:** PASS when cumulative deposits on or before the deadline (and as of the investigation date) reach the expected amount; FAIL if that amount is not reached by end of deadline; otherwise PENDING. An excess payment is an amount failure even if timing passes. MAX(posting_date) is descriptive, not a sufficient timeliness test. No bank entries means NULL last deposit date. Overall FAIL if either check fails; otherwise PENDING if either is pending; otherwise PASS. Zero tolerance for discrepancies.

## Table catalog and relationships

| Table | Grain / identifier | Fields and role |
|---|---|---|
| payments | payment_id | location_id, payment_date, amount (positive NUMERIC), status (completed/cancelled), vendor_id (VA/VB) |
| refunds | refund_id | payment_id references payments; refund_date, amount (positive NUMERIC), status (processed/pending). Location and vendor inherited from original payment. |
| reported_revenue | location_id + report_date | report_id, reported_net_revenue (signed NUMERIC); internal reporting output, not the authoritative calculation. |
| payout_components | component_id | payout_id, component_type (payment/refund/fee), source_id, signed_amount. Payment and refund source IDs reference their respective source tables; fee source IDs are processor references, not a seventh table. |
| payouts | payout_id | location_id, vendor_id, payout_date, processor_amount, expected_bank_date, processor_reference, status (sent). Sent does not establish bank receipt. |
| bank_entries | bank_entry_id | posting_date, amount, payout_id, bank_reference. Multiple deposits per payout. payout_id is a trusted link in this fixture; bank_reference agrees with processor_reference. |

Each location uses one payment vendor in the fixture. A payment may have multiple refunds. All processed refund dates are on/after the original payment date, and their cumulative amount cannot exceed the payment. All bank posting dates are on/after payout initiation. No ambiguous or unmatched deposits, reversals, FX, disputed chargebacks or separate cross-batch refunds in V3.

## Evidence and access

The actual SQL used to populate reported_revenue is retained as `reporting_transformation.sql` (the same statement is embedded in the seed). This is internal transformation lineage evidence, to be retrieved only if relevant to an investigation. It is not the approved business definition. The AI can use these business definitions, table descriptions and authorized source/lineage evidence. Keep evaluation labels, reference queries, generator and demo answer key out of the AI/RAG context. Bank shortfalls or excesses establish an amount discrepancy, not a proven bank or processor fault. Additional evidence would be required to establish the underlying operational cause.
