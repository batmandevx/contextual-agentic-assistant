# Implementation Plan: Contextual Agentic AI Assistant

## Overview

This implementation plan breaks down the development into three phases, with Phase 1 being the priority for initial submission. The plan focuses on incremental development with testing integrated throughout. Each task builds on previous work, ensuring no orphaned code.

The implementation uses:
- **Backend**: Python with FastAPI
- **Frontend**: React with TypeScript (Next.js)
- **Infrastructure**: Terraform for AWS provisioning
- **CI/CD**: GitHub Actions

## Tasks

### Phase 1: Foundation (Priority - Submission Ready)

- [x] 1. Project Setup and Repository Structure
  - Create GitHub repository with frontend/ and backend/ directories
  - Set up .gitignore for Python, Node.js, and Terraform
  - Create README.md with project overview and setup instructions
  - Initialize backend with Python virtual environment and requirements.txt
  - Initialize frontend with Next.js and TypeScript
  - _Requirements: 5.1_

- [x] 2. Backend Core Setup
  - [x] 2.1 Create FastAPI application structure
    - Set up main.py with FastAPI app initialization
    - Configure CORS middleware for frontend communication
    - Add health check endpoint (GET /api/health)
    - Create config.py for environment variable management
    - _Requirements: 2.1, 15.3_
  
  - [x] 2.2 Write unit tests for health endpoint
    - Test health endpoint returns 200 status
    - Test CORS headers are present
    - _Requirements: 15.3_

- [x] 3. Database Setup and Models
  - [x] 3.1 Set up database connection and models
    - Install SQLAlchemy and psycopg2
    - Create database.py with connection pooling
    - Define User, Session, Conversation, Message, MemoryEntry models
    - Create Alembic migration scripts for initial schema
    - Add database initialization script
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 3.2 Write property test for data persistence
    - **Property 9: Conversation Persistence**
    - **Validates: Requirements 4.2, 4.5**
    - Test that conversations with messages survive system restart
    - _Requirements: 4.2, 4.5_
  
  - [x] 3.3 Write property test for memory entry structure
    - **Property 10: Memory Entry Structure**
    - **Validates: Requirements 4.3**
    - Test that all memory entries have required metadata fields
    - _Requirements: 4.3_


- [x] 4. Google OAuth Authentication
  - [x] 4.1 Implement OAuth flow endpoints
    - Create auth.py with OAuth2 client configuration
    - Implement POST /api/auth/login (redirect to Google)
    - Implement POST /api/auth/callback (handle OAuth response)
    - Implement POST /api/auth/logout (revoke session)
    - Implement GET /api/auth/status (check authentication)
    - Add token encryption/decryption utilities
    - Configure test user harisankar@sentellent.com in Google Cloud Console
    - _Requirements: 1.1, 1.2, 1.3, 1.5_
  
  - [x] 4.2 Write property test for OAuth session creation
    - **Property 1: OAuth Session Creation**
    - **Validates: Requirements 1.2**
    - Test that successful OAuth creates encrypted session
    - _Requirements: 1.2_
  
  - [x] 4.3 Write property test for logout cleanup
    - **Property 3: Logout Cleanup**
    - **Validates: Requirements 1.5**
    - Test that logout clears all tokens and session data
    - _Requirements: 1.5_
  
  - [x] 4.4 Write unit tests for authentication edge cases
    - Test OAuth failure handling
    - Test invalid token scenarios
    - Test session expiry
    - _Requirements: 1.4, 1.6_

- [x] 5. Basic LangGraph Agent Setup
  - [x] 5.1 Create minimal LangGraph agent
    - Install langchain, langgraph, and openai packages
    - Create agent.py with AgentState TypedDict
    - Implement simple graph: retrieve_memory → call_llm → respond
    - Create agent initialization function
    - Add LLM configuration (OpenAI GPT-4)
    - _Requirements: 2.1, 3.1_
  
  - [x] 5.2 Write property test for message processing
    - **Property 4: Message Processing**
    - **Validates: Requirements 2.1, 2.3**
    - Test that any user message gets a response
    - _Requirements: 2.1, 2.3_

- [x] 6. Chat API Endpoints
  - [x] 6.1 Implement chat endpoints
    - Create chat.py with conversation management
    - Implement POST /api/chat/message (send message, get response)
    - Implement GET /api/chat/history/{conversation_id} (retrieve history)
    - Add authentication middleware to protect endpoints
    - Integrate LangGraph agent for message processing
    - _Requirements: 2.1, 2.2_
  
  - [x] 6.2 Write property test for conversation history
    - **Property 5: Conversation History Preservation**
    - **Validates: Requirements 2.2**
    - Test that message sequences are maintained in order
    - _Requirements: 2.2_
  
  - [x] 6.3 Write property test for user isolation
    - **Property 6: User Isolation**
    - **Validates: Requirements 2.4**
    - Test that concurrent users don't see each other's data
    - _Requirements: 2.4_
  
  - [x] 6.4 Write unit tests for chat API
    - Test message sending with valid session
    - Test message sending without authentication
    - Test conversation history retrieval
    - _Requirements: 2.1, 2.2_

- [x] 7. Checkpoint - Backend Core Complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Frontend Setup
  - [x] 8.1 Create Next.js application structure
    - Set up Next.js with TypeScript and Tailwind CSS
    - Create pages: index (chat), login, callback
    - Set up API client with axios for backend communication
    - Configure environment variables for API URL
    - _Requirements: 13.1_
  
  - [x] 8.2 Write unit tests for frontend components
    - Test chat interface renders correctly
    - Test message list displays messages
    - _Requirements: 13.1_

- [x] 9. Authentication UI
  - [x] 9.1 Implement login and authentication flow
    - Create LoginButton component
    - Create AuthProvider context for auth state management
    - Implement OAuth callback page
    - Add protected route wrapper for authenticated pages
    - Store JWT token in localStorage
    - _Requirements: 1.1, 13.4_
  
  - [x] 9.2 Write unit tests for authentication UI
    - Test login button triggers OAuth flow
    - Test callback page handles OAuth response
    - Test protected routes redirect when not authenticated
    - _Requirements: 1.1_

- [x] 10. Chat Interface
  - [x] 10.1 Build chat UI components
    - Create ChatInterface component with message list
    - Create MessageList component with user/assistant distinction
    - Create InputBox component with send button
    - Add typing indicator component
    - Implement message sending and display
    - Add auto-scroll to latest message
    - _Requirements: 13.1, 13.2_
  
  - [x] 10.2 Write property test for typing indicators
    - **Property 33: Typing Indicator Display**
    - **Validates: Requirements 13.2**
    - Test that typing indicator shows during processing
    - _Requirements: 13.2_
  
  - [x] 10.3 Write unit tests for chat UI
    - Test message rendering
    - Test input box submission
    - Test empty message prevention
    - _Requirements: 13.1_

- [x] 11. Docker Configuration
  - [x] 11.1 Create Dockerfiles for frontend and backend
    - Create backend/Dockerfile with Python 3.11
    - Create frontend/Dockerfile with Node.js 18 and nginx
    - Create docker-compose.yml for local development
    - Add .dockerignore files
    - Test local Docker builds
    - _Requirements: 5.1_
  
  - [x] 11.2 Write unit tests for Docker builds
    - Test that Docker images build successfully
    - Test that containers start and respond to health checks
    - _Requirements: 5.1_

- [x] 12. Terraform Infrastructure Setup
  - [x] 12.1 Create Terraform configuration for AWS
    - Create terraform/ directory structure
    - Write provider.tf with AWS provider configuration
    - Write variables.tf with input variables
    - Write outputs.tf with output values
    - Create modules/vpc/ for VPC, subnets, routing
    - Create modules/ecs/ for ECS cluster and services
    - Create modules/rds/ for PostgreSQL database
    - Create modules/iam/ for IAM roles and policies
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6_
  
  - [x] 12.2 Create ECS task definitions
    - Write ECS task definition for backend service
    - Write ECS task definition for frontend service
    - Configure environment variables and secrets
    - Set up Application Load Balancer
    - Configure CloudFront distribution for frontend
    - _Requirements: 5.3, 5.4_
  
  - [x] 12.3 Configure RDS PostgreSQL
    - Create RDS instance with Terraform
    - Set up security groups for database access
    - Configure automated backups
    - Store database credentials in Secrets Manager
    - _Requirements: 5.6_

- [x] 13. AWS ECR Setup
  - [x] 13.1 Create ECR repositories
    - Create ECR repository for backend images
    - Create ECR repository for frontend images
    - Configure repository policies
    - _Requirements: 5.1_

- [x] 14. CI/CD Pipeline with GitHub Actions
  - [x] 14.1 Create GitHub Actions workflow
    - Create .github/workflows/deploy.yml
    - Add test job (run pytest for backend)
    - Add build-and-push job (build Docker images, push to ECR)
    - Add deploy job (update ECS services)
    - Configure AWS credentials as GitHub secrets
    - Add workflow triggers (push to main branch)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 14.2 Write unit tests for CI/CD validation
    - Test that workflow YAML is valid
    - Test that all required secrets are documented
    - _Requirements: 6.1_

- [x] 15. Checkpoint - Phase 1 Complete
  - Deploy to AWS using Terraform
  - Verify CI/CD pipeline runs successfully
  - Test live application URL
  - Verify user can log in via OAuth
  - Verify user can chat with agent
  - Take screenshots of AWS Console and CI/CD pipeline
  - Ensure all tests pass, ask the user if questions arise.

### Phase 2: Google Workspace Integration

- [ ] 16. MCP Server Setup
  - [ ] 16.1 Create MCP server structure
    - Install MCP SDK packages
    - Create mcp_servers/ directory
    - Create gmail_server.py with Gmail tool definitions
    - Create calendar_server.py with Calendar tool definitions
    - Implement MCP tool registration
    - _Requirements: 3.1, 3.2_
  
  - [ ] 16.2 Write property test for tool routing
    - **Property 8: Tool Routing**
    - **Validates: Requirements 3.2**
    - Test that actions route to correct MCP servers
    - _Requirements: 3.2_

- [ ] 17. Gmail Integration
  - [ ] 17.1 Implement Gmail API wrapper
    - Create google_integration.py with GmailService class
    - Implement get_messages() method with query support
    - Implement get_message_content() method
    - Add OAuth token refresh logic
    - Handle Gmail API rate limits
    - _Requirements: 7.1, 7.2, 7.5_
  
  - [ ] 17.2 Create Gmail MCP tools
    - Implement read_email tool
    - Implement search_emails tool
    - Add email formatting for chat display
    - _Requirements: 7.2, 7.3_
  
  - [ ] 17.3 Write property test for Gmail authentication
    - **Property 12: Google API Authentication**
    - **Validates: Requirements 7.1, 8.1**
    - Test that Gmail requests use OAuth tokens
    - _Requirements: 7.1_
  
  - [ ] 17.4 Write property test for token refresh
    - **Property 13: OAuth Token Refresh**
    - **Validates: Requirements 7.5, 8.5**
    - Test that expired tokens are automatically refreshed
    - _Requirements: 7.5_
  
  - [ ] 17.5 Write property test for email query filtering
    - **Property 14: Email Query Filtering**
    - **Validates: Requirements 7.2**
    - Test that email searches return only matching results
    - _Requirements: 7.2_
  
  - [ ] 17.6 Write unit tests for Gmail integration
    - Test email fetching with various queries
    - Test rate limit handling
    - Test API failure scenarios
    - _Requirements: 7.2, 7.4, 7.6_

- [ ] 18. Calendar Integration
  - [ ] 18.1 Implement Calendar API wrapper
    - Add CalendarService class to google_integration.py
    - Implement list_events() method
    - Implement get_free_busy() method
    - Add OAuth token refresh logic
    - Handle Calendar API rate limits
    - _Requirements: 8.1, 8.2, 8.5_
  
  - [ ] 18.2 Create Calendar MCP tools
    - Implement list_events tool
    - Implement check_availability tool
    - Add event formatting for chat display
    - _Requirements: 8.2, 8.3_
  
  - [ ] 18.3 Write property test for calendar event query
    - **Property 16: Calendar Event Query**
    - **Validates: Requirements 8.2**
    - Test that event queries return only events in time range
    - _Requirements: 8.2_
  
  - [ ] 18.4 Write property test for event completeness
    - **Property 17: Calendar Event Completeness**
    - **Validates: Requirements 8.3**
    - Test that displayed events have all required fields
    - _Requirements: 8.3_
  
  - [ ] 18.5 Write unit tests for Calendar integration
    - Test event fetching with various time ranges
    - Test rate limit handling
    - Test API failure scenarios
    - _Requirements: 8.2, 8.4, 8.6_

- [ ] 19. Integrate MCP Tools with LangGraph Agent
  - [ ] 19.1 Update agent to use MCP tools
    - Add execute_tool node to LangGraph
    - Implement tool selection logic
    - Add tool result incorporation to responses
    - Update agent state to track tool calls
    - _Requirements: 3.2, 3.3_
  
  - [ ] 19.2 Write property test for tool result incorporation
    - **Property 7: Tool Result Incorporation**
    - **Validates: Requirements 3.3**
    - Test that MCP tool results appear in agent responses
    - _Requirements: 3.3_
  
  - [ ] 19.3 Write unit tests for agent tool integration
    - Test agent selects correct tool for email requests
    - Test agent selects correct tool for calendar requests
    - Test agent handles tool failures gracefully
    - _Requirements: 3.2, 3.4_

- [ ] 20. Email Drafting Feature
  - [ ] 20.1 Implement email draft generation
    - Add draft_email tool to Gmail MCP server
    - Implement draft generation in agent
    - Add draft review UI component in frontend
    - Implement draft confirmation flow
    - _Requirements: 9.1, 9.3, 9.4, 9.5_
  
  - [ ] 20.2 Write property test for draft generation
    - **Property 18: Draft Generation from Instructions**
    - **Validates: Requirements 9.1**
    - Test that drafts address all instruction points
    - _Requirements: 9.1_
  
  - [ ] 20.3 Write property test for draft structure
    - **Property 20: Draft Structure Completeness**
    - **Validates: Requirements 9.4**
    - Test that drafts have subject, greeting, body, signature
    - _Requirements: 9.4_
  
  - [ ] 20.4 Write property test for no unsolicited sending
    - **Property 21: No Unsolicited Sending**
    - **Validates: Requirements 9.5**
    - Test that drafts never send without confirmation
    - _Requirements: 9.5_
  
  - [ ] 20.5 Write unit tests for email drafting
    - Test draft generation with various instructions
    - Test draft review UI
    - Test draft confirmation flow
    - _Requirements: 9.1, 9.3_

- [ ] 21. Checkpoint - Phase 2 Complete
  - Verify Gmail integration works (read emails)
  - Verify Calendar integration works (view events)
  - Verify email drafting works
  - Ensure all tests pass, ask the user if questions arise.

### Phase 3: Dynamic Memory System

- [ ] 22. Memory System Core
  - [ ] 22.1 Implement memory storage and retrieval
    - Create memory.py with MemorySystem class
    - Implement store() method for saving memory entries
    - Implement retrieve() method with semantic search
    - Implement update() method for updating entries
    - Add embedding generation using OpenAI embeddings
    - Set up vector store (pgvector or separate vector DB)
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ] 22.2 Write property test for memory entry structure
    - **Property 10: Memory Entry Structure** (already tested in 3.3)
    - Verify memory entries have all required metadata
    - _Requirements: 4.3, 10.2_
  
  - [ ] 22.3 Write property test for memory retrieval
    - **Property 24: Memory Retrieval for Requests**
    - **Validates: Requirements 10.4, 12.1**
    - Test that requests trigger relevant memory queries
    - _Requirements: 10.4, 12.1_
  
  - [ ] 22.4 Write property test for memory prioritization
    - **Property 31: Memory Prioritization**
    - **Validates: Requirements 12.2**
    - Test that memories are prioritized by confidence and recency
    - _Requirements: 12.2_

- [ ] 23. Chat-Based Memory Learning
  - [ ] 23.1 Implement preference extraction from chat
    - Create extract_from_text() method in MemorySystem
    - Add LLM-based preference detection
    - Implement confidence scoring for explicit preferences
    - Add memory extraction to agent graph
    - _Requirements: 10.1, 10.2_
  
  - [ ] 23.2 Write property test for explicit preference extraction
    - **Property 22: Explicit Preference Extraction**
    - **Validates: Requirements 10.1**
    - Test that explicit preferences are extracted and stored
    - _Requirements: 10.1_
  
  - [ ] 23.3 Write property test for preference updates
    - **Property 23: Preference Update on Contradiction**
    - **Validates: Requirements 10.3**
    - Test that contradictions update existing preferences
    - _Requirements: 10.3_
  
  - [ ] 23.4 Write unit tests for chat memory extraction
    - Test extraction of various preference types
    - Test confidence scoring
    - Test handling of ambiguous statements
    - _Requirements: 10.1, 10.2_

- [ ] 24. Data-Based Memory Learning
  - [ ] 24.1 Implement information extraction from emails and calendar
    - Add email content analysis to Gmail tools
    - Add calendar pattern recognition
    - Implement extraction of projects, deadlines, contacts
    - Implement pattern detection for recurring meetings
    - Add confidence scoring for extracted information
    - _Requirements: 11.1, 11.2, 11.3, 11.4_
  
  - [ ] 24.2 Write property test for email information extraction
    - **Property 26: Email Information Extraction**
    - **Validates: Requirements 11.1**
    - Test that key info is extracted from emails
    - _Requirements: 11.1_
  
  - [ ] 24.3 Write property test for calendar pattern recognition
    - **Property 27: Calendar Pattern Recognition**
    - **Validates: Requirements 11.2**
    - Test that patterns are identified from calendar data
    - _Requirements: 11.2_
  
  - [ ] 24.4 Write property test for extraction confidence scoring
    - **Property 28: Extraction Confidence Scoring**
    - **Validates: Requirements 11.4**
    - Test that extractions have confidence scores
    - _Requirements: 11.4_
  
  - [ ] 24.5 Write property test for confidence increase on repetition
    - **Property 29: Confidence Increase on Repetition**
    - **Validates: Requirements 11.5**
    - Test that repeated info increases confidence
    - _Requirements: 11.5_

- [ ] 25. Memory Application to Actions
  - [ ] 25.1 Integrate memory into agent actions
    - Update agent to query memory before responding
    - Apply preferences to email drafts
    - Apply preferences to meeting time suggestions
    - Apply learned importance to inbox prioritization
    - Add reasoning explanations when using memory
    - _Requirements: 10.5, 12.3, 12.4, 12.5, 12.6_
  
  - [ ] 25.2 Write property test for preference application
    - **Property 25: Preference Application to Actions**
    - **Validates: Requirements 10.5, 12.4, 12.5**
    - Test that actions respect stored preferences
    - _Requirements: 10.5, 12.4, 12.5_
  
  - [ ] 25.3 Write property test for draft style application
    - **Property 19: Draft Style Application**
    - **Validates: Requirements 9.2, 12.3**
    - Test that drafts reflect learned communication style
    - _Requirements: 9.2, 12.3_
  
  - [ ] 25.4 Write property test for extracted context application
    - **Property 30: Extracted Context Application**
    - **Validates: Requirements 11.6**
    - Test that extracted info is used in responses
    - _Requirements: 11.6_
  
  - [ ] 25.5 Write property test for memory-influenced reasoning
    - **Property 32: Memory-Influenced Reasoning**
    - **Validates: Requirements 12.6**
    - Test that responses explain memory usage
    - _Requirements: 12.6_
  
  - [ ] 25.6 Write unit tests for memory application
    - Test preference application to various actions
    - Test reasoning explanations
    - Test memory retrieval performance
    - _Requirements: 10.5, 12.3, 12.4, 12.5, 12.6_

- [ ] 26. Memory UI Features
  - [ ] 26.1 Add memory visualization to frontend
    - Create MemoryPanel component to display learned preferences
    - Add ability to view stored memories
    - Add ability to edit or delete memories
    - Show memory confidence scores
    - _Requirements: 10.1, 10.2_

- [ ] 27. Checkpoint - Phase 3 Complete
  - Verify memory learns from chat
  - Verify memory extracts from emails
  - Verify memory extracts from calendar
  - Verify drafts use learned style
  - Verify suggestions respect preferences
  - Ensure all tests pass, ask the user if questions arise.

### Security and Production Readiness

- [ ] 28. Security Hardening
  - [ ] 28.1 Implement security features
    - Add token encryption at rest
    - Implement rate limiting middleware
    - Add input validation and sanitization
    - Implement security event logging
    - Add HTTPS enforcement
    - Configure CORS properly
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_
  
  - [ ] 28.2 Write property test for token encryption
    - **Property 35: Token Encryption at Rest**
    - **Validates: Requirements 14.1**
    - Test that stored tokens are encrypted
    - _Requirements: 14.1_
  
  - [ ] 28.3 Write property test for rate limiting
    - **Property 37: Rate Limiting**
    - **Validates: Requirements 14.4**
    - Test that excessive requests are blocked
    - _Requirements: 14.4_
  
  - [ ] 28.4 Write property test for security event logging
    - **Property 38: Security Event Logging**
    - **Validates: Requirements 14.5**
    - Test that security events are logged
    - _Requirements: 14.5_
  
  - [ ] 28.5 Write unit tests for security features
    - Test input validation
    - Test CORS configuration
    - Test HTTPS enforcement
    - _Requirements: 14.2, 14.3_

- [ ] 29. Error Handling and Monitoring
  - [ ] 29.1 Implement comprehensive error handling
    - Add structured error logging
    - Implement circuit breakers for external APIs
    - Add CloudWatch metrics integration
    - Create CloudWatch alarms for critical errors
    - Add user-friendly error messages
    - _Requirements: 15.1, 15.2, 15.4, 15.5, 15.6_
  
  - [ ] 29.2 Write property test for error logging structure
    - **Property 41: Error Logging Structure**
    - **Validates: Requirements 15.1**
    - Test that errors are logged with required info
    - _Requirements: 15.1_
  
  - [ ] 29.3 Write property test for safe error messages
    - **Property 42: Safe Error Messages**
    - **Validates: Requirements 15.2**
    - Test that errors don't expose internal details
    - _Requirements: 15.2_
  
  - [ ] 29.4 Write property test for metrics tracking
    - **Property 43: Metrics Tracking**
    - **Validates: Requirements 15.4**
    - Test that API requests are tracked with metrics
    - _Requirements: 15.4_
  
  - [ ] 29.5 Write property test for circuit breakers
    - **Property 44: Circuit Breaker Activation**
    - **Validates: Requirements 15.6**
    - Test that repeated failures trigger circuit breakers
    - _Requirements: 15.6_

- [ ] 30. Data Privacy and Compliance
  - [ ] 30.1 Implement data privacy features
    - Add email content minimization logic
    - Implement account deletion functionality
    - Add data retention policies
    - Create privacy policy documentation
    - _Requirements: 14.6, 14.7_
  
  - [ ] 30.2 Write property test for email content minimization
    - **Property 39: Email Content Minimization**
    - **Validates: Requirements 14.6**
    - Test that full email content isn't over-retained
    - _Requirements: 14.6_
  
  - [ ] 30.3 Write property test for account deletion
    - **Property 40: Account Deletion Completeness**
    - **Validates: Requirements 14.7**
    - Test that account deletion removes all user data
    - _Requirements: 14.7_

- [ ] 31. Final Integration and Testing
  - [ ] 31.1 End-to-end testing
    - Test complete user flow: login → chat → email reading → drafting
    - Test memory learning across multiple sessions
    - Test error scenarios and recovery
    - Performance testing for response times
    - Load testing for concurrent users
    - _Requirements: All_
  
  - [ ] 31.2 Write integration tests
    - Test full authentication flow
    - Test chat with Gmail integration
    - Test chat with Calendar integration
    - Test memory persistence across sessions
    - _Requirements: All_

- [ ] 32. Documentation and Deployment
  - [ ] 32.1 Create deployment documentation
    - Document AWS setup steps
    - Document Google Cloud Console OAuth setup
    - Document environment variables
    - Document CI/CD pipeline configuration
    - Create troubleshooting guide
    - _Requirements: All_
  
  - [ ] 32.2 Final deployment
    - Deploy to production AWS environment
    - Verify all services running
    - Test live application
    - Take screenshots for submission
    - _Requirements: 5.8, 6.7_

- [ ] 33. Final Checkpoint - Project Complete
  - Verify all requirements met
  - Verify all tests passing
  - Verify live URL accessible
  - Verify CI/CD pipeline working
  - Verify AWS Console shows running services
  - Prepare submission materials
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks are now required for complete implementation
- Phase 1 (Tasks 1-15) is submission-worthy on its own and covers >50% of evaluation
- Infrastructure and deployment tasks (11-15) are heavily weighted in evaluation
- Each property test should run minimum 100 iterations
- Property tests should be tagged with: `# Feature: contextual-agentic-assistant, Property {number}: {property_text}`
- Focus on getting Phase 1 deployed before moving to Phase 2 and 3
- Test user harisankar@sentellent.com must be configured in Google Cloud Console OAuth settings
