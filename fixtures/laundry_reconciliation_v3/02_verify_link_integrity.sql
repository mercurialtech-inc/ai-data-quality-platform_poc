 -- All counts should be zero.
SELECT 'payments_unique' AS check_name, (SELECT COUNT(*) FROM (SELECT payment_id FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` GROUP BY payment_id HAVING COUNT(*)<>1 OR payment_id IS NULL) q) AS violations
UNION ALL
SELECT 'refunds_unique' AS check_name, (SELECT COUNT(*) FROM (SELECT refund_id FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.refunds` GROUP BY refund_id HAVING COUNT(*)<>1 OR refund_id IS NULL) q) AS violations
UNION ALL
SELECT 'payouts_unique' AS check_name, (SELECT COUNT(*) FROM (SELECT payout_id FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payouts` GROUP BY payout_id HAVING COUNT(*)<>1 OR payout_id IS NULL) q) AS violations
UNION ALL
SELECT 'payout_components_unique' AS check_name, (SELECT COUNT(*) FROM (SELECT component_id FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payout_components` GROUP BY component_id HAVING COUNT(*)<>1 OR component_id IS NULL) q) AS violations
UNION ALL
SELECT 'bank_entries_unique' AS check_name, (SELECT COUNT(*) FROM (SELECT bank_entry_id FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.bank_entries` GROUP BY bank_entry_id HAVING COUNT(*)<>1 OR bank_entry_id IS NULL) q) AS violations
UNION ALL
SELECT 'report_grain_unique' AS check_name, (SELECT COUNT(*) FROM (SELECT location_id,report_date FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.reported_revenue` GROUP BY location_id,report_date HAVING COUNT(*)<>1) q) AS violations
UNION ALL
SELECT 'report_coverage' AS check_name, (WITH expected_dates AS (SELECT location_id,payment_date AS report_date FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` UNION DISTINCT SELECT p.location_id,r.refund_date FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.refunds` r JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` p ON r.payment_id=p.payment_id) SELECT COUNT(*) FROM (SELECT d.location_id,d.report_date FROM expected_dates d LEFT JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.reported_revenue` r ON d.location_id=r.location_id AND d.report_date=r.report_date WHERE r.location_id IS NULL UNION ALL SELECT r.location_id,r.report_date FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.reported_revenue` r LEFT JOIN expected_dates d ON d.location_id=r.location_id AND d.report_date=r.report_date WHERE d.location_id IS NULL) q) AS violations
UNION ALL
SELECT 'refund_links_dates_amounts' AS check_name, (SELECT COUNT(*) FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.refunds` r LEFT JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` p ON r.payment_id=p.payment_id WHERE p.payment_id IS NULL OR p.status<>'completed' OR r.refund_date<p.payment_date OR r.amount<=0) AS violations
UNION ALL
SELECT 'refund_amount_limit' AS check_name, (SELECT COUNT(*) FROM (SELECT p.payment_id FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` p JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.refunds` r ON r.payment_id=p.payment_id WHERE r.status='processed' GROUP BY p.payment_id,p.amount HAVING SUM(r.amount)>p.amount) q) AS violations
UNION ALL
SELECT 'eligible_payment_coverage' AS check_name, (SELECT COUNT(*) FROM (SELECT s.payment_id FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` s LEFT JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payout_components` c ON c.component_type='payment' AND c.source_id=s.payment_id GROUP BY s.payment_id,s.status HAVING COUNT(c.component_id)<>CASE WHEN s.status='completed' THEN 1 ELSE 0 END) q) AS violations
UNION ALL
SELECT 'eligible_refund_coverage' AS check_name, (SELECT COUNT(*) FROM (SELECT s.refund_id FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.refunds` s LEFT JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payout_components` c ON c.component_type='refund' AND c.source_id=s.refund_id GROUP BY s.refund_id,s.status HAVING COUNT(c.component_id)<>CASE WHEN s.status='processed' THEN 1 ELSE 0 END) q) AS violations
UNION ALL
SELECT 'component_payout_fk' AS check_name, (SELECT COUNT(*) FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payout_components` c LEFT JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payouts` p ON c.payout_id=p.payout_id WHERE p.payout_id IS NULL OR c.component_type NOT IN ('payment','refund','fee')) AS violations
UNION ALL
SELECT 'payment_component_matches_source' AS check_name, (SELECT COUNT(*) FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payout_components` c JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payouts` p ON c.payout_id=p.payout_id LEFT JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` s ON c.source_id=s.payment_id WHERE c.component_type='payment' AND (s.payment_id IS NULL OR s.status<>'completed' OR c.signed_amount<>s.amount OR s.location_id<>p.location_id OR s.vendor_id<>p.vendor_id OR s.payment_date NOT BETWEEN DATE_SUB(p.payout_date, INTERVAL 1 DAY) AND p.payout_date)) AS violations
UNION ALL
SELECT 'refund_component_matches_source' AS check_name, (SELECT COUNT(*) FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payout_components` c JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payouts` p ON c.payout_id=p.payout_id LEFT JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.refunds` r ON c.source_id=r.refund_id LEFT JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` s ON r.payment_id=s.payment_id WHERE c.component_type='refund' AND (r.refund_id IS NULL OR s.payment_id IS NULL OR r.status<>'processed' OR c.signed_amount<>-r.amount OR s.location_id<>p.location_id OR s.vendor_id<>p.vendor_id OR r.refund_date NOT BETWEEN DATE_SUB(p.payout_date, INTERVAL 1 DAY) AND p.payout_date)) AS violations
UNION ALL
SELECT 'fee_per_payout' AS check_name, (SELECT COUNT(*) FROM (SELECT p.payout_id FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payouts` p LEFT JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payout_components` c ON p.payout_id=c.payout_id AND c.component_type='fee' GROUP BY p.payout_id HAVING COUNT(c.component_id)<>1 OR SUM(c.signed_amount)<>NUMERIC '-2.00') q) AS violations
UNION ALL
SELECT 'payout_total_matches' AS check_name, (SELECT COUNT(*) FROM (SELECT p.payout_id FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payouts` p LEFT JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payout_components` c ON p.payout_id=c.payout_id GROUP BY p.payout_id,p.processor_amount HAVING COUNT(c.component_id)=0 OR SUM(c.signed_amount)<>p.processor_amount) q) AS violations
UNION ALL
SELECT 'deadline_two_days' AS check_name, (SELECT COUNT(*) FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payouts` p WHERE p.expected_bank_date<>DATE_ADD(p.payout_date, INTERVAL 2 DAY)) AS violations
UNION ALL
SELECT 'bank_links_dates_amounts' AS check_name, (SELECT COUNT(*) FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.bank_entries` b LEFT JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payouts` p ON b.payout_id=p.payout_id WHERE p.payout_id IS NULL OR b.posting_date<p.payout_date OR b.posting_date>DATE '2026-11-20' OR b.amount<=0 OR b.bank_reference<>p.processor_reference) AS violations
UNION ALL
SELECT 'source_payment_validity' AS check_name, (SELECT COUNT(*) FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` WHERE amount<=0 OR status NOT IN ('completed','cancelled') OR vendor_id NOT IN ('VA','VB') OR payment_date>DATE '2026-11-20') AS violations
UNION ALL
SELECT 'refund_status_validity' AS check_name, (SELECT COUNT(*) FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.refunds` WHERE status NOT IN ('processed','pending') OR refund_date>DATE '2026-11-20') AS violations
UNION ALL
SELECT 'payout_positive_and_sent' AS check_name, (SELECT COUNT(*) FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payouts` WHERE processor_amount<=0 OR status<>'sent' OR payout_date>DATE '2026-11-20') AS violations
UNION ALL
SELECT 'one_vendor_per_location' AS check_name, (SELECT COUNT(*) FROM (SELECT location_id FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` GROUP BY location_id HAVING COUNT(DISTINCT vendor_id)<>1) q) AS violations
ORDER BY check_name;
