import pathlib

p = pathlib.Path("/app/core/cli.py")
c = p.read_text(encoding="utf-8")

# Добавляем импорт
if "from engines.performance_dashboard import PerformanceDashboard" not in c:
    c = c.replace(
        "from core.channel_manager import ChannelManager",
        "from core.channel_manager import ChannelManager\nfrom engines.performance_dashboard import PerformanceDashboard",
    )

# Добавляем subparser для performance-report
old = '''    # status
    subparsers.add_parser("status", help="Show system status")'''

new = '''    # status
    subparsers.add_parser("status", help="Show system status")
    
    # performance-report
    report_parser = subparsers.add_parser("performance-report", help="Generate performance report")
    report_parser.add_argument("--days", type=int, default=7, help="Period in days (default: 7)")
    report_parser.add_argument("--channel", type=str, help="Filter by channel name")
    report_parser.add_argument("--top", type=int, default=10, help="Number of top posts (default: 10)")'''

if old in c:
    c = c.replace(old, new, 1)

# Добавляем обработку команды
old2 = '''    elif args.command == "status":
        status = manager.get_status()
        print(json.dumps(status, indent=2, default=str))'''

new2 = '''    elif args.command == "status":
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
            print(report)'''

if old2 in c:
    c = c.replace(old2, new2, 1)

p.write_text(c, encoding="utf-8")
print("✅ CLI: performance-report added")