import pathlib

p = pathlib.Path("/app/core/cli.py")
c = p.read_text(encoding="utf-8")

if "alerts" not in c:
    c = c.replace(
        "from engines.ab_test_framework import ABTestFramework",
        "from engines.ab_test_framework import ABTestFramework\nfrom core import alerts as alerts_module",
        1,
    )

    old = '    ab_parser.add_argument("--metric", type=str, default="views", help="Winner metric")'
    new = old + '''
    
    # alerts
    alerts_parser = subparsers.add_parser("alerts", help="Alerting management")
    alerts_parser.add_argument("action", choices=["test", "status"])'''
    c = c.replace(old, new, 1)

    old2 = '''    elif args.command == "ab-test":'''
    new2 = '''    elif args.command == "alerts":
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
    
    elif args.command == "ab-test":'''
    c = c.replace(old2, new2, 1)

    p.write_text(c, encoding="utf-8")
    print("[OK] CLI alerts added")
else:
    print("[i] already present")