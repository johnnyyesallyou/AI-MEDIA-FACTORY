import pathlib

p = pathlib.Path("/app/core/cli.py")
c = p.read_text(encoding="utf-8")

if "optimize" not in c or "auto_apply" not in c:
    c = c.replace(
        "from engines.ab_test_framework import ABTestFramework",
        "from engines.ab_test_framework import ABTestFramework\nfrom engines.content_optimization.auto_apply import OptimizationApplier\nfrom engines.content_optimization.feedback_loop import FeedbackLoop",
        1,
    )

    old = '    alerts_parser.add_argument("action", choices=["test", "status"])'
    new = old + '''
    
    # optimize
    optimize_parser = subparsers.add_parser("optimize", help="Optimization management")
    optimize_parser.add_argument("action", choices=["apply", "stats"])
    optimize_parser.add_argument("--channel-id", type=int, help="Channel ID for optimization")'''
    c = c.replace(old, new, 1)

    old2 = '''    elif args.command == "alerts":'''
    new2 = '''    elif args.command == "optimize":
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
            print(f"Feedback loop stats:")
            print(f"  Total posts: {stats['total_posts']}")
            print(f"  Posts with engagement: {stats['posts_with_engagement']}")
            print(f"  Engagement rate: {stats['engagement_rate']:.2%}")
    
    elif args.command == "alerts":'''
    c = c.replace(old2, new2, 1)

    p.write_text(c, encoding="utf-8")
    print("[OK] CLI optimize added")
else:
    print("[i] already present")