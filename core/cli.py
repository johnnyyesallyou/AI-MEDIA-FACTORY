"""CLI Tools - Sprint 35.

Command-line interface для управления automation.

Usage:
    python -m core.cli list-channels
    python -m core.cli enable-automation <channel_id> [interval_minutes]
    python -m core.cli disable-automation <channel_id>
    python -m core.cli status
"""
import sys
import json
import argparse

from core.channel_manager import ChannelManager
from engines.performance_dashboard import PerformanceDashboard
from engines.automated_insights import AutomatedInsights
from engines.ab_test_framework import ABTestFramework
from engines.content_optimization.auto_apply import OptimizationApplier
from engines.content_optimization.feedback_loop import FeedbackLoop
from core import alerts as alerts_module
from engines.content_optimization import HeadlineOptimizer, PostingTimeOptimizer


def main():
    parser = argparse.ArgumentParser(description="AI Media Factory CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list-channels
    subparsers.add_parser("list-channels", help="List all channels")
    
    # enable-automation
    enable_parser = subparsers.add_parser("enable-automation", help="Enable automation for channel")
    enable_parser.add_argument("channel_id", help="Channel ID")
    enable_parser.add_argument("--interval", type=int, default=30, help="Interval in minutes")
    
    # disable-automation
    disable_parser = subparsers.add_parser("disable-automation", help="Disable automation for channel")
    disable_parser.add_argument("channel_id", help="Channel ID")
    
    # status
    subparsers.add_parser("status", help="Show system status")
    
    # performance-report
    report_parser = subparsers.add_parser("performance-report", help="Generate performance report")
    report_parser.add_argument("--days", type=int, default=7, help="Period in days (default: 7)")
    report_parser.add_argument("--channel", type=str, help="Filter by channel name")
    report_parser.add_argument("--top", type=int, default=10, help="Number of top posts (default: 10)")
    
    # insights
    insights_parser = subparsers.add_parser("insights", help="Generate automated insights and recommendations")
    insights_parser.add_argument("--days", type=int, default=7, help="Period in days (default: 7)")
    insights_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # ab-test
    ab_parser = subparsers.add_parser("ab-test", help="A/B testing management")
    ab_parser.add_argument("action", choices=["create", "list", "start", "analyze", "complete"])
    ab_parser.add_argument("--id", type=str, help="Test ID")
    ab_parser.add_argument("--name", type=str, help="Test name")
    ab_parser.add_argument("--variants", type=str, help="Variants JSON")
    ab_parser.add_argument("--split", type=str, help="Traffic split JSON")
    ab_parser.add_argument("--scope", type=str, help="Scope JSON")
    ab_parser.add_argument("--metric", type=str, default="views", help="Winner metric")
    
    # alerts
    alerts_parser = subparsers.add_parser("alerts", help="Alerting management")
    alerts_parser.add_argument("action", choices=["test", "status"])
    
    # optimize
    optimize_parser = subparsers.add_parser("optimize", help="Optimization management")
    optimize_parser.add_argument("action", choices=["apply", "stats"])
    optimize_parser.add_argument("--channel-id", type=str, help="Channel ID (UUID) for optimization")
    
    # optimize-headline
    opt_hl = subparsers.add_parser("optimize-headline", help="Optimize headline")
    opt_hl.add_argument("headline", type=str, help="Headline to optimize")
    opt_hl.add_argument("--channel", type=str, help="Channel ID for context")
    
    # best-posting-time
    opt_time = subparsers.add_parser("best-posting-time", help="Get best posting time")
    opt_time.add_argument("--channel", type=str, help="Channel ID")
    opt_time.add_argument("--days", type=int, default=30, help="Analysis period")
    
    args = parser.parse_args()
    
    manager = ChannelManager()
    
    if args.command == "list-channels":
        channels = manager.list_channels()
        print(f"\nChannels ({len(channels)}):")
        for ch in channels:
            print(f"  [{ch['id'][:8]}] {ch['name']} ({ch['platform']})")
            print(f"           connected={ch['is_connected']}")
            if ch['scheduler']:
                sched = ch['scheduler']
                print(f"           automation: enabled={sched['enabled']}, interval={sched['interval_minutes']}m")
                print(f"           last_run: {sched['last_run']}, errors: {sched['error_count']}")
    
    elif args.command == "enable-automation":
        try:
            manager.enable_automation(args.channel_id, args.interval)
            print(f"✅ Automation enabled for {args.channel_id} (every {args.interval}m)")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == "disable-automation":
        try:
            manager.disable_automation(args.channel_id)
            print(f"✅ Automation disabled for {args.channel_id}")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    elif args.command == "status":
        status = manager.get_status()
        print(json.dumps(status, indent=2, default=str))
    
    elif args.command == "performance-report":
        dashboard = PerformanceDashboard()
        
        if args.channel:
            # Детальный отчёт по каналу
            details = dashboard.channel_details(args.channel, days=args.days)
            print(json.dumps(details, indent=2, default=str))
        else:
            # Полный отчёт
            report = dashboard.generate_report(days=args.days)
            print(report)
    
    elif args.command == "insights":
        insights = AutomatedInsights()
        
        if args.json:
            # JSON формат
            analysis = insights.analyze(days=args.days)
            print(json.dumps(analysis, indent=2, default=str))
        else:
            # Текстовый формат
            report = insights.generate_report(days=args.days)
            print(report)
    
    elif args.command == "optimize":
        if args.action == "apply":
            if not args.channel_id:
                print("Error: --channel-id required")
                return
            applier = OptimizationApplier()
            result = applier.run_full_optimization(args.channel_id)
            print(f"Optimization results for channel {args.channel_id}:")
            print(f"  Headline insights: {result['headline'].get('applied', 0)}")
            print(f"  Posting time: {result['posting_time'].get('applied', False)}")
            print(f"  AB winners: {result['ab_winners'].get('winners_applied', 0)}")
        else:  # stats
            loop = FeedbackLoop()
            stats = loop.get_feedback_stats()
            print("Feedback loop stats:")
            print(f"  Total metrics: {stats['total_metrics']}")
            print(f"  Posts with views: {stats['posts_with_views']}")
            print(f"  Engagement rate: {stats['engagement_rate']:.2%}")
            print(f"  Total views: {stats['total_views']}")
            print(f"  Total likes: {stats['total_likes']}")
    
    elif args.command == "alerts":
        if args.action == "test":
            a = alerts_module.Alert(
                key="manual_test",
                severity="warning",
                title="Test alert",
                body="Это тестовое уведомление системы алертов AI Media Factory.",
            )
            sent = alerts_module._notifier.send(a)
            print("Sent to Telegram" if sent else "Logged only (Telegram not configured)")
        else:
            alerts_list = alerts_module._evaluator.evaluate()
            print(f"Active alerts: {len(alerts_list)}")
            for a in alerts_list:
                print(f"  [{a.severity}] {a.title}")
    
    elif args.command == "ab-test":
        ab = ABTestFramework()
        
        if args.action == "create":
            test_id = ab.create_test(
                name=args.name or "Unnamed test",
                variants=json.loads(args.variants),
                traffic_split=json.loads(args.split),
                scope=json.loads(args.scope) if args.scope else {},
                winner_metric=args.metric,
            )
            print(f"✅ Test created: {test_id}")
        
        elif args.action == "list":
            for t in ab.list_tests():
                print(f"  [{t['id'][:8]}] {t['name']} | {t['status']} | metric={t['metric']} | variants={t['variants']}")
        
        elif args.action == "start":
            print("✅ Started" if ab.start_test(args.id) else "❌ Not found")
        
        elif args.action == "analyze":
            ab.update_results(args.id)
            result = ab.analyze(args.id)
            print(json.dumps(result, indent=2, default=str))
        
        elif args.action == "complete":
            result = ab.complete_test(args.id)
            print(json.dumps(result, indent=2, default=str))
    
    elif args.command == "optimize-headline":
        optimizer = HeadlineOptimizer()
        result = optimizer.optimize(args.headline, channel_id=args.channel)
        print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
    
    elif args.command == "best-posting-time":
        optimizer = PostingTimeOptimizer()
        result = optimizer.suggest_posting_time(channel_id=args.channel, days=args.days)
        print(json.dumps(result, indent=2, default=str))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()