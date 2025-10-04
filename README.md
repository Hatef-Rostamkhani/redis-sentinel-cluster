# Redis Cluster with Docker Compose

این پروژه یک خوشه Redis با یک Master و دو Replica را با استفاده از Docker Compose راه‌اندازی می‌کند.

## 🏗️ معماری

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Redis Master  │    │  Redis Replica1 │    │  Redis Replica2 │
│   Port: 6379    │◄───┤   Port: 6380    │    │   Port: 6381    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Redis Commander │
                    │   Port: 8081    │
                    │   (Web UI)      │
                    └─────────────────┘
```

## 🚀 راه‌اندازی سریع

### Windows
```bash
# اجرای اسکریپت راه‌اندازی
start-redis-cluster.bat
```

### Linux/macOS
```bash
# اجرای اسکریپت راه‌اندازی
chmod +x start-redis-cluster.sh
./start-redis-cluster.sh
```

### راه‌اندازی دستی
```bash
# راه‌اندازی تمام سرویس‌ها
docker-compose up -d

# بررسی وضعیت سرویس‌ها
docker-compose ps

# مشاهده لاگ‌ها
docker-compose logs -f
```

## 🔧 پیکربندی

### پورت‌ها
- **Redis Master**: 6379
- **Redis Replica 1**: 6380
- **Redis Replica 2**: 6381
- **Redis Commander**: 8081

### رمزهای عبور
- **Master**: `redis_master_password_2024`
- **Replicas**: `redis_replica_password_2024`

### فایل‌های پیکربندی
- `config/redis-master.conf` - پیکربندی Master
- `config/redis-replica-1.conf` - پیکربندی Replica 1
- `config/redis-replica-2.conf` - پیکربندی Replica 2

## 🔐 ویژگی‌های امنیتی

### 1. احراز هویت
- تمام نودها با رمز عبور محافظت شده‌اند
- رمزهای عبور جداگانه برای Master و Replicas

### 2. شبکه‌ایزوله
- شبکه اختصاصی برای Redis (`redis-network`)
- محدودیت دسترسی به پورت‌های داخلی

### 3. پایداری داده‌ها
- AOF (Append Only File) فعال
- RDB snapshots منظم
- Volume های persistent برای داده‌ها

## 📊 مانیتورینگ

### Redis Commander
- دسترسی به رابط وب: http://localhost:8081
- مشاهده تمام نودها در یک رابط واحد
- امکان اجرای دستورات Redis

### Health Checks
- بررسی خودکار سلامت نودها
- راه‌اندازی خودکار در صورت خرابی
- وابستگی‌های صحیح بین سرویس‌ها

## 🛠️ دستورات مفید

### مدیریت سرویس‌ها
```bash
# راه‌اندازی
docker-compose up -d

# توقف
docker-compose down

# راه‌اندازی مجدد
docker-compose restart

# مشاهده وضعیت
docker-compose ps

# مشاهده لاگ‌ها
docker-compose logs -f [service-name]
```

### اتصال به Redis
```bash
# اتصال به Master
docker exec -it redis-master redis-cli -a redis_master_password_2024

# اتصال به Replica 1
docker exec -it redis-replica-1 redis-cli -a redis_replica_password_2024

# اتصال به Replica 2
docker exec -it redis-replica-2 redis-cli -a redis_replica_password_2024
```

### بررسی وضعیت Replication
```bash
# بررسی وضعیت Master
docker exec redis-master redis-cli -a redis_master_password_2024 info replication

# بررسی وضعیت Replicas
docker exec redis-replica-1 redis-cli -a redis_replica_password_2024 info replication
docker exec redis-replica-2 redis-cli -a redis_replica_password_2024 info replication
```

### تست عملکرد
```bash
# تست نوشتن در Master
docker exec redis-master redis-cli -a redis_master_password_2024 set test_key "Hello Redis"

# تست خواندن از Replica
docker exec redis-replica-1 redis-cli -a redis_replica_password_2024 get test_key
```

## 🔍 عیب‌یابی

### مشکلات رایج

#### 1. سرویس‌ها راه‌اندازی نمی‌شوند
```bash
# بررسی لاگ‌ها
docker-compose logs redis-master
docker-compose logs redis-replica-1
docker-compose logs redis-replica-2
```

#### 2. Replicas به Master متصل نمی‌شوند
```bash
# بررسی شبکه
docker network ls
docker network inspect test-docker_redis-network

# بررسی اتصال
docker exec redis-replica-1 ping redis-master
```

#### 3. مشکلات احراز هویت
```bash
# تست اتصال با رمز عبور
docker exec redis-master redis-cli -a redis_master_password_2024 ping
```

### لاگ‌ها
```bash
# مشاهده لاگ‌های زنده
docker-compose logs -f

# مشاهده لاگ‌های خاص
docker-compose logs -f redis-master
docker-compose logs -f redis-replica-1
```

## 📈 بهینه‌سازی

### تنظیمات حافظه
- `maxmemory`: 512MB برای هر نود
- `maxmemory-policy`: allkeys-lru

### تنظیمات Replication
- `repl-backlog-size`: 1MB
- `repl-timeout`: 60 ثانیه
- `repl-ping-replica-period`: 10 ثانیه

### تنظیمات Persistence
- AOF فعال با `appendfsync everysec`
- RDB snapshots منظم
- `auto-aof-rewrite-percentage`: 100%

## 🚨 نکات امنیتی

1. **تغییر رمزهای عبور**: رمزهای پیش‌فرض را در محیط تولید تغییر دهید
2. **فایروال**: دسترسی به پورت‌ها را محدود کنید
3. **SSL/TLS**: برای اتصالات خارجی از SSL استفاده کنید
4. **مانیتورینگ**: لاگ‌ها و عملکرد را به طور منظم بررسی کنید

## 📚 منابع بیشتر

- [Redis Documentation](https://redis.io/documentation)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Redis Replication](https://redis.io/topics/replication)
- [Redis Security](https://redis.io/topics/security)
