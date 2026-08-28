import pathlib

p = pathlib.Path("backend/automation/scheduler.py")
c = p.read_text(encoding="utf-8")

job_block = '''        # Sprint 58: Analytics Collector (every hour)
        self.scheduler.add_job(
            func=self.run_analytics_collection,
            trigger="interval",
            hours=1,
            id="analytics_collector_job",
            name="Analytics Collector (post metrics + learnings)",
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )
        logger.info("Added analytics collector job (every hour)")

'''

if "analytics_collector_job" not in c:
    marker = '        logger.info("Added manga pipeline job (every 30 minutes)")\n\n'
    if marker in c:
        c = c.replace(marker, marker + job_block)
        print("[OK] analytics job inserted")
    else:
        print("[!] marker not found for job insertion")
else:
    print("[i] analytics job already exists")

method_block = '''
    async def run_analytics_collection(self):
        """Sprint 58: hourly analytics collection for active connected channels."""
        db = SessionLocal()
        try:
            from engines.analytics import AnalyticsCollector

            channels = (
                db.query(ChannelORM)
                .filter(
                    ChannelORM.is_active == True,
                    ChannelORM.is_connected == True,
                )
                .all()
            )

            collector = AnalyticsCollector(db)

            logger.info("Analytics collection started for %d channels", len(channels))

            for channel in channels:
                try:
                    await collector.collect_metrics_for_channel(channel.id)
                except Exception as e:
                    logger.exception("Analytics collection failed for channel=%s: %s", channel.id, e)

            logger.info("Analytics collection finished")
        finally:
            db.close()

'''

if "async def run_analytics_collection" not in c:
    marker = "    async def stop(self):\n"
    if marker in c:
        c = c.replace(marker, method_block + marker)
        print("[OK] run_analytics_collection method inserted")
    else:
        print("[!] marker not found for method insertion")
else:
    print("[i] method already exists")

p.write_text(c, encoding="utf-8")