from backend.app.api.v1.metrics import PrometheusMetrics

# Симулируем успешную работу
PrometheusMetrics.record_job("test_job", "success", 1.5)
PrometheusMetrics.record_post_published("telegram", "test_channel")
PrometheusMetrics.set_channels_active(3)
PrometheusMetrics.set_posts_in_queue(5)

print("✅ Test metrics recorded!")
print("  - amf_jobs_total{job_name='test_job', status='success'} = 1")
print("  - amf_posts_published_total{platform='telegram', channel='test_channel'} = 1")
print("  - amf_channels_active = 3")
print("  - amf_posts_in_queue = 5")