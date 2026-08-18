import pathlib

p = pathlib.Path("/app/core/cli.py")
c = p.read_text(encoding="utf-8")

# Добавляем импорт
if "from engines.automated_insights import AutomatedInsights" not in c:
    c = c.replace(
        "from engines.performance_dashboard import PerformanceDashboard",
        "from engines.performance_dashboard import PerformanceDashboard\nfrom engines.automated_insights import AutomatedInsights",
    )

# Добавляем subparser
old = '''    # performance-report
    report_parser = subparsers.add_parser("performance-report", help="Generate performance report")
    report_parser.add_argument("--days", type=int, default=7, help="Period in days (default: 7)")
    report_parser.add_argument("--channel", type=str, help="Filter by channel name")
    report_parser.add_argument("--top", type=int, default=10, help="Number of top posts (default: 10)")'''

new = '''    # performance-report
    report_parser = subparsers.add_parser("performance-report", help="Generate performance report")
    report_parser.add_argument("--days", type=int, default=7, help="Period in days (default: 7)")
    report_parser.add_argument("--channel", type=str, help="Filter by channel name")
    report_parser.add_argument("--top", type=int, default=10, help="Number of top posts (default: 10)")
    
    # insights
    insights_parser = subparsers.add_parser("insights", help="Generate automated insights and recommendations")
    insights_parser.add_argument("--days", type=int, default=7, help="Period in days (default: 7)")
    insights_parser.add_argument("--json", action="store_true", help="Output as JSON")'''

if old in c:
    c = c.replace(old, new, 1)

# Добавляем обработку
old2 = '''    elif args.command == "performance-report":
        dashboard = PerformanceDashboard()
        
        if args.channel:
            # Детальный отчёт по каналу
            details = dashboard.channel_details(args.channel, days=args.days)
            print(json.dumps(details, indent=2, default=str))
        else:
            # Полный отчёт
            report = dashboard.generate_report(days=args.days)
            print(report)'''

new2 = '''    elif args.command == "performance-report":
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
            print(report)'''

if old2 in c:
    c = c.replace(old2, new2, 1)

p.write_text(c, encoding="utf-8")
print("✅ CLI: insights added")