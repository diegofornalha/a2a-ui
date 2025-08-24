/**
 * A2A Server for a2a_mcp
 * Refactored to use BaseA2AServer - eliminates code duplication
 */

const BaseA2AServer = require('../../BaseA2AServer');
const A2amcpAgent = require('./agents/a2a_mcp_agent');

class A2AServer extends BaseA2AServer {
  constructor() {
    const agent = new A2amcpAgent();
    const port = process.env.A2A_PORT || 8174;
    const options = {
      agentCardPath: '.well-known/agent.json'
    };
    
    super(agent, port, options);
  }
}

// Start server if run directly
if (require.main === module) {
  const server = new A2AServer();
  server.start();
}

module.exports = A2AServer;