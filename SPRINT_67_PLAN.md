"""
🎯 SPRINT 67: Performance Optimization & Production Hardening
==============================================================

Objective: Optimize performance bottlenecks and prepare for production deployment
Duration: ~2-3 weeks
Status: PLANNING

---

## 📊 CURRENT STATE (Post Sprint 66.4)

### Strengths:
- ✅ 64/64 unit tests passing
- ✅ Structured JSON logging
- ✅ SQLite + PostgreSQL support
- ✅ Zero technical debt in logging

### Bottlenecks Identified:
1. ❌ LLM generation: 300s timeout (too long)
2. ❌ Source fetching: No caching (repeated API calls)
3. ⚠️ Database: Connection pooling not optimized
4. ⚠️ API rate limiting: Missing (Pixabay, Ollama)
5. ⚠️ Channel processing: Sequential (not parallel)

---

## 🎯 SPRINT 67 GOALS

### Goal 1: LLM Performance (30% improvement target)
- **Current:** 300s timeout, blocking generation
- **Target:** 60-90s per generation (fallback to caching)
- **Approach:**
  - Profile LLM calls (log duration, token count)
  - Implement response caching
  - Add request queuing
  - Optimize prompt engineering

### Goal 2: Source Data Caching (50% improvement)
- **Current:** Manga/Anime fetched on every request
- **Target:** Cache with 24h TTL
- **Approach:**
  - Redis caching layer
  - Cache invalidation strategy
  - Fallback to DB on miss

### Goal 3: Database Optimization (40% improvement)
- **Current:** Pool size 20, max overflow 30
- **Target:** Intelligent pooling based on load
- **Approach:**
  - Profile connection usage
  - Implement connection pre-warming
  - Add query optimization

### Goal 4: Rate Limiting (API reliability)
- **Current:** None (can get blocked)
- **Target:** Sliding window rate limiting
- **Approach:**
  - Pixabay: 100 req/hour
  - Ollama: 10 concurrent requests
  - Telegram: Batch messages

### Goal 5: Parallel Processing (2-3x throughput)
- **Current:** Sequential channel updates
- **Target:** Process N channels in parallel
- **Approach:**
  - Worker pool architecture
  - Async task distribution
  - Load balancing

---

## 📋 SPRINT 67 TASKS

### Task 67.1: LLM Performance Profiling
**Files to create/modify:**
- `backend/engines/llm_profiler.py` - New
- `backend/engines/llm_generator.py` - Modify
- `backend/engines/llm_cache.py` - New

**Steps:**
1. Add timing instrumentation to LLM calls
   - Prompt building time
   - LLM generation time
   - Response parsing time

2. Create LLM response cache
   - Key: hash(channel_id + prompt + model)
   - Value: (response, timestamp, token_count)
   - TTL: 1 hour

3. Implement fallback mechanism
   - If LLM timeout > 120s, use cache
   - If no cache, use template-based generation
   - Log all fallbacks for analysis

**Expected Result:**
```
Before: 300s median, 500s p99
After: 45s median (cached), 120s p99 (LLM)
Improvement: 87% faster (with caching)
```

### Task 67.2: Source Data Caching
**Files to create/modify:**
- `core/cache_layer.py` - New
- `engines/source_registry.py` - Modify
- `engines/manga_engine.py` - Modify
- `engines/anime_engine.py` - Modify

**Steps:**
1. Create cache abstraction
   - Memory cache for local dev
   - Redis cache for production
   - Fallback to DB

2. Cache manga/anime sources
   - Key: (source_type, query, language)
   - TTL: 24 hours
   - Size limit: 10k entries

3. Implement cache invalidation
   - Manual refresh endpoint
   - Periodic validation (every 6h)
   - On-demand fetch for new titles

**Expected Result:**
```
Before: 2s per source fetch (Remanga API)
After: 50ms (cache hit)
Improvement: 97% faster for repeated queries
```

### Task 67.3: Database Connection Optimization
**Files to create/modify:**
- `core/database.py` - Modify
- `core/connection_pool.py` - New

**Steps:**
1. Profile connection usage
   - Monitor pool size
   - Track timeout errors
   - Measure query duration

2. Implement dynamic pooling
   ```python
   class DynamicConnectionPool:
       def __init__(self, min=5, max=20, optimal=15):
           self.min_size = min
           self.max_size = max
           self.optimal = optimal
           
       def adjust_pool_size(self, current_load):
           # Scale pool based on actual demand
           pass
   ```

3. Add query optimization
   - Index analysis
   - N+1 query detection
   - Slow query logging

**Expected Result:**
```
Before: 20 conn pool, 30s max overflow timeout
After: Dynamic 5-15 conn pool, no timeouts
Improvement: 40% less memory, faster cleanup
```

### Task 67.4: Rate Limiting Implementation
**Files to create/modify:**
- `backend/core/rate_limiter.py` - New
- `engines/video_manager.py` - Modify (Pixabay)
- `engines/llm_generator.py` - Modify (Ollama)
- `engines/telegram_publisher.py` - Modify

**Steps:**
1. Create sliding window rate limiter
   ```python
   class RateLimiter:
       def __init__(self, max_requests=100, window_seconds=3600):
           self.max_requests = max_requests
           self.window_seconds = window_seconds
       
       async def acquire(self, key):
           # Sliding window implementation
           pass
   ```

2. Apply to external APIs
   - Pixabay: 100 req/hour
   - Ollama: 10 concurrent
   - Telegram: 30 msg/sec

3. Add backoff strategy
   - Exponential backoff on 429
   - Circuit breaker on repeated failures

**Expected Result:**
```
Before: Occasional 429 rate limit errors
After: 0 rate limit errors, queued requests
Improvement: 100% reliability
```

### Task 67.5: Parallel Channel Processing
**Files to create/modify:**
- `backend/automation/worker_pool.py` - New
- `backend/automation/scheduler.py` - Modify

**Steps:**
1. Create worker pool
   ```python
   class ChannelWorkerPool:
       def __init__(self, num_workers=4):
           self.workers = [Worker(i) for i in range(num_workers)]
       
       async def process_channels(self, channel_ids):
           # Distribute work across workers
           pass
   ```

2. Implement load balancing
   - Round-robin distribution
   - Monitor worker queue depth
   - Dynamic worker scaling

3. Add sync/coordination
   - Shared state management
   - Atomic updates to DB
   - Deadlock prevention

**Expected Result:**
```
Before: 1 channel at a time, 5m total for 5 channels
After: 4 channels in parallel, 1.5m total
Improvement: 3.3x throughput increase
```

### Task 67.6: Production Docker Compose Setup
**Files to create/modify:**
- `docker-compose.prod.yml` - New
- `.env.production` - New
- `nginx.conf` - New

**Content:**
```yaml
version: '3.8'
services:
  backend:
    image: ai-media-factory:latest
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/ai_media_factory
      - REDIS_URL=redis://redis:6379/0
      - APP_ENV=production
    depends_on:
      - db
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ai_media_factory
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
  
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - MODELS=gemma2:9b
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
  ollama_data:
```

**Expected Result:**
- Production-ready deployment
- Auto health checks
- Data persistence
- SSL/TLS support

### Task 67.7: Performance Benchmarking
**Files to create/modify:**
- `tests/performance/benchmark.py` - New
- `tests/performance/load_test.py` - New

**Benchmarks:**
1. LLM generation: target < 120s
2. Source fetch: target < 500ms (cache) / < 2s (API)
3. Channel processing: target < 5s per channel
4. API throughput: target 100+ req/s

**Load Test Scenarios:**
1. Concurrent channels (10, 50, 100)
2. Concurrent users (10, 100, 1000)
3. Mixed workloads (read/write ratio 80/20)

---

## 📊 SUCCESS CRITERIA

| Metric | Before | Target | Status |
|--------|--------|--------|--------|
| LLM generation | 300s p99 | 120s p99 | ⏳ |
| Source fetch (cached) | 2s | 50ms | ⏳ |
| Channel processing | 5s sequential | 2s parallel | ⏳ |
| DB connection timeouts | Frequent | 0 | ⏳ |
| API rate limit errors | Occasional | 0 | ⏳ |
| API throughput | 50 req/s | 100+ req/s | ⏳ |
| Memory usage | ~500MB | ~300MB | ⏳ |
| Test coverage | 64/64 (unit) | 70+ (integration) | ⏳ |

---

## 🚀 DEPLOYMENT STRATEGY

### Phase 1: Development (Week 1)
- Implement profiling infrastructure
- Create caching layer
- Local performance testing

### Phase 2: Staging (Week 2)
- Deploy to staging environment
- Run load tests
- Performance validation

### Phase 3: Production (Week 3)
- Gradual rollout (10% → 50% → 100%)
- Monitor metrics
- Rollback plan ready

---

## ⚠️ RISKS & MITIGATIONS

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Cache invalidation bugs | Data stale | Validation layer, TTL override |
| Worker pool deadlocks | System hang | Timeout, circuit breaker |
| Rate limiter too strict | Dropped requests | Adaptive thresholds |
| DB pool exhaustion | Connection errors | Monitoring, alerts |
| LLM service down | No generation | Fallback to templates |

---

## 📈 EXPECTED OUTCOMES

After Sprint 67 completion:
- ✅ 30-40% faster LLM generation (with caching)
- ✅ 97% faster source fetching (with caching)
- ✅ 3-4x higher channel throughput (parallel processing)
- ✅ 0 rate limit errors (with rate limiting)
- ✅ Optimized database connections
- ✅ Production-ready Docker setup
- ✅ Comprehensive performance benchmarks

---

## 📝 NOTES

### LLM Optimization Priority:
1. Most impactful: Response caching (300s → 50ms on hit)
2. Second: Prompt optimization (reduce tokens)
3. Third: Model optimization (use faster model for simple tasks)

### Caching Strategy:
- Multi-tier: Memory (hot) → Redis (warm) → DB (cold)
- TTL: Sources 24h, LLM responses 1h, user data 5m
- Invalidation: Manual + time-based + event-based

### Rate Limiting Approach:
- Use Redis for distributed rate limiting
- Sliding window algorithm (better than token bucket)
- Graceful degradation (queue, not reject)

---

## 🎓 TECHNICAL DECISIONS

### Why Parallel Processing:
- Channels are independent
- No cross-channel dependencies
- Perfect for worker pool pattern

### Why Redis over in-memory:
- Distributed system ready
- Shared cache across workers
- Persistent across restarts

### Why RateLimit not Queue:
- Queue adds latency
- Rate limiting with backoff = best UX
- Combines throughput + reliability

---

**Sprint 67 Plan Ready** ✅
Next: Start with Task 67.1 (LLM Profiling)
"""
