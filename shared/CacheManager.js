/**
 * CacheManager - Redis-based caching for A2A Protocol
 * Optimizes performance for agent discovery and health checks
 */

class CacheManager {
  constructor(config = {}) {
    this.config = {
      ttl: config.ttl || 300, // 5 minutes default
      enabled: config.enabled !== false,
      prefix: config.prefix || 'a2a:',
      redis: config.redis || null,
      fallbackToMemory: config.fallbackToMemory !== false,
      ...config
    };

    this.memoryCache = new Map();
    this.redisClient = null;
    
    this.initializeRedis();
  }

  async initializeRedis() {
    if (this.config.redis && this.config.enabled) {
      try {
        // Try to use provided Redis client or create new one
        if (typeof this.config.redis === 'object') {
          this.redisClient = this.config.redis;
        } else {
          // Fallback to memory cache if Redis not available
          console.log('⚠️  Redis not configured, using memory cache');
        }
      } catch (error) {
        console.warn('⚠️  Redis connection failed, falling back to memory cache:', error.message);
        this.redisClient = null;
      }
    }
  }

  generateKey(prefix, key) {
    return `${this.config.prefix}${prefix}:${key}`;
  }

  async get(prefix, key) {
    if (!this.config.enabled) return null;

    const cacheKey = this.generateKey(prefix, key);

    try {
      // Try Redis first
      if (this.redisClient) {
        const cached = await this.redisClient.get(cacheKey);
        if (cached) {
          const data = JSON.parse(cached);
          if (data.expires > Date.now()) {
            return data.value;
          } else {
            // Expired, clean up
            await this.redisClient.del(cacheKey);
          }
        }
      }

      // Fallback to memory cache
      if (this.config.fallbackToMemory) {
        const memCached = this.memoryCache.get(cacheKey);
        if (memCached && memCached.expires > Date.now()) {
          return memCached.value;
        } else if (memCached) {
          this.memoryCache.delete(cacheKey);
        }
      }
    } catch (error) {
      console.warn('⚠️  Cache get error:', error.message);
    }

    return null;
  }

  async set(prefix, key, value, customTtl = null) {
    if (!this.config.enabled) return;

    const cacheKey = this.generateKey(prefix, key);
    const ttl = customTtl || this.config.ttl;
    const expires = Date.now() + (ttl * 1000);
    const cacheData = { value, expires };

    try {
      // Store in Redis
      if (this.redisClient) {
        await this.redisClient.setex(
          cacheKey, 
          ttl, 
          JSON.stringify(cacheData)
        );
      }

      // Store in memory cache as backup
      if (this.config.fallbackToMemory) {
        this.memoryCache.set(cacheKey, cacheData);
        
        // Clean up expired memory entries periodically
        if (this.memoryCache.size % 100 === 0) {
          this.cleanupMemoryCache();
        }
      }
    } catch (error) {
      console.warn('⚠️  Cache set error:', error.message);
    }
  }

  async invalidate(prefix, key = null) {
    if (!this.config.enabled) return;

    try {
      if (key) {
        // Invalidate specific key
        const cacheKey = this.generateKey(prefix, key);
        
        if (this.redisClient) {
          await this.redisClient.del(cacheKey);
        }
        
        if (this.config.fallbackToMemory) {
          this.memoryCache.delete(cacheKey);
        }
      } else {
        // Invalidate all keys with prefix
        const pattern = this.generateKey(prefix, '*');
        
        if (this.redisClient) {
          const keys = await this.redisClient.keys(pattern);
          if (keys.length > 0) {
            await this.redisClient.del(...keys);
          }
        }
        
        if (this.config.fallbackToMemory) {
          const prefixPattern = this.generateKey(prefix, '');
          for (const [cacheKey] of this.memoryCache) {
            if (cacheKey.startsWith(prefixPattern)) {
              this.memoryCache.delete(cacheKey);
            }
          }
        }
      }
    } catch (error) {
      console.warn('⚠️  Cache invalidate error:', error.message);
    }
  }

  cleanupMemoryCache() {
    const now = Date.now();
    for (const [key, data] of this.memoryCache) {
      if (data.expires <= now) {
        this.memoryCache.delete(key);
      }
    }
  }

  // Cache middleware for Express
  middleware(prefix, ttl = null) {
    return async (req, res, next) => {
      if (!this.config.enabled) {
        return next();
      }

      const cacheKey = `${req.method}:${req.path}:${JSON.stringify(req.query)}`;
      
      try {
        const cached = await this.get(prefix, cacheKey);
        if (cached) {
          res.header('X-Cache', 'HIT');
          return res.json(cached);
        }
      } catch (error) {
        console.warn('⚠️  Cache middleware error:', error.message);
      }

      // Override res.json to cache the response
      const originalJson = res.json.bind(res);
      res.json = (data) => {
        // Cache successful responses
        if (res.statusCode >= 200 && res.statusCode < 300) {
          this.set(prefix, cacheKey, data, ttl).catch(error => {
            console.warn('⚠️  Failed to cache response:', error.message);
          });
        }
        
        res.header('X-Cache', 'MISS');
        return originalJson(data);
      };

      next();
    };
  }

  // Get cache statistics
  async getStats() {
    const stats = {
      enabled: this.config.enabled,
      redis_connected: !!this.redisClient,
      memory_cache_size: this.memoryCache.size,
      memory_cache_keys: Array.from(this.memoryCache.keys()),
      config: {
        ttl: this.config.ttl,
        prefix: this.config.prefix,
        fallbackToMemory: this.config.fallbackToMemory
      }
    };

    if (this.redisClient) {
      try {
        const redisInfo = await this.redisClient.info('memory');
        stats.redis_memory = redisInfo;
      } catch (error) {
        stats.redis_error = error.message;
      }
    }

    return stats;
  }

  async close() {
    if (this.redisClient && typeof this.redisClient.quit === 'function') {
      await this.redisClient.quit();
    }
    this.memoryCache.clear();
  }
}

module.exports = CacheManager;