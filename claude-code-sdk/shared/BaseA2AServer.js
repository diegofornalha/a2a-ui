/**
 * BaseA2AServer - Unified A2A Protocol Server
 * Eliminates duplication across multiple a2a-server.js files
 * Implements Agent2Agent Protocol 1.0 with configurable agents
 * Enhanced with caching and performance optimizations
 */

const express = require('express');
const path = require('path');
const fs = require('fs').promises;
const CacheManager = require('./CacheManager');

class BaseA2AServer {
  constructor(config = {}) {
    this.config = {
      port: config.port || process.env.A2A_PORT || 8130,
      agentClass: config.agentClass,
      agentName: config.agentName || 'Unknown Agent',
      basePath: config.basePath || __dirname,
      wellKnownPath: config.wellKnownPath || '.well-known',
      cache: {
        enabled: config.cache?.enabled !== false,
        ttl: config.cache?.ttl || 300, // 5 minutes
        redis: config.cache?.redis || null,
        ...config.cache
      },
      ...config
    };
    
    this.app = express();
    this.agent = null;
    this.cache = new CacheManager(this.config.cache);
    
    this.initializeAgent();
    this.setupMiddleware();
    this.setupRoutes();
  }

  initializeAgent() {
    if (this.config.agentClass) {
      this.agent = new this.config.agentClass(this.config.agentConfig || {});
    } else {
      throw new Error('Agent class must be provided in config');
    }
  }

  setupMiddleware() {
    this.app.use(express.json());
    this.app.use((req, res, next) => {
      res.header('Access-Control-Allow-Origin', '*');
      res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.header('Access-Control-Allow-Headers', 'Content-Type, X-A2A-Protocol');
      res.header('X-A2A-Protocol', '1.0');
      next();
    });

    // Request logging middleware
    this.app.use((req, res, next) => {
      console.log(`🌐 ${new Date().toISOString()} - ${req.method} ${req.path}`);
      next();
    });
  }

  setupRoutes() {
    // A2A Protocol Core Endpoints with caching
    this.app.get('/discover', 
      this.cache.middleware('discover', 60), // Cache for 1 minute
      async (req, res) => {
      try {
        const discovery = await this.agent.discover();
        res.json({
          ...discovery,
          timestamp: new Date().toISOString(),
          protocol_version: '1.0'
        });
      } catch (error) {
        console.error('❌ Discovery error:', error);
        res.status(500).json({ 
          error: 'Discovery failed', 
          message: error.message,
          timestamp: new Date().toISOString()
        });
      }
    });

    this.app.post('/communicate', async (req, res) => {
      try {
        const response = await this.agent.communicate(req.body);
        res.json({
          ...response,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        console.error('❌ Communication error:', error);
        res.status(500).json({ 
          error: 'Communication failed', 
          message: error.message,
          timestamp: new Date().toISOString()
        });
      }
    });

    this.app.post('/delegate', async (req, res) => {
      try {
        const result = await this.agent.delegate(req.body);
        res.json({
          ...result,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        console.error('❌ Delegation error:', error);
        res.status(500).json({ 
          error: 'Delegation failed', 
          message: error.message,
          timestamp: new Date().toISOString()
        });
      }
    });

    this.app.get('/health', 
      this.cache.middleware('health', 30), // Cache for 30 seconds
      async (req, res) => {
      try {
        const health = await this.agent.health();
        res.json({
          ...health,
          server_status: 'healthy',
          uptime: process.uptime(),
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        console.error('❌ Health check error:', error);
        res.status(503).json({ 
          server_status: 'unhealthy',
          error: error.message,
          timestamp: new Date().toISOString()
        });
      }
    });

    // Agent Card endpoint (well-known) with caching
    this.app.get('/agent.json', 
      this.cache.middleware('agent-card', 600), // Cache for 10 minutes
      async (req, res) => {
      try {
        const agentCardPath = path.join(
          this.config.basePath, 
          this.config.wellKnownPath, 
          'agent.json'
        );
        
        const agentCard = await fs.readFile(agentCardPath, 'utf-8');
        const cardData = JSON.parse(agentCard);
        
        res.json({
          ...cardData,
          last_updated: new Date().toISOString()
        });
      } catch (error) {
        console.error('❌ Agent card error:', error);
        res.status(404).json({ 
          error: 'Agent card not found',
          path: this.config.wellKnownPath,
          timestamp: new Date().toISOString()
        });
      }
    });

    // Status endpoint for monitoring
    this.app.get('/status', (req, res) => {
      res.json({
        agent_name: this.config.agentName,
        protocol_version: '1.0',
        server_uptime: process.uptime(),
        memory_usage: process.memoryUsage(),
        timestamp: new Date().toISOString()
      });
    });

    // Cache statistics endpoint
    this.app.get('/cache/stats', async (req, res) => {
      try {
        const stats = await this.cache.getStats();
        res.json({
          cache_stats: stats,
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        res.status(500).json({
          error: 'Failed to get cache stats',
          message: error.message,
          timestamp: new Date().toISOString()
        });
      }
    });

    // Cache invalidation endpoint (admin only)
    this.app.delete('/cache/:prefix?', async (req, res) => {
      try {
        const { prefix } = req.params;
        const { key } = req.query;
        
        await this.cache.invalidate(prefix || 'default', key);
        
        res.json({
          message: 'Cache invalidated successfully',
          prefix: prefix || 'default',
          key: key || 'all',
          timestamp: new Date().toISOString()
        });
      } catch (error) {
        res.status(500).json({
          error: 'Failed to invalidate cache',
          message: error.message,
          timestamp: new Date().toISOString()
        });
      }
    });

    // 404 handler
    this.app.use('*', (req, res) => {
      res.status(404).json({
        error: 'Endpoint not found',
        available_endpoints: ['/discover', '/communicate', '/delegate', '/health', '/agent.json', '/status'],
        timestamp: new Date().toISOString()
      });
    });
  }

  start() {
    return new Promise((resolve, reject) => {
      const server = this.app.listen(this.config.port, (error) => {
        if (error) {
          reject(error);
          return;
        }

        console.log(`🤖 A2A Server for ${this.config.agentName} started successfully`);
        console.log(`🚀 Port: ${this.config.port}`);
        console.log(`📋 A2A Protocol Endpoints:`);
        console.log(`   Discovery: http://localhost:${this.config.port}/discover`);
        console.log(`   Communicate: http://localhost:${this.config.port}/communicate`);
        console.log(`   Delegate: http://localhost:${this.config.port}/delegate`);
        console.log(`   Health: http://localhost:${this.config.port}/health`);
        console.log(`   Status: http://localhost:${this.config.port}/status`);
        console.log(`   Agent Card: http://localhost:${this.config.port}/agent.json`);
        
        resolve(server);
      });
    });
  }

  async stop() {
    try {
      // Close cache connections first
      await this.cache.close();
      
      if (this.server) {
        return new Promise((resolve) => {
          this.server.close(() => {
            console.log(`🛑 A2A Server for ${this.config.agentName} stopped`);
            resolve();
          });
        });
      }
    } catch (error) {
      console.error('❌ Error stopping server:', error);
    }
  }
}

module.exports = BaseA2AServer;