import pathlib

p = pathlib.Path("/app/core/cli.py")
c = p.read_text(encoding="utf-8")

# 1. Импорт
if "HeadlineOptimizer" not in c:
    c = c.replace(
        "from engines.ab_test_framework import ABTestFramework",
        "from engines.ab_test_framework import ABTestFramework\nfrom engines.content_optimization import HeadlineOptimizer, PostingTimeOptimizer",
    )

    # 2. Subparsers
    old = '''    ab_parser.add_argument("--metric", type=str, default="views", help="Winner metric")'''
    new = '''    ab_parser.add_argument("--metric", type=str, default="views", help="Winner metric")
    
    # optimize-headline
    opt_hl = subparsers.add_parser("optimize-headline", help="Optimize headline")
    opt_hl.add_argument("headline", type=str, help="Headline to optimize")
    opt_hl.add_argument("--channel", type=str, help="Channel ID for context")
    
    # best-posting-time
    opt_time = subparsers.add_parser("best-posting-time", help="Get best posting time")
    opt_time.add_argument("--channel", type=str, help="Channel ID")
    opt_time.add_argument("--days", type=int, default=30, help="Analysis period")'''

    if old in c:
        c = c.replace(old, new, 1)

    # 3. Обработка команд
    old2 = '''        elif args.action == "complete":
            result = ab.complete_test(args.id)
            print(json.dumps(result, indent=2, default=str))'''

    new2 = '''        elif args.action == "complete":
            result = ab.complete_test(args.id)
            print(json.dumps(result, indent=2, default=str))
    
    elif args.command == "optimize-headline":
        optimizer = HeadlineOptimizer()
        result = optimizer.optimize(args.headline, channel_id=args.channel)
        print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
    
    elif args.command == "best-posting-time":
        optimizer = PostingTimeOptimizer()
        result = optimizer.suggest_posting_time(channel_id=args.channel, days=args.days)
        print(json.dumps(result, indent=2, default=str))'''

    if old2 in c:
        c = c.replace(old2, new2, 1)

    p.write_text(c, encoding="utf-8")
    print("✅ CLI: optimize-headline + best-posting-time added")
else:
    print("ℹ️ Content optimization already in CLI")