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
         ┌─────────────────────────────────────────────────┐
         │              Sentinel Cluster                   │
         │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
         │  │ Sentinel 1  │ │ Sentinel 2  │ │ Sentinel 3  │ │
         │  │ Port: 26379 │ │ Port: 26380 │ │ Port: 26381 │ │
         │  └─────────────┘ └─────────────┘ └─────────────┘ │
         └─────────────────────────────────────────────────┘
```

## 🚀 راه‌اندازی سریع

### Windows
```bash
# اجرای اسکریپت راه‌اندازی (راه‌اندازی دستی برای Windows توصیه می‌شود)
docker-compose up -d
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
- **Redis Sentinel 1**: 26379
- **Redis Sentinel 2**: 26380
- **Redis Sentinel 3**: 26381
- **RedisInsight**: 8001 (رابط وب برای مدیریت Redis)

### رمزهای عبور
- **Master**: `redis_master_password_2024` (قابل تنظیم از طریق Docker secrets)
- **Replicas**: `redis_replica_password_2024` (قابل تنظیم از طریق Docker secrets)
- **Sentinels**: `redis_sentinel_password_2024` (قابل تنظیم از طریق Docker secrets)

### فایل‌های پیکربندی
- `config/redis-master.conf` - پیکربندی Master
- `config/redis-replica-1.conf` - پیکربندی Replica 1
- `config/redis-replica-2.conf` - پیکربندی Replica 2
- `config/redis-sentinel-1.conf` - پیکربندی Sentinel 1
- `config/redis-sentinel-2.conf` - پیکربندی Sentinel 2
- `config/redis-sentinel-3.conf` - پیکربندی Sentinel 3

### اسکریپت‌های راه‌اندازی
- `scripts/init-redis-master.sh` - اسکریپت راه‌اندازی Master
- `scripts/init-redis-replica.sh` - اسکریپت راه‌اندازی Replica
- `scripts/init-redis-sentinel.sh` - اسکریپت راه‌اندازی Sentinel

### Docker Secrets
- `secrets/redis_master_password` - فایل رمز Master
- `secrets/redis_sentinel_password` - فایل رمز Sentinel

## 🔐 ویژگی‌های امنیتی

### 1. پیاده‌سازی Docker Secrets
- رمزهای عبور در فایل‌های Docker secrets ذخیره می‌شوند
- عدم وجود رمزهای عبور سخت‌کد شده در پیکربندی
- مدیریت امن رمزهای عبور مطابق با بهترین روش‌های Docker
- امکان تغییر رمزهای عبور بدون بازسازی کانتینرها

### 2. احراز هویت
- تمام نودها با رمزهای عبور قوی محافظت شده‌اند
- رمزهای عبور جداگانه برای Master و Replicas
- حالت محافظت شده فعال
- بارگذاری پویای رمزهای عبور از secrets

### 3. شبکه‌ایزوله
- شبکه اختصاصی برای Redis (`redis-network`)
- محدودیت دسترسی به پورت‌های داخلی با IP های ثابت
- شبکه bridge برای ارتباط امن بین کانتینرها
- زیرشبکه جدا شده (192.168.55.0/24)

### 4. پایداری داده‌ها
- AOF (Append Only File) فعال
- RDB snapshots منظم
- Volume های persistent برای ذخیره داده‌ها
- جداسازی دایرکتوری داده برای هر نود

### 5. دسترسی بالا با Sentinel
- سه نود Sentinel برای تصمیم‌گیری مبتنی بر quorum
- قابلیت failover خودکار
- مانیتورینگ Master و بررسی سلامت
- Service discovery برای اپلیکیشن‌ها
- تنظیمات timeout و down-after-milliseconds

## 📊 مانیتورینگ

### Health Checks
- بررسی خودکار سلامت نودها
- راه‌اندازی خودکار در صورت خرابی
- وابستگی‌های صحیح بین سرویس‌ها
- بررسی‌های سلامت آگاه از رمز عبور با استفاده از Docker secrets

### RedisInsight رابط وب
- رابط مدیریت Redis مبتنی بر وب مدرن
- دسترسی از طریق http://localhost:8001
- اتصالات پایگاه داده از پیش پیکربندی شده
- مانیتورینگ و مدیریت بلادرنگ
- رابط پرس‌وجو و تحلیل عملکرد

### تست‌های جامع عملکرد
```bash
# اجرای تست‌های Redis cluster
python3 test-redis-cluster.py

# اجرای تست‌های Sentinel cluster
python3 test-sentinel-simple.py

# اجرای نمایش failover
./demo-sentinel-failover.sh
```

مجموعه تست‌ها شامل:
- ✅ تست اتصال
- ✅ بررسی وضعیت replication
- ✅ تست عملیات خواندن/نوشتن
- ✅ تأیید رفتار read-only در replicas
- ✅ اتصال و مانیتورینگ Sentinel
- ✅ کشف Master/Slave توسط Sentinel
- ✅ ارتباط بین Sentinel ها

## 🛠️ دستورات مفید

### اسکریپت‌های نمایشی و تست
```bash
# اجرای نمایش failover Sentinel
./demo-sentinel-failover.sh

# تست عملکرد Redis cluster
python3 test-redis-cluster.py

# تست مانیتورینگ و HA Sentinel
python3 test-sentinel-simple.py
```

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

# اتصال به Sentinel 1
docker exec -it redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024

# اتصال به Sentinel 2
docker exec -it redis-sentinel-2 redis-cli -p 26379 -a redis_sentinel_password_2024

# اتصال به Sentinel 3
docker exec -it redis-sentinel-3 redis-cli -p 26379 -a redis_sentinel_password_2024
```

### اتصال خارجی
```bash
# اتصال به Master از host
redis-cli -h localhost -p 6379 -a redis_master_password_2024

# اتصال به Replica 1 از host
redis-cli -h localhost -p 6380 -a redis_replica_password_2024

# اتصال به Replica 2 از host
redis-cli -h localhost -p 6381 -a redis_replica_password_2024

# اتصال به Sentinel 1 از host
redis-cli -h localhost -p 26379 -a redis_sentinel_password_2024

# اتصال به Sentinel 2 از host
redis-cli -h localhost -p 26380 -a redis_sentinel_password_2024

# اتصال به Sentinel 3 از host
redis-cli -h localhost -p 26381 -a redis_sentinel_password_2024
```

### بررسی وضعیت Replication
```bash
# بررسی وضعیت Master
docker exec redis-master redis-cli -a redis_master_password_2024 info replication

# بررسی وضعیت Replicas
docker exec redis-replica-1 redis-cli -a redis_replica_password_2024 info replication
docker exec redis-replica-2 redis-cli -a redis_replica_password_2024 info replication

# بررسی وضعیت مانیتورینگ Sentinel
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel masters

# بررسی slaves مانیتور شده توسط Sentinel
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel slaves mymaster

# بررسی سایر Sentinel ها در cluster
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel sentinels mymaster
```

### تست عملکرد
```bash
# تست نوشتن در Master
docker exec redis-master redis-cli -a redis_master_password_2024 set test_key "Hello Redis"

# تست خواندن از Replica 1
docker exec redis-replica-1 redis-cli -a redis_replica_password_2024 get test_key

# تست خواندن از Replica 2
docker exec redis-replica-2 redis-cli -a redis_replica_password_2024 get test_key

# دریافت Master فعلی از طریق Sentinel
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel get-master-addr-by-name mymaster

# بررسی اطلاعات Sentinel
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 info sentinel
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

#### 4. تداخل پورت‌ها
```bash
# بررسی استفاده از پورت‌ها
netstat -tulpn | grep :6379
netstat -tulpn | grep :6380
netstat -tulpn | grep :6381
netstat -tulpn | grep :26379
netstat -tulpn | grep :26380
netstat -tulpn | grep :26381
```

#### 5. مشکلات Sentinel
```bash
# بررسی لاگ‌های Sentinel
docker-compose logs redis-sentinel-1
docker-compose logs redis-sentinel-2
docker-compose logs redis-sentinel-3

# تست اتصال Sentinel
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 ping

# بررسی پیکربندی Sentinel
docker exec redis-sentinel-1 redis-cli -p 26379 -a redis_sentinel_password_2024 sentinel masters
```

### لاگ‌ها
```bash
# مشاهده لاگ‌های زنده
docker-compose logs -f

# مشاهده لاگ‌های خاص
docker-compose logs -f redis-master
docker-compose logs -f redis-replica-1
docker-compose logs -f redis-sentinel-1
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

## 🧪 تست‌ها

پروژه شامل مجموعه تست‌های جامع و اسکریپت‌های نمایشی است که موارد زیر را تأیید می‌کند:

### تست‌های Redis Cluster (`test-redis-cluster.py`)
1. **تست اتصال**: بررسی دسترسی به تمام نودها
2. **وضعیت Replication**: تأیید روابط master-replica
3. **عملیات داده**: تست عملیات خواندن/نوشتن و replication
4. **امنیت**: تأیید رفتار read-only در replicas

### تست‌های Sentinel Cluster (`test-sentinel-simple.py`)
1. **اتصال Sentinel**: تأیید دسترسی به تمام نودهای Sentinel
2. **مانیتورینگ Master**: تأیید مانیتورینگ Master توسط Sentinel
3. **مانیتورینگ Slave**: تأیید کشف Replica ها توسط Sentinel
4. **ارتباط Cluster**: تست ارتباط بین Sentinel ها
5. **اتصال Master**: اطمینان از کارکرد اتصال مستقیم به Master

### نمایش Failover (`demo-sentinel-failover.sh`)
1. **نمایش زنده Failover**: نمایش فرآیند failover Sentinel در زمان واقعی
2. **ارتقای Master**: نمایش ارتقای replica به master
3. **بازیابی سرویس**: تست بازیابی خودکار سرویس
4. **مانیتورینگ سلامت**: تأیید سلامت cluster در طول failover

اجرای تست‌ها:
```bash
# تست عملکرد Redis cluster
python3 test-redis-cluster.py

# تست مانیتورینگ و HA Sentinel
python3 test-sentinel-simple.py

# اجرای نمایش failover
./demo-sentinel-failover.sh
```

## 📋 ساختار پروژه

```
test-docker/
├── config/
│   ├── redis-master.conf      # پیکربندی Master
│   ├── redis-replica-1.conf   # پیکربندی Replica 1
│   ├── redis-replica-2.conf   # پیکربندی Replica 2
│   ├── redis-sentinel-1.conf  # پیکربندی Sentinel 1
│   ├── redis-sentinel-2.conf  # پیکربندی Sentinel 2
│   └── redis-sentinel-3.conf  # پیکربندی Sentinel 3
├── scripts/
│   ├── init-redis-master.sh   # اسکریپت راه‌اندازی Master
│   ├── init-redis-replica.sh  # اسکریپت راه‌اندازی Replica
│   └── init-redis-sentinel.sh # اسکریپت راه‌اندازی Sentinel
├── secrets/
│   ├── redis_master_password  # secret رمز Master
│   └── redis_sentinel_password # secret رمز Sentinel
├── docker-compose.yml         # پیکربندی Docker Compose
├── test-redis-cluster.py      # مجموعه تست‌های Redis cluster
├── test-sentinel-simple.py    # مجموعه تست‌های Sentinel cluster
├── demo-sentinel-failover.sh  # اسکریپت نمایش failover
├── start-redis-cluster.sh     # اسکریپت راه‌اندازی Linux/macOS
├── requirements.txt           # وابستگی‌های Python
├── redisinsight-config.json   # پیکربندی RedisInsight
├── redisinsight-databases.json # تعاریف پایگاه داده RedisInsight
├── README-Docker-Secrets.md   # مستندات Docker secrets
├── README.md                  # مستندات فارسی
└── README-EN.md              # مستندات انگلیسی
```

## 🤝 مشارکت

1. Fork کردن repository
2. ایجاد شاخه feature
3. اعمال تغییرات
4. تست کامل
5. ارسال pull request

## 📚 منابع بیشتر

- [Redis Documentation](https://redis.io/documentation)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Secrets Documentation](https://docs.docker.com/engine/swarm/secrets/)
- [Redis Replication](https://redis.io/topics/replication)
- [Redis Sentinel](https://redis.io/topics/sentinel)
- [Redis Security](https://redis.io/topics/security)
- [Redis Performance](https://redis.io/topics/benchmarks)
- [RedisInsight Documentation](https://docs.redis.com/latest/ri/)

## 📄 فایل‌های مستندات

- `README-Docker-Secrets.md` - راهنمای تفصیلی پیاده‌سازی Docker secrets
- `SECRETS-IMPLEMENTATION-SUMMARY.md` - خلاصه بهبودهای امنیتی

## 📄 مجوز

این پروژه open source است و تحت مجوز MIT در دسترس می‌باشد.
