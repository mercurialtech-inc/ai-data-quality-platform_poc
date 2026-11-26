# Instructor walkthrough — keep out of AI retrieval

## One connected comparison: L101 / PO001 and L102 / PO011

October 31 payments and November 1 refunds (cross-month). Both payouts settle on time. This shows that an internal revenue reporting error does not imply the bank is wrong.

| Location | Vendor | Date | Correct revenue | Reported | Variance (reported−expected) |
|---|---|---|---:|---:|---:|
| L101 | VA | Oct 31 | 90.50 | 90.50 | 0.00 |
| L101 | VA | Nov 1 | -3.00 | -3.00 | 0.00 |
| L102 | VB | Oct 31 | 105.50 | 102.50 | -3.00 |
| L102 | VB | Nov 1 | -3.00 | 0.00 | 3.00 |

Use the following minimal queries, in sequence (dataset in project `gen-lang-client-0597630202`).

```sql
SELECT payment_id, location_id, vendor_id, payment_date, amount, status
FROM `laundry_reconciliation_v3.payments`
WHERE location_id IN ('L101','L102') AND payment_date BETWEEN DATE '2026-10-31' AND DATE '2026-11-01';

SELECT r.refund_id,r.payment_id,r.refund_date,r.amount,r.status
FROM `laundry_reconciliation_v3.refunds` r
JOIN `laundry_reconciliation_v3.payments` p USING(payment_id)
WHERE p.location_id IN ('L101','L102') AND p.payment_date=DATE '2026-10-31';

SELECT location_id,report_date,reported_net_revenue
FROM `laundry_reconciliation_v3.reported_revenue`
WHERE location_id IN ('L101','L102') AND report_date BETWEEN DATE '2026-10-31' AND DATE '2026-11-01';

SELECT payout_id,component_type,source_id,signed_amount
FROM `laundry_reconciliation_v3.payout_components`
WHERE payout_id IN ('PO001','PO011');

SELECT payout_id,location_id,payout_date,processor_amount,expected_bank_date
FROM `laundry_reconciliation_v3.payouts` WHERE payout_id IN ('PO001','PO011');

SELECT bank_entry_id,payout_id,posting_date,amount
FROM `laundry_reconciliation_v3.bank_entries` WHERE payout_id IN ('PO001','PO011');
```

Net revenue over both days: L101 87.50, L102 102.50. Each payout deducts 2.00 in fees, making expected settlement 85.50 and 100.50 respectively. Each matches the processor amount and bank total. Both have due date Nov 3. The source, payout and bank amounts remain linked even for the reporting failure. Inspect the actual reporting transformation after identifying the common pattern across VB locations. VB same-day refunds are controls that do not expose the defect (e.g., L102 Nov 2–3). 

## Settlement exceptions (as of Nov 20 end of day)

| Payout | Expected | Actual | By deadline | Amount | Timing | Why this example matters |
|---|---:|---:|---:|---|---|---|
| PO001 | 85.50 | 85.50 | 85.50 | PASS | PASS | Normal, on deadline |
| PO011 | 100.50 | 100.50 | 100.50 | PASS | PASS | Multiple deposits, no revenue-to-bank coupling |
| PO003 | 121.50 | 111.50 | 111.50 | FAIL | FAIL | Two on-time partial deposits, $10 still missing |
| PO007 | 93.25 | 93.25 | 46.62 | PASS | FAIL | Second deposit late |
| PO016 | 142.75 | 0 | 0 | FAIL | FAIL | No bank entry after deadline |
| PO024 | 95.50 | 100.50 | 100.50 | FAIL | PASS | Excess, timely |
| PO087 | 110.75 | 115.75 | 110.75 | FAIL | PASS | Late excess: MAX date alone wrongly fails timing |
| PO090 | 104.00 | 0 | 0 | PENDING | PENDING | No deposit yet, not due |
| PO100 | 115.50 | 57.75 | 57.75 | PENDING | PENDING | Partial deposit, not due |

All other examples, exact dates and amounts are available in the CSV manifests. Do not claim that operational causes are confirmed merely because the shortfall is localized.
