"""CLI for single-query, batch evaluation, replay, and registry inspection."""
import argparse, json
from graph import run_query
from tools.registry import list_tools
from evaluation.runner import run_evaluation
from observability.session_capture import get_capture

def main():
    p = argparse.ArgumentParser(description="Squad-4 IT Helpdesk multi-agent demo")
    sub = p.add_subparsers(dest="command", required=True)
    q = sub.add_parser("ask", help="Run one helpdesk query"); q.add_argument("query"); q.add_argument("--user-id", default="demo-user-001")
    sub.add_parser("eval", help="Run golden-set evaluation")
    sub.add_parser("tools", help="List registered tools")
    r = sub.add_parser("replay", help="Display captured session"); r.add_argument("session_id")
    args = p.parse_args()
    if args.command == "ask": print(json.dumps(run_query(args.query, args.user_id), indent=2, ensure_ascii=False))
    elif args.command == "eval": print(json.dumps(run_evaluation(), indent=2))
    elif args.command == "tools": print(json.dumps(list_tools(), indent=2))
    elif args.command == "replay":
        item = get_capture(args.session_id)
        print(json.dumps(item, indent=2) if item else f"No capture found for {args.session_id}")
if __name__ == "__main__": main()
