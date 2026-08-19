import pathlib

p = pathlib.Path("/app/core/cli.py")
c = p.read_text(encoding="utf-8")

if "ABTestFramework" not in c:
    c = c.replace(
        "from engines.automated_insights import AutomatedInsights",
        "from engines.automated_insights import AutomatedInsights\nfrom engines.ab_test_framework import ABTestFramework",
    )

    old = '''    insights_parser.add_argument("--json", action="store_true", help="Output as JSON")'''
    new = '''    insights_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # ab-test
    ab_parser = subparsers.add_parser("ab-test", help="A/B testing management")
    ab_parser.add_argument("action", choices=["create", "list", "start", "analyze", "complete"])
    ab_parser.add_argument("--id", type=str, help="Test ID")
    ab_parser.add_argument("--name", type=str, help="Test name")
    ab_parser.add_argument("--variants", type=str, help="Variants JSON")
    ab_parser.add_argument("--split", type=str, help="Traffic split JSON")
    ab_parser.add_argument("--scope", type=str, help="Scope JSON")
    ab_parser.add_argument("--metric", type=str, default="views", help="Winner metric")'''

    if old in c:
        c = c.replace(old, new, 1)

    old2 = '''        if args.json:
            # JSON формат
            analysis = insights.analyze(days=args.days)
            print(json.dumps(analysis, indent=2, default=str))
        else:
            # Текстовый формат
            report = insights.generate_report(days=args.days)
            print(report)'''

    new2 = '''        if args.json:
            # JSON формат
            analysis = insights.analyze(days=args.days)
            print(json.dumps(analysis, indent=2, default=str))
        else:
            # Текстовый формат
            report = insights.generate_report(days=args.days)
            print(report)
    
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
            print(json.dumps(result, indent=2, default=str))'''

    if old2 in c:
        c = c.replace(old2, new2, 1)

    p.write_text(c, encoding="utf-8")
    print("✅ CLI: ab-test added")
else:
    print("ℹ️ ab-test already in CLI")