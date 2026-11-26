WITH component_totals AS (
 SELECT payout_id,SUM(signed_amount) AS expected_settlement FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payout_components` GROUP BY payout_id
), bank_totals AS (
 SELECT b.payout_id,SUM(b.amount) AS actual_settlement,
 SUM(CASE WHEN b.posting_date<=p.expected_bank_date THEN b.amount ELSE 0 END) AS received_by_deadline,
 MAX(b.posting_date) AS last_deposit_date,COUNT(*) AS bank_entry_count
 FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.bank_entries` b JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payouts` p ON b.payout_id=p.payout_id
 WHERE b.posting_date<=DATE '2026-11-20' GROUP BY b.payout_id
), amounts AS (
 SELECT p.payout_id,p.expected_bank_date,c.expected_settlement,
 COALESCE(b.actual_settlement,0) AS actual_settlement,COALESCE(b.received_by_deadline,0) AS received_by_deadline,
 b.last_deposit_date,COALESCE(b.bank_entry_count,0) AS bank_entry_count
 FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payouts` p JOIN component_totals c ON p.payout_id=c.payout_id LEFT JOIN bank_totals b ON p.payout_id=b.payout_id
 WHERE p.payout_date<=DATE '2026-11-20'
), statuses AS (
 SELECT *, CASE WHEN actual_settlement=expected_settlement THEN 'PASS'
 WHEN actual_settlement<expected_settlement AND DATE '2026-11-20'<expected_bank_date THEN 'PENDING' ELSE 'FAIL' END AS amount_status,
 CASE WHEN received_by_deadline>=expected_settlement THEN 'PASS'
 WHEN DATE '2026-11-20'<expected_bank_date THEN 'PENDING' ELSE 'FAIL' END AS timing_status
 FROM amounts
)
SELECT payout_id,expected_settlement,actual_settlement,received_by_deadline,last_deposit_date,bank_entry_count,amount_status,timing_status,
 CASE WHEN amount_status='FAIL' OR timing_status='FAIL' THEN 'FAIL'
 WHEN amount_status='PENDING' OR timing_status='PENDING' THEN 'PENDING' ELSE 'PASS' END AS overall_status
FROM statuses
ORDER BY payout_id;
