CREATE OR REPLACE TABLE `gen-lang-client-0597630202.laundry_reconciliation_v3.reported_revenue` AS
WITH report_dates AS (
  SELECT location_id, payment_date AS report_date FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payments`
  UNION DISTINCT
  SELECT p.location_id, r.refund_date AS report_date
  FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.refunds` r JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` p ON r.payment_id=p.payment_id
), events AS (
  SELECT location_id, payment_date AS report_date, amount AS signed_amount
  FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` WHERE status='completed'
  UNION ALL
  SELECT p.location_id,
         CASE WHEN p.vendor_id='VB' THEN p.payment_date ELSE r.refund_date END AS report_date,
         -r.amount AS signed_amount
  FROM `gen-lang-client-0597630202.laundry_reconciliation_v3.refunds` r JOIN `gen-lang-client-0597630202.laundry_reconciliation_v3.payments` p ON r.payment_id=p.payment_id
  WHERE r.status='processed'
), daily AS (
  SELECT location_id, report_date, SUM(signed_amount) AS net_revenue
  FROM events GROUP BY location_id, report_date
)
SELECT d.location_id || '-' || CAST(d.report_date AS STRING) AS report_id,
       d.location_id, d.report_date, COALESCE(a.net_revenue,0) AS reported_net_revenue
FROM report_dates d LEFT JOIN daily a
ON d.location_id=a.location_id AND d.report_date=a.report_date;
