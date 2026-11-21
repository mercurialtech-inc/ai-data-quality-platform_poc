from summary import summarize_results
from engine import execute_rules

def run_checks(transactions, rules):
   results = execute_rules(transactions, rules)
   final_summary = summarize_results(results)

   return {
      "results": results
      , "summary": final_summary
   }