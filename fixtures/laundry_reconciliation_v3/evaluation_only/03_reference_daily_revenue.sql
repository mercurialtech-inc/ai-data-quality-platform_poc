WITH gross AS (
 SELECT location_id,payment_date AS report_date,SUM(amount) AS gross_amount
 FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` WHERE status='completed' GROUP BY location_id,payment_date
), refunds_by_day AS (
 SELECT p.location_id,r.refund_date AS report_date,SUM(r.amount) AS refund_amount
 FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.refunds` r JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` p ON r.payment_id=p.payment_id
 WHERE r.status='processed' GROUP BY p.location_id,r.refund_date
)
SELECT rr.location_id,rr.report_date,
 COALESCE(g.gross_amount,0)-COALESCE(r.refund_amount,0) AS expected_net_revenue,
 rr.reported_net_revenue,
 CASE WHEN rr.reported_net_revenue=COALESCE(g.gross_amount,0)-COALESCE(r.refund_amount,0) THEN 'PASS' ELSE 'FAIL' END AS status
FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.reported_revenue` rr LEFT JOIN gross g ON rr.location_id=g.location_id AND rr.report_date=g.report_date
LEFT JOIN refunds_by_day r ON rr.location_id=r.location_id AND rr.report_date=r.report_date
ORDER BY location_id,report_date;
