/**
 * A2A Server for agent_cards
 * Uses unified BaseA2AServer to eliminate duplication
 */

const BaseA2AServer = require('../shared/BaseA2AServer');
const AgentcardsAgent = require('./agents/agent_cards_agent');

// Simple configuration-based approach using BaseA2AServer
const server = new BaseA2AServer({
  port: process.env.A2A_PORT || 8130,
  agentClass: AgentcardsAgent,
  agentName: 'Agent Cards Agent',
  basePath: __dirname,
  wellKnownPath: '.well-known'
});

// Start server if run directly
if (require.main === module) {
  server.start().catch(error => {
    console.error('❌ Failed to start A2A Server:', error);
    process.exit(1);
  });
}

module.exports = server;