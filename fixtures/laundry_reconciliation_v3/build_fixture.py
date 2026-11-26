"""Generate V3, run local relational checks, write BigQuery scripts and CSVs. Python stdlib only."""
from pathlib import Path
from datetime import date,timedelta
from collections import defaultdict,Counter
from decimal import Decimal
import csv, sqlite3, random

ROOT=Path(__file__).resolve().parent
DS='gen-lang-client-0597630202.laundry_reconciliation_v3'
ASOF=date(2026,11,20)
START=date(2026,10,31)
R=random.Random(426)
T={k:[] for k in ['payments','refunds','payouts','payout_components','bank_entries','reported_revenue']}
G=[]; B=[]
# IDs carry no outcome labels. Explicit bank event schedule (fixture generator only).
exceptions={3:'short_split',7:'late_split',16:'missing',24:'excess_split',29:'short_single',36:'late_single',44:'short_split',53:'late_split',65:'excess_single',72:'short_split',87:'late_excess',96:'late_single',90:'pending_none',100:'pending_partial'}
# cents throughout the independent generator / oracle

def add(t,**row): T[t].append(row)
def money(c): return f'{Decimal(c)/100:.2f}'
def dstr(d):return d.isoformat()
def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def event(loc,day,vendor,amount,status='completed'):
    pid=f'P{len(T["payments"])+1:05d}'
    add('payments',payment_id=pid,location_id=loc,payment_date=dstr(day),amount=money(amount),status=status,vendor_id=vendor)
    return pid,amount,day,status

def refund(payment,day,amount,status='processed'):
    rid=f'R{len(T["refunds"])+1:04d}'
    add('refunds',refund_id=rid,payment_id=payment[0],refund_date=dstr(day),amount=money(amount),status=status)
    return rid,amount,day,status

expected=defaultdict(int)
for l in range(10):
    loc=f'L{101+l}'; vendor='VB' if l in (1,6) else 'VA'
    for k in range(10):
        n=l*10+k+1; po=f'PO{n:03d}'; a=START+timedelta(days=2*k); b=a+timedelta(days=1); due=b+timedelta(days=2)
        # Every location has the same eligibility and settlement policy. One vendor has the reporting-only defect.
        ps=[event(loc,a,vendor,R.randrange(8,23)*100+R.choice([0,25,50,75])) for _ in range(6)]
        if k%3 != 0 or k%2==1:
            ps += [event(loc,b,vendor,R.randrange(8,23)*100) for _ in range(2)]
        if k%2==0: ps.append(event(loc,a,vendor,900,'cancelled'))
        rs=[refund(ps[0],b if k%2==0 else a,300+100*(k%3))]
        if k%2==0: rs.append(refund(ps[0],a,200)) # multiple refunds against same payment; no fan-out permitted
        if k%4==0: rs.append(refund(ps[1],b,200,'pending'))
        expected[loc,dstr(a)]+=0; expected[loc,dstr(b)]+=0
        for p in ps:
            if p[3]=='completed':expected[loc,dstr(p[2])]+=p[1]
        for r in rs:
            if r[3]=='processed':expected[loc,dstr(r[2])]-=r[1]
        total=sum(p[1] for p in ps if p[3]=='completed')-sum(r[1] for r in rs if r[3]=='processed')-200
        assert total>2000
        add('payouts',payout_id=po,location_id=loc,payout_date=dstr(b),processor_amount=money(total),expected_bank_date=dstr(due),processor_reference=f'PR-{n:03d}',status='sent',vendor_id=vendor)
        for kind,items,sign,eligible in [('payment',ps,1,'completed'),('refund',rs,-1,'processed')]:
            for e in items:
                if e[3]==eligible:
                    add('payout_components',component_id=f'C{len(T["payout_components"])+1:05d}',payout_id=po,component_type=kind,source_id=e[0],signed_amount=money(sign*e[1]))
        add('payout_components',component_id=f'C{len(T["payout_components"])+1:05d}',payout_id=po,component_type='fee',source_id=f'F{n:03d}',signed_amount=money(-200))
        mode=exceptions.get(n,'normal'); half=total//2
        # bank entries are a separate observed event stream, not overwritten report values
        if mode=='normal':
            if k==9: deposits=[(b+timedelta(days=1),total)] if n%2 else [(b,half),(b+timedelta(days=1),total-half)]
            elif n%3==0: deposits=[(b+timedelta(days=1),total)]
            elif n%3==1: deposits=[(due,total)]
            else: deposits=[(b+timedelta(days=1),half),(due,total-half)]
        elif mode=='short_split': deposits=[(b+timedelta(days=1),half),(due,total-half-1000)]
        elif mode=='short_single':deposits=[(due,total-1000)]
        elif mode=='late_split':deposits=[(b+timedelta(days=1),half),(due+timedelta(days=2),total-half)]
        elif mode=='late_single':deposits=[(due+timedelta(days=1),total)]
        elif mode=='excess_split':deposits=[(b+timedelta(days=1),half),(due,total-half+500)]
        elif mode=='excess_single':deposits=[(due,total+500)]
        elif mode=='late_excess':deposits=[(due,total),(due+timedelta(days=1),500)]
        elif mode=='missing' or mode=='pending_none':deposits=[]
        elif mode=='pending_partial':deposits=[(b+timedelta(days=1),half)]
        else:raise AssertionError(mode)
        assert all(b<=day<=ASOF and val>0 for day,val in deposits),(po,mode,deposits)
        for day,val in deposits:
            add('bank_entries',bank_entry_id=f'B{len(T["bank_entries"])+1:04d}',posting_date=dstr(day),amount=money(val),payout_id=po,bank_reference=f'PR-{n:03d}')
        received=sum(v for _,v in deposits); timely=sum(v for day,v in deposits if day<=due)
        amount_status='PASS' if received==total else 'PENDING' if received<total and ASOF<due else 'FAIL'
        timing_status='PASS' if timely>=total else 'PENDING' if ASOF<due else 'FAIL'
        B.append(dict(payout_id=po,expected_settlement=money(total),actual_settlement=money(received),received_by_deadline=money(timely),last_deposit_date=dstr(max(day for day,_ in deposits)) if deposits else '',amount_status=amount_status,timing_status=timing_status,overall_status='FAIL' if 'FAIL' in (amount_status,timing_status) else 'PENDING' if 'PENDING' in (amount_status,timing_status) else 'PASS',bank_entry_count=len(deposits),case=mode))

# SQL transformation is the actual reporting pipeline; it is executed locally and in the BigQuery seed.
# UNION of date spine intentionally deduplicates dates; UNION ALL preserves events.
REPORT='''WITH report_dates AS (
  SELECT location_id, payment_date AS report_date FROM {payments}
  UNION DISTINCT
  SELECT p.location_id, r.refund_date AS report_date
  FROM {refunds} r JOIN {payments} p ON r.payment_id=p.payment_id
), events AS (
  SELECT location_id, payment_date AS report_date, amount AS signed_amount
  FROM {payments} WHERE status='completed'
  UNION ALL
  SELECT p.location_id,
         CASE WHEN p.vendor_id='VB' THEN p.payment_date ELSE r.refund_date END AS report_date,
         -r.amount AS signed_amount
  FROM {refunds} r JOIN {payments} p ON r.payment_id=p.payment_id
  WHERE r.status='processed'
), daily AS (
  SELECT location_id, report_date, SUM(signed_amount) AS net_revenue
  FROM events GROUP BY location_id, report_date
)
SELECT d.location_id || '-' || CAST(d.report_date AS STRING) AS report_id,
       d.location_id, d.report_date, COALESCE(a.net_revenue,0) AS reported_net_revenue
FROM report_dates d LEFT JOIN daily a
ON d.location_id=a.location_id AND d.report_date=a.report_date'''
# Separate reference computation: aggregate payments and refunds independently, correct date, then join report.
REV='''WITH gross AS (
 SELECT location_id,payment_date AS report_date,SUM(amount) AS gross_amount
 FROM {payments} WHERE status='completed' GROUP BY location_id,payment_date
), refunds_by_day AS (
 SELECT p.location_id,r.refund_date AS report_date,SUM(r.amount) AS refund_amount
 FROM {refunds} r JOIN {payments} p ON r.payment_id=p.payment_id
 WHERE r.status='processed' GROUP BY p.location_id,r.refund_date
)
SELECT rr.location_id,rr.report_date,
 COALESCE(g.gross_amount,0)-COALESCE(r.refund_amount,0) AS expected_net_revenue,
 rr.reported_net_revenue,
 CASE WHEN rr.reported_net_revenue=COALESCE(g.gross_amount,0)-COALESCE(r.refund_amount,0) THEN 'PASS' ELSE 'FAIL' END AS status
FROM {reported_revenue} rr LEFT JOIN gross g ON rr.location_id=g.location_id AND rr.report_date=g.report_date
LEFT JOIN refunds_by_day r ON rr.location_id=r.location_id AND rr.report_date=r.report_date'''
BANK='''WITH component_totals AS (
 SELECT payout_id,SUM(signed_amount) AS expected_settlement FROM {payout_components} GROUP BY payout_id
), bank_totals AS (
 SELECT b.payout_id,SUM(b.amount) AS actual_settlement,
 SUM(CASE WHEN b.posting_date<=p.expected_bank_date THEN b.amount ELSE 0 END) AS received_by_deadline,
 MAX(b.posting_date) AS last_deposit_date,COUNT(*) AS bank_entry_count
 FROM {bank_entries} b JOIN {payouts} p ON b.payout_id=p.payout_id
 WHERE b.posting_date<={asof} GROUP BY b.payout_id
), amounts AS (
 SELECT p.payout_id,p.expected_bank_date,c.expected_settlement,
 COALESCE(b.actual_settlement,0) AS actual_settlement,COALESCE(b.received_by_deadline,0) AS received_by_deadline,
 b.last_deposit_date,COALESCE(b.bank_entry_count,0) AS bank_entry_count
 FROM {payouts} p JOIN component_totals c ON p.payout_id=c.payout_id LEFT JOIN bank_totals b ON p.payout_id=b.payout_id
 WHERE p.payout_date<={asof}
), statuses AS (
 SELECT *, CASE WHEN actual_settlement=expected_settlement THEN 'PASS'
 WHEN actual_settlement<expected_settlement AND {asof}<expected_bank_date THEN 'PENDING' ELSE 'FAIL' END AS amount_status,
 CASE WHEN received_by_deadline>=expected_settlement THEN 'PASS'
 WHEN {asof}<expected_bank_date THEN 'PENDING' ELSE 'FAIL' END AS timing_status
 FROM amounts
)
SELECT payout_id,expected_settlement,actual_settlement,received_by_deadline,last_deposit_date,bank_entry_count,amount_status,timing_status,
 CASE WHEN amount_status='FAIL' OR timing_status='FAIL' THEN 'FAIL'
 WHEN amount_status='PENDING' OR timing_status='PENDING' THEN 'PENDING' ELSE 'PASS' END AS overall_status
FROM statuses'''
# SQLite stores exact integer cents; BigQuery stores NUMERIC dollars. Shared SQL bodies, only syntax adaptation.
MONEY={'amount','processor_amount','signed_amount','reported_net_revenue'}
DATES={'payment_date','refund_date','payout_date','expected_bank_date','posting_date','report_date'}
def cents(v):return int(Decimal(str(v))*100)
conn=sqlite3.connect(':memory:');conn.row_factory=sqlite3.Row
for name,rows in T.items():
    if name=='reported_revenue':continue
    cols=list(rows[0]);conn.execute(f'CREATE TABLE {name} ('+','.join(c+(' INTEGER' if c in MONEY else ' TEXT') for c in cols)+')')
    conn.executemany(f'INSERT INTO {name} VALUES ('+','.join('?' for _ in cols)+')',[[cents(r[c]) if c in MONEY else r[c] for c in cols] for r in rows])
def fmt(sql,bq):
    vals={name:f'`{DS}.{name}`' if bq else name for name in T}; vals['asof']=f"DATE '{ASOF}'" if bq else f"'{ASOF}'"
    s=sql.format(**vals)
    return s if bq else s.replace('UNION DISTINCT','UNION').replace(' AS STRING)',' AS TEXT)').replace("DATE_ADD(p.payout_date, INTERVAL 2 DAY)","date(p.payout_date,'+2 day')").replace("DATE_SUB(p.payout_date, INTERVAL 1 DAY)","date(p.payout_date,'-1 day')")
conn.execute('CREATE TABLE reported_revenue AS '+fmt(REPORT,False))
for row in conn.execute('SELECT * FROM reported_revenue ORDER BY location_id,report_date'):
    r=dict(row);r['reported_net_revenue']=money(r['reported_net_revenue']);T['reported_revenue'].append(r)
# Python oracle for faulty report independent of actual SQL; same-day refunds cancel their reallocation.
alt=expected.copy(); pmap={r['payment_id']:r for r in T['payments']}
for r in T['refunds']:
    p=pmap[r['payment_id']]
    if p['vendor_id']=='VB' and r['status']=='processed':
        amt=cents(r['amount']);alt[p['location_id'],r['refund_date']]+=amt;alt[p['location_id'],p['payment_date']]-=amt
assert len(T['reported_revenue'])==len(expected)==200
for row in conn.execute(fmt(REV,False)):
    key=(row['location_id'],row['report_date']); exp=expected[key]; reported=alt[key];status='PASS' if exp==reported else 'FAIL'
    assert (row['expected_net_revenue'],row['reported_net_revenue'],row['status'])==(exp,reported,status),key
    G.append(dict(location_id=key[0],report_date=key[1],expected_net_revenue=money(exp),reported_net_revenue=money(reported),status=status))
bmap={r['payout_id']:r for r in B}
for row in conn.execute(fmt(BANK,False)):
    gold=bmap[row['payout_id']]
    for c in ['expected_settlement','actual_settlement','received_by_deadline']:assert row[c]==cents(gold[c]),(row['payout_id'],c)
    for c in ['amount_status','timing_status','overall_status','bank_entry_count']:assert row[c]==gold[c],(row['payout_id'],c)
    assert (row['last_deposit_date'] or '')==gold['last_deposit_date']
assert len(list(conn.execute(fmt(BANK,False))))==len(B)==100
# Checks expressed as queries returning violation counts, also run locally.
CHECKS={}
for t,key in [('payments','payment_id'),('refunds','refund_id'),('payouts','payout_id'),('payout_components','component_id'),('bank_entries','bank_entry_id')]:
    CHECKS[t+'_unique']=f'SELECT COUNT(*) FROM (SELECT {key} FROM {{{t}}} GROUP BY {key} HAVING COUNT(*)<>1 OR {key} IS NULL) q'
CHECKS.update({
 'report_grain_unique': 'SELECT COUNT(*) FROM (SELECT location_id,report_date FROM {reported_revenue} GROUP BY location_id,report_date HAVING COUNT(*)<>1) q',
 'report_coverage': '''WITH expected_dates AS (SELECT location_id,payment_date AS report_date FROM {payments} UNION DISTINCT SELECT p.location_id,r.refund_date FROM {refunds} r JOIN {payments} p ON r.payment_id=p.payment_id) SELECT COUNT(*) FROM (SELECT d.location_id,d.report_date FROM expected_dates d LEFT JOIN {reported_revenue} r ON d.location_id=r.location_id AND d.report_date=r.report_date WHERE r.location_id IS NULL UNION ALL SELECT r.location_id,r.report_date FROM {reported_revenue} r LEFT JOIN expected_dates d ON d.location_id=r.location_id AND d.report_date=r.report_date WHERE d.location_id IS NULL) q''',
 'refund_links_dates_amounts': '''SELECT COUNT(*) FROM {refunds} r LEFT JOIN {payments} p ON r.payment_id=p.payment_id WHERE p.payment_id IS NULL OR p.status<>'completed' OR r.refund_date<p.payment_date OR r.amount<=0''',
 'refund_amount_limit': '''SELECT COUNT(*) FROM (SELECT p.payment_id FROM {payments} p JOIN {refunds} r ON r.payment_id=p.payment_id WHERE r.status='processed' GROUP BY p.payment_id,p.amount HAVING SUM(r.amount)>p.amount) q''',
 'eligible_payment_coverage': '''SELECT COUNT(*) FROM (SELECT s.payment_id FROM {payments} s LEFT JOIN {payout_components} c ON c.component_type='payment' AND c.source_id=s.payment_id GROUP BY s.payment_id,s.status HAVING COUNT(c.component_id)<>CASE WHEN s.status='completed' THEN 1 ELSE 0 END) q''',
 'eligible_refund_coverage': '''SELECT COUNT(*) FROM (SELECT s.refund_id FROM {refunds} s LEFT JOIN {payout_components} c ON c.component_type='refund' AND c.source_id=s.refund_id GROUP BY s.refund_id,s.status HAVING COUNT(c.component_id)<>CASE WHEN s.status='processed' THEN 1 ELSE 0 END) q''',
 'component_payout_fk': '''SELECT COUNT(*) FROM {payout_components} c LEFT JOIN {payouts} p ON c.payout_id=p.payout_id WHERE p.payout_id IS NULL OR c.component_type NOT IN ('payment','refund','fee')''',
 'payment_component_matches_source': '''SELECT COUNT(*) FROM {payout_components} c JOIN {payouts} p ON c.payout_id=p.payout_id LEFT JOIN {payments} s ON c.source_id=s.payment_id WHERE c.component_type='payment' AND (s.payment_id IS NULL OR s.status<>'completed' OR c.signed_amount<>s.amount OR s.location_id<>p.location_id OR s.vendor_id<>p.vendor_id OR s.payment_date NOT BETWEEN DATE_SUB(p.payout_date, INTERVAL 1 DAY) AND p.payout_date)''',
 'refund_component_matches_source': '''SELECT COUNT(*) FROM {payout_components} c JOIN {payouts} p ON c.payout_id=p.payout_id LEFT JOIN {refunds} r ON c.source_id=r.refund_id LEFT JOIN {payments} s ON r.payment_id=s.payment_id WHERE c.component_type='refund' AND (r.refund_id IS NULL OR s.payment_id IS NULL OR r.status<>'processed' OR c.signed_amount<>-r.amount OR s.location_id<>p.location_id OR s.vendor_id<>p.vendor_id OR r.refund_date NOT BETWEEN DATE_SUB(p.payout_date, INTERVAL 1 DAY) AND p.payout_date)''',
 'fee_per_payout': '''SELECT COUNT(*) FROM (SELECT p.payout_id FROM {payouts} p LEFT JOIN {payout_components} c ON p.payout_id=c.payout_id AND c.component_type='fee' GROUP BY p.payout_id HAVING COUNT(c.component_id)<>1 OR SUM(c.signed_amount)<>{fee}) q''',
 'payout_total_matches': '''SELECT COUNT(*) FROM (SELECT p.payout_id FROM {payouts} p LEFT JOIN {payout_components} c ON p.payout_id=c.payout_id GROUP BY p.payout_id,p.processor_amount HAVING COUNT(c.component_id)=0 OR SUM(c.signed_amount)<>p.processor_amount) q''',
 'deadline_two_days': '''SELECT COUNT(*) FROM {payouts} p WHERE p.expected_bank_date<>DATE_ADD(p.payout_date, INTERVAL 2 DAY)''',
 'bank_links_dates_amounts': '''SELECT COUNT(*) FROM {bank_entries} b LEFT JOIN {payouts} p ON b.payout_id=p.payout_id WHERE p.payout_id IS NULL OR b.posting_date<p.payout_date OR b.posting_date>{asof} OR b.amount<=0 OR b.bank_reference<>p.processor_reference''',
 'source_payment_validity': '''SELECT COUNT(*) FROM {payments} WHERE amount<=0 OR status NOT IN ('completed','cancelled') OR vendor_id NOT IN ('VA','VB') OR payment_date>{asof}''',
 'refund_status_validity': '''SELECT COUNT(*) FROM {refunds} WHERE status NOT IN ('processed','pending') OR refund_date>{asof}''',
 'payout_positive_and_sent': '''SELECT COUNT(*) FROM {payouts} WHERE processor_amount<=0 OR status<>'sent' OR payout_date>{asof}''',
 'one_vendor_per_location': '''SELECT COUNT(*) FROM (SELECT location_id FROM {payments} GROUP BY location_id HAVING COUNT(DISTINCT vendor_id)<>1) q''',
})
for name,q in CHECKS.items():
    n=conn.execute(fmt(q.replace('{fee}','-200'),False)).fetchone()[0];assert n==0,(name,n)
# Reproducible output files
(ROOT/'data').mkdir(exist_ok=True); (ROOT/'evaluation_only').mkdir(exist_ok=True)
for t,rows in T.items():write_csv(ROOT/'data'/f'{t}.csv',rows)
write_csv(ROOT/'evaluation_only'/'expected_daily_revenue.csv',G);write_csv(ROOT/'evaluation_only'/'expected_payouts.csv',B)
def literal(c,v):
    if c in MONEY:return f"NUMERIC '{v}'"
    if c in DATES:return f"DATE '{v}'"
    return "'"+str(v).replace("'","''")+"'"
seed=['-- V3: replaces only the six V3 demo tables. Run after creating the V3 US dataset.']
for t in ['payments','refunds','payouts','payout_components','bank_entries']:
    rows=T[t]; seed.append(f'CREATE OR REPLACE TABLE `{DS}.{t}` AS\nSELECT * FROM UNNEST([\n'+',\n'.join('  STRUCT('+', '.join(f'{literal(c,v)} AS {c}' for c,v in row.items())+')' for row in rows)+'\n]);')
transformation=f'CREATE OR REPLACE TABLE `{DS}.reported_revenue` AS\n'+fmt(REPORT,True)+';\n'
(ROOT/'reporting_transformation.sql').write_text(transformation)
seed.append(transformation)
seed.append('\nUNION ALL\n'.join(f"SELECT '{t}' AS table_name,COUNT(*) AS row_count FROM `{DS}.{t}`" for t in T)+'\nORDER BY table_name;')
(ROOT/'01_seed_bigquery.sql').write_text('\n\n'.join(seed)+'\n')
fee_bq="NUMERIC '-2.00'"
(ROOT/'02_verify_link_integrity.sql').write_text(' -- All counts should be zero.\n'+'\nUNION ALL\n'.join(f"SELECT '{name}' AS check_name, ({fmt(q.replace('{fee}',fee_bq),True)}) AS violations" for name,q in CHECKS.items())+'\nORDER BY check_name;\n')
(ROOT/'evaluation_only'/'03_reference_daily_revenue.sql').write_text(fmt(REV,True)+'\nORDER BY location_id,report_date;\n')
(ROOT/'evaluation_only'/'04_reference_payouts.sql').write_text(fmt(BANK,True)+'\nORDER BY payout_id;\n')
# Gold comparison: actual SQL outputs vs independently computed Python values; mismatch count + missing/extra.
def gold_literal(rows,cols,moneycols,datecols,intcols):
    def val(c,v):
        if c in moneycols:return f"NUMERIC '{v}'"
        if c in datecols:return f"DATE '{v}'" if v else 'CAST(NULL AS DATE)'
        if c in intcols:return str(v)
        return f"'{v}'"
    return 'SELECT * FROM UNNEST([\n'+',\n'.join('STRUCT('+', '.join(f'{val(c,r[c])} AS {c}' for c in cols)+')' for r in rows)+'\n])'
for filename,sql,rows,keys,mc,dc,ic in [('05_verify_revenue_gold.sql',REV,G,['location_id','report_date'],['expected_net_revenue','reported_net_revenue'],['report_date'],[]),('06_verify_payout_gold.sql',BANK,B,['payout_id'],['expected_settlement','actual_settlement','received_by_deadline'],['last_deposit_date'],['bank_entry_count'])]:
    cols=[c for c in rows[0] if c!='case']; conditions=' OR '.join(f'a.{c} IS DISTINCT FROM g.{c}' for c in cols if c not in keys)
    query='WITH actual AS (\n'+fmt(sql,True)+'\n), gold AS (\n'+gold_literal(rows,cols,mc,dc,ic)+'\n)\nSELECT COUNT(*) AS compared_rows, COUNTIF(a.'+keys[0]+' IS NULL OR g.'+keys[0]+' IS NULL OR '+conditions+') AS mismatches\nFROM actual a FULL OUTER JOIN gold g ON '+' AND '.join(f'a.{k}=g.{k}' for k in keys)+';\n'
    (ROOT/'evaluation_only'/filename).write_text(query)
rc=Counter(r['status'] for r in G); bc=Counter(r['overall_status'] for r in B)
lines=['LOCAL VALIDATION (SQLite relational SQL, integer cents; no BigQuery execution)',str({t:len(rows) for t,rows in T.items()}),f'{len(CHECKS)} integrity checks: zero violations',f'{len(G)} daily revenue rows match independent Python oracle: {dict(rc)}',f'{len(B)} payout rows match independent Python oracle: {dict(bc)}',f'Amount statuses: {dict(Counter(r["amount_status"] for r in B))}',f'Timing statuses: {dict(Counter(r["timing_status"] for r in B))}',f'Multi-entry payout statuses: {dict(Counter(r["overall_status"] for r in B if r["bank_entry_count"]>1))}',f'Bank event modes: {dict(Counter(r["case"] for r in B))}']
assert rc=={'PASS':180,'FAIL':20};assert bc=={'PASS':86,'FAIL':12,'PENDING':2}
(ROOT/'local_validation.txt').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
