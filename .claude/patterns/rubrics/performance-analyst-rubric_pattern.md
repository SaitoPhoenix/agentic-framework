# Performance Analyst Rubric

**Version**: 1.0  
**Domain**: System Performance and Optimization  
**Purpose**: Evaluate application performance, identify bottlenecks, and assess optimization opportunities

## Scoring Methodology

### Performance Grade Scale
- **A (90-100)**: Exceptional performance, highly optimized
- **B (80-89)**: Good performance, minor optimizations possible
- **C (70-79)**: Acceptable performance, noticeable improvements needed
- **D (60-69)**: Poor performance, significant optimization required
- **F (0-59)**: Unacceptable performance, critical issues present

### Weight Distribution
- Response Time: 25%
- Resource Utilization: 20%
- Scalability: 20%
- Database Performance: 15%
- Caching & Optimization: 10%
- Network Efficiency: 10%

## Evaluation Categories

### 1. Response Time (25 points)

#### Page Load Time (10 points)
| Score | Criteria | Metrics |
|-------|----------|---------|
| 9-10 | Excellent load times | <1s initial, <200ms subsequent |
| 7-8 | Good load times | 1-2s initial, 200-500ms subsequent |
| 5-6 | Acceptable load times | 2-3s initial, 500ms-1s subsequent |
| 3-4 | Slow load times | 3-5s initial, 1-2s subsequent |
| 0-2 | Unacceptable load times | >5s initial, >2s subsequent |

**Measure:**
- Time to First Byte (TTFB)
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Time to Interactive (TTI)
- Total Blocking Time (TBT)

#### API Response Time (8 points)
| Score | Criteria | Metrics |
|-------|----------|---------|
| 8 | Lightning fast | <50ms average |
| 6-7 | Fast responses | 50-200ms average |
| 4-5 | Acceptable | 200-500ms average |
| 2-3 | Slow | 500ms-1s average |
| 0-1 | Very slow | >1s average |

**Measure:**
- Average response time
- 95th percentile response time
- 99th percentile response time
- Timeout rate
- Error rate under load

#### Rendering Performance (7 points)
| Score | Criteria | Metrics |
|-------|----------|---------|
| 7 | Smooth rendering | 60 FPS, no jank |
| 5-6 | Good rendering | 50-60 FPS, minimal jank |
| 3-4 | Acceptable | 30-50 FPS, some jank |
| 1-2 | Poor rendering | <30 FPS, frequent jank |
| 0 | Unusable | Constant freezing |

**Measure:**
- Frames per second (FPS)
- JavaScript execution time
- Layout thrashing occurrences
- Paint and composite times
- Main thread blocking time

### 2. Resource Utilization (20 points)

#### CPU Usage (7 points)
| Score | Criteria | Load Condition |
|-------|----------|---------------|
| 7 | Minimal CPU usage | <20% under normal load |
| 5-6 | Low CPU usage | 20-40% under normal load |
| 3-4 | Moderate CPU usage | 40-60% under normal load |
| 1-2 | High CPU usage | 60-80% under normal load |
| 0 | Excessive CPU usage | >80% under normal load |

**Check for:**
- CPU spikes during operations
- Sustained high CPU usage
- Multi-core utilization
- Process/thread efficiency
- Background task impact

#### Memory Management (7 points)
| Score | Criteria | Metrics |
|-------|----------|---------|
| 7 | Excellent memory usage | No leaks, <100MB baseline |
| 5-6 | Good memory usage | Minor leaks, 100-250MB baseline |
| 3-4 | Acceptable | Some leaks, 250-500MB baseline |
| 1-2 | Poor memory usage | Significant leaks, 500MB-1GB |
| 0 | Critical memory issues | Severe leaks, >1GB |

**Check for:**
- Memory leaks over time
- Garbage collection frequency
- Heap size growth
- Object allocation rate
- Memory fragmentation

#### Disk I/O (6 points)
| Score | Criteria | Metrics |
|-------|----------|---------|
| 6 | Minimal disk I/O | <10 IOPS average |
| 4-5 | Low disk I/O | 10-50 IOPS average |
| 2-3 | Moderate disk I/O | 50-100 IOPS average |
| 1 | High disk I/O | 100-200 IOPS average |
| 0 | Excessive disk I/O | >200 IOPS average |

**Check for:**
- Read/write patterns
- Sequential vs random access
- File system cache utilization
- Temporary file usage
- Log file impact

### 3. Scalability (20 points)

#### Load Handling (8 points)
| Score | Criteria | Concurrent Users |
|-------|----------|-----------------|
| 8 | Excellent scalability | >10,000 concurrent |
| 6-7 | Good scalability | 5,000-10,000 concurrent |
| 4-5 | Moderate scalability | 1,000-5,000 concurrent |
| 2-3 | Limited scalability | 100-1,000 concurrent |
| 0-1 | Poor scalability | <100 concurrent |

**Test scenarios:**
- Gradual load increase
- Spike testing
- Sustained load testing
- Stress testing to failure
- Recovery testing

#### Horizontal Scaling (7 points)
| Score | Criteria |
|-------|----------|
| 7 | Perfect linear scaling |
| 5-6 | Near-linear scaling (>80% efficiency) |
| 3-4 | Moderate scaling (50-80% efficiency) |
| 1-2 | Poor scaling (<50% efficiency) |
| 0 | Cannot scale horizontally |

**Evaluate:**
- Load balancing effectiveness
- Session management
- State handling
- Database connection pooling
- Cache synchronization

#### Performance Degradation (5 points)
| Score | Criteria | Under 2x Load |
|-------|----------|---------------|
| 5 | No degradation | <10% slower |
| 4 | Minimal degradation | 10-25% slower |
| 3 | Acceptable degradation | 25-50% slower |
| 2 | Significant degradation | 50-100% slower |
| 0-1 | Severe degradation | >100% slower |

**Measure:**
- Response time under load
- Throughput reduction
- Error rate increase
- Queue depth growth
- Timeout frequency

### 4. Database Performance (15 points)

#### Query Optimization (6 points)
| Score | Criteria | Query Time |
|-------|----------|------------|
| 6 | All queries optimized | <10ms average |
| 4-5 | Most queries optimized | 10-50ms average |
| 2-3 | Some slow queries | 50-200ms average |
| 1 | Many slow queries | 200-500ms average |
| 0 | Critical query issues | >500ms average |

**Check for:**
- Index usage
- Query execution plans
- N+1 query problems
- Full table scans
- Join optimization

#### Connection Management (5 points)
| Score | Criteria |
|-------|----------|
| 5 | Optimal connection pooling |
| 4 | Good connection management |
| 3 | Adequate management |
| 2 | Poor connection handling |
| 0-1 | Connection leaks/exhaustion |

**Evaluate:**
- Connection pool size
- Connection reuse
- Idle connection handling
- Connection timeouts
- Dead connection detection

#### Data Access Patterns (4 points)
| Score | Criteria |
|-------|----------|
| 4 | Optimal access patterns |
| 3 | Good patterns, minor issues |
| 2 | Inefficient patterns |
| 1 | Poor patterns |
| 0 | Terrible patterns |

**Check for:**
- Batch operations usage
- Lazy loading implementation
- Eager loading where appropriate
- Pagination implementation
- Data locality

### 5. Caching & Optimization (10 points)

#### Cache Implementation (5 points)
| Score | Criteria | Hit Rate |
|-------|----------|----------|
| 5 | Excellent caching | >95% hit rate |
| 4 | Good caching | 85-95% hit rate |
| 3 | Moderate caching | 70-85% hit rate |
| 2 | Poor caching | 50-70% hit rate |
| 0-1 | Minimal/no caching | <50% hit rate |

**Evaluate:**
- Cache levels (L1, L2, CDN)
- Cache invalidation strategy
- Cache key design
- TTL configuration
- Cache warming

#### Code Optimization (5 points)
| Score | Criteria |
|-------|----------|
| 5 | Highly optimized algorithms |
| 4 | Well-optimized code |
| 3 | Some optimizations |
| 2 | Few optimizations |
| 0-1 | No optimization effort |

**Check for:**
- Algorithm complexity (Big O)
- Hot path optimization
- Loop optimization
- String concatenation efficiency
- Collection usage

### 6. Network Efficiency (10 points)

#### Bandwidth Usage (4 points)
| Score | Criteria |
|-------|----------|
| 4 | Minimal bandwidth usage |
| 3 | Efficient usage |
| 2 | Moderate efficiency |
| 1 | Inefficient usage |
| 0 | Excessive bandwidth usage |

**Measure:**
- Payload sizes
- Compression usage
- Unnecessary data transfer
- Chunked responses
- WebSocket efficiency

#### Request Optimization (3 points)
| Score | Criteria |
|-------|----------|
| 3 | Minimal requests, well-batched |
| 2 | Good request management |
| 1 | Many unnecessary requests |
| 0 | Excessive requests |

**Check for:**
- Request batching
- HTTP/2 usage
- Keep-alive connections
- Prefetching strategy
- Lazy loading

#### CDN & Static Assets (3 points)
| Score | Criteria |
|-------|----------|
| 3 | Optimal CDN usage |
| 2 | Good CDN usage |
| 1 | Limited CDN usage |
| 0 | No CDN usage |

**Evaluate:**
- Static asset caching
- CDN coverage
- Asset minification
- Bundle optimization
- Image optimization

## Performance Testing Requirements

### Load Testing Scenarios
1. **Baseline Test**: Normal expected load
2. **Stress Test**: 2-3x expected load
3. **Spike Test**: Sudden load increases
4. **Soak Test**: Extended duration testing
5. **Breakpoint Test**: Find system limits

### Metrics to Collect
- **Response Times**: Min, Max, Average, Median, 95th, 99th percentile
- **Throughput**: Requests per second, Transactions per second
- **Error Rates**: By type and endpoint
- **Resource Usage**: CPU, Memory, Disk, Network
- **Concurrency**: Active users, connections, threads

## Bottleneck Identification

### Common Bottlenecks
1. **Database**: Slow queries, lock contention, connection limits
2. **CPU**: Inefficient algorithms, excessive processing
3. **Memory**: Leaks, large objects, poor GC
4. **Network**: Latency, bandwidth, chattiness
5. **I/O**: Disk access, file operations, logging

### Analysis Tools
- **Profilers**: CPU, memory, I/O profiling
- **APM Tools**: Application Performance Monitoring
- **Database Tools**: Query analyzers, explain plans
- **Network Tools**: Protocol analyzers, trace tools
- **Browser Tools**: DevTools, Lighthouse

## Reporting Template

### Performance Summary
```
Overall Score: [Score]/100 ([Grade])

Key Metrics:
- Average Response Time: [X]ms
- 95th Percentile: [X]ms
- Throughput: [X] req/s
- Error Rate: [X]%
- CPU Usage: [X]%
- Memory Usage: [X]MB

Critical Issues:
1. [Issue description and impact]
2. [Issue description and impact]

Top Recommendations:
1. [Optimization with expected improvement]
2. [Optimization with expected improvement]
```

### Detailed Findings

#### Critical Performance Issues
| Issue | Location | Impact | Current | Target | Priority |
|-------|----------|--------|---------|--------|----------|
| Slow API | /api/search | 3s response | 3000ms | <500ms | Critical |
| Memory leak | UserService | OOM after 2h | 2GB growth/h | <100MB/h | High |

#### Optimization Opportunities
| Optimization | Effort | Impact | ROI |
|--------------|--------|--------|-----|
| Add DB indexes | Low | High | Excellent |
| Implement caching | Medium | High | Excellent |
| Code refactoring | High | Medium | Good |

## Performance Standards

### Minimum Acceptable Performance
- Page Load: <3 seconds
- API Response: <500ms average
- Error Rate: <1%
- Availability: >99.9%
- CPU Usage: <70% sustained
- Memory: No leaks

### Target Performance
- Page Load: <1 second
- API Response: <200ms average
- Error Rate: <0.1%
- Availability: >99.99%
- CPU Usage: <50% sustained
- Memory: Stable usage

## Optimization Recommendations

### Quick Wins (Implement First)
1. Enable compression (gzip/brotli)
2. Add appropriate indexes
3. Implement basic caching
4. Optimize images
5. Minify assets

### Medium-term Improvements
1. Implement CDN
2. Database query optimization
3. Code refactoring
4. Advanced caching strategies
5. Async processing

### Long-term Strategies
1. Architecture redesign
2. Microservices migration
3. Database sharding
4. Global distribution
5. Edge computing

---

*This rubric should be adapted based on specific application requirements and performance SLAs.*