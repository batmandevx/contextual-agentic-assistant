# Design Document: Contextual Agentic AI Assistant

## Overview

The Contextual Agentic AI Assistant is a cloud-native personal Chief of Staff application that combines conversational AI with dynamic memory management and Google Workspace integration. The system architecture follows a microservices pattern with containerized frontend and backend services deployed on AWS infrastructure.

The core innovation is the dynamic memory system that learns from both explicit user instructions and implicit data extraction from emails and calendar events. This memory informs all agent actions, creating increasingly personalized and contextually aware assistance.

### Key Design Principles

1. **Cloud-Native Architecture**: Fully containerized, scalable deployment on AWS
2. **Security First**: OAuth 2.0, encrypted tokens, HTTPS everywhere
3. **Modular Tool Integration**: MCP servers for extensible capabilities
4. **Stateful Conversations**: LangGraph for complex, multi-step interactions
5. **Dynamic Learning**: Continuous memory building from chat and data sources
6. **Infrastructure as Code**: Terraform for reproducible deployments

## Architecture

### High-Level Architecture

```mermaid
graph TB
    User[User Browser] -->|HTTPS| CF[CloudFront CDN]
    CF --> FE[Frontend - React/Next.js<br/>ECS Fargate]
    FE -->|REST API| APIG[API Gateway]
    APIG --> BE[Backend - FastAPI<br/>ECS Fargate/Lambda]
    
    BE --> LG[LangGraph Agent]
    LG --> MCP[MCP Servers]
    
    BE --> DB[(PostgreSQL RDS<br/>or DynamoDB)]
    BE --> VS[(Vector Store<br/>for Embeddings)]
    
    BE -->|OAuth| GAPI[Google APIs]
    GAPI --> Gmail[Gmail API]
    GAPI --> Cal[Calendar API]
    
    BE --> Mem[Memory System]
    Mem --> VS
    Mem --> DB
    
    GH[GitHub] -->|Push to main| GHA[GitHub Actions<br/>CI/CD]
    GHA -->|Deploy| ECR[AWS ECR]
    ECR --> FE
    ECR --> BE
```

### Deployment Architecture

```mermaid
graph TB
    subgraph "AWS Cloud"
        subgraph "Public Subnet"
            CF[CloudFront]
            ALB[Application Load Balancer]
            APIG[API Gateway]
        end
        
        subgraph "Private Subnet - ECS Cluster"
            FE[Frontend Container<br/>ECS Fargate]
            BE[Backend Container<br/>ECS Fargate]
        end
        
        subgraph "Data Layer"
            RDS[(RDS PostgreSQL)]
            DDB[(DynamoDB)]
            S3[(S3 Bucket)]
        end
        
        CF --> ALB
        ALB --> FE
        APIG --> BE
        BE --> RDS
        BE --> DDB
        BE --> S3
    end
    
    subgraph "External Services"
        Google[Google OAuth & APIs]
    end
    
    BE --> Google
```

### Component Interaction Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant BE as Backend
    participant LG as LangGraph Agent
    participant MCP as MCP Server
    participant MEM as Memory System
    participant GAPI as Google API
    participant DB as Database
    
    U->>FE: Send message
    FE->>BE: POST /chat
    BE->>LG: Process message
    LG->>MEM: Retrieve relevant context
    MEM->>DB: Query memory entries
    DB-->>MEM: Return memories
    MEM-->>LG: Context data
    
    alt Action requires tool
        LG->>MCP: Execute tool (e.g., read email)
        MCP->>GAPI: API call
        GAPI-->>MCP: Response
        MCP-->>LG: Tool result
        LG->>MEM: Extract & store new info
        MEM->>DB: Save memory entry
    end
    
    LG-->>BE: Response with context
    BE-->>FE: JSON response
    FE-->>U: Display message
```

## Components and Interfaces

### 1. Frontend Application (React/Next.js)

**Responsibilities:**
- Render chat interface with message history
- Handle user authentication flow
- Manage WebSocket or polling for real-time updates
- Display typing indicators and loading states

**Key Components:**
- `ChatInterface`: Main conversation UI
- `AuthProvider`: OAuth flow management
- `MessageList`: Scrollable message history
- `InputBox`: Message composition with send button
- `LoginButton`: Authentication trigger

**API Interface:**
```typescript
interface FrontendAPI {
  // Authentication
  POST /auth/login -> { redirectUrl: string }
  POST /auth/callback -> { token: string, user: User }
  POST /auth/logout -> { success: boolean }
  
  // Chat
  POST /chat/message -> { response: string, conversationId: string }
  GET /chat/history -> { messages: Message[] }
  
  // Health
  GET /health -> { status: string }
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  conversationId: string;
}

interface User {
  id: string;
  email: string;
  name: string;
}
```

### 2. Backend API (FastAPI)

**Responsibilities:**
- Handle HTTP requests from frontend
- Manage user sessions and authentication
- Orchestrate LangGraph agent interactions
- Persist data to database
- Interface with Google APIs

**Key Modules:**
- `auth.py`: OAuth flow, token management, session handling
- `chat.py`: Message processing, conversation management
- `agent.py`: LangGraph agent initialization and execution
- `memory.py`: Memory storage and retrieval logic
- `google_integration.py`: Gmail and Calendar API wrappers
- `database.py`: Database models and operations

**API Endpoints:**
```python
# Authentication
POST /api/auth/login
POST /api/auth/callback
POST /api/auth/logout
GET /api/auth/status

# Chat
POST /api/chat/message
  Request: { message: str, conversationId?: str }
  Response: { response: str, conversationId: str }

GET /api/chat/history/{conversationId}
  Response: { messages: List[Message] }

# Memory (admin/debug)
GET /api/memory/entries
  Response: { entries: List[MemoryEntry] }

# Health
GET /api/health
  Response: { status: str, services: Dict[str, str] }
```

### 3. LangGraph Agent

**Responsibilities:**
- Process user messages with conversation context
- Decide when to use tools (email, calendar, memory)
- Maintain conversation state across turns
- Generate contextually appropriate responses

**Graph Structure:**
```python
class AgentState(TypedDict):
    messages: List[Message]
    conversation_id: str
    user_id: str
    memory_context: List[MemoryEntry]
    tool_results: List[ToolResult]
    next_action: str

# Graph nodes
def retrieve_memory(state: AgentState) -> AgentState:
    """Query memory system for relevant context"""
    pass

def call_llm(state: AgentState) -> AgentState:
    """Generate response using LLM with context"""
    pass

def execute_tool(state: AgentState) -> AgentState:
    """Execute MCP tool if needed"""
    pass

def extract_memory(state: AgentState) -> AgentState:
    """Extract new information to store in memory"""
    pass

def should_use_tool(state: AgentState) -> str:
    """Decide if tool execution is needed"""
    return "execute_tool" if needs_tool else "call_llm"
```

**LangGraph Flow:**
```mermaid
graph TD
    Start[Receive Message] --> RM[Retrieve Memory]
    RM --> LLM[Call LLM]
    LLM --> DT{Needs Tool?}
    DT -->|Yes| ET[Execute Tool]
    DT -->|No| EM[Extract Memory]
    ET --> EM
    EM --> End[Return Response]
```

### 4. MCP Server Integration

**Responsibilities:**
- Provide standardized tool interface for agent
- Execute Gmail operations (read, search)
- Execute Calendar operations (list events)
- Handle API authentication and rate limiting

**Tool Definitions:**
```python
# Gmail Tools
@mcp_tool
def read_email(email_id: str, user_id: str) -> EmailContent:
    """Read a specific email by ID"""
    pass

@mcp_tool
def search_emails(query: str, max_results: int, user_id: str) -> List[EmailSummary]:
    """Search emails matching criteria"""
    pass

# Calendar Tools
@mcp_tool
def list_events(start_date: str, end_date: str, user_id: str) -> List[CalendarEvent]:
    """List calendar events in date range"""
    pass

@mcp_tool
def check_availability(date: str, user_id: str) -> List[TimeSlot]:
    """Check free time slots on a date"""
    pass
```

### 5. Memory System

**Responsibilities:**
- Store learned preferences and extracted facts
- Retrieve relevant context for queries
- Update memory entries with new information
- Manage confidence scores and metadata

**Memory Entry Structure:**
```python
class MemoryEntry:
    id: str
    user_id: str
    content: str  # The actual memory (e.g., "User prefers meetings after 10 AM")
    category: str  # 'preference', 'fact', 'style', 'contact'
    source: str  # 'chat', 'email', 'calendar'
    confidence: float  # 0.0 to 1.0
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]  # Additional context
    embedding: List[float]  # Vector for semantic search
```

**Memory Operations:**
```python
class MemorySystem:
    def store(self, entry: MemoryEntry) -> str:
        """Store a new memory entry"""
        pass
    
    def retrieve(self, query: str, user_id: str, top_k: int = 5) -> List[MemoryEntry]:
        """Retrieve relevant memories using semantic search"""
        pass
    
    def update(self, entry_id: str, new_content: str, confidence: float) -> None:
        """Update existing memory entry"""
        pass
    
    def extract_from_text(self, text: str, source: str, user_id: str) -> List[MemoryEntry]:
        """Extract memorable information from text"""
        pass
```

**Memory Extraction Logic:**
- Use LLM to identify preferences, facts, and important information
- Assign confidence based on explicitness (explicit > implicit)
- Store with source metadata for traceability
- Generate embeddings for semantic retrieval

### 6. Google Workspace Integration

**Gmail Integration:**
```python
class GmailService:
    def __init__(self, credentials: OAuth2Credentials):
        self.service = build('gmail', 'v1', credentials=credentials)
    
    def get_messages(self, query: str, max_results: int = 10) -> List[Message]:
        """Fetch messages matching query"""
        pass
    
    def get_message_content(self, message_id: str) -> EmailContent:
        """Get full content of a message"""
        pass
    
    def create_draft(self, to: str, subject: str, body: str) -> Draft:
        """Create email draft"""
        pass
```

**Calendar Integration:**
```python
class CalendarService:
    def __init__(self, credentials: OAuth2Credentials):
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def list_events(self, time_min: str, time_max: str) -> List[Event]:
        """List events in time range"""
        pass
    
    def get_free_busy(self, time_min: str, time_max: str) -> FreeBusyResponse:
        """Get free/busy information"""
        pass
```

### 7. Database Schema

**PostgreSQL Schema:**
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    google_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    access_token_encrypted TEXT NOT NULL,
    refresh_token_encrypted TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Memory entries table
CREATE TABLE memory_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    source VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Vector embeddings (if using pgvector)
CREATE TABLE memory_embeddings (
    id UUID PRIMARY KEY REFERENCES memory_entries(id) ON DELETE CASCADE,
    embedding vector(1536)  -- Dimension depends on embedding model
);

CREATE INDEX idx_memory_embeddings ON memory_embeddings USING ivfflat (embedding vector_cosine_ops);
```

## Data Models

### Core Data Models

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class MemoryCategory(str, Enum):
    PREFERENCE = "preference"
    FACT = "fact"
    STYLE = "style"
    CONTACT = "contact"

class MemorySource(str, Enum):
    CHAT = "chat"
    EMAIL = "email"
    CALENDAR = "calendar"

class User(BaseModel):
    id: str
    email: str
    name: Optional[str]
    google_id: str
    created_at: datetime
    updated_at: datetime

class Session(BaseModel):
    id: str
    user_id: str
    access_token_encrypted: str
    refresh_token_encrypted: str
    expires_at: datetime
    created_at: datetime

class Message(BaseModel):
    id: str
    conversation_id: str
    role: MessageRole
    content: str
    created_at: datetime

class Conversation(BaseModel):
    id: str
    user_id: str
    messages: List[Message] = []
    created_at: datetime
    updated_at: datetime

class MemoryEntry(BaseModel):
    id: str
    user_id: str
    content: str
    category: MemoryCategory
    source: MemorySource
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    embedding: Optional[List[float]] = None

class EmailContent(BaseModel):
    id: str
    subject: str
    sender: str
    recipient: str
    body: str
    timestamp: datetime
    labels: List[str] = []

class CalendarEvent(BaseModel):
    id: str
    summary: str
    start: datetime
    end: datetime
    location: Optional[str]
    attendees: List[str] = []
    description: Optional[str]

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    memory_used: List[str] = []  # IDs of memory entries used
```

### State Models for LangGraph

```python
from typing import TypedDict, List, Annotated
from langgraph.graph import add_messages

class AgentState(TypedDict):
    messages: Annotated[List[Message], add_messages]
    conversation_id: str
    user_id: str
    memory_context: List[MemoryEntry]
    tool_calls: List[Dict[str, Any]]
    extracted_memories: List[MemoryEntry]
    next_action: str
```

## Infrastructure Design

### AWS Resource Architecture

**Compute:**
- **ECS Fargate Cluster**: Runs frontend and backend containers
- **Application Load Balancer**: Routes traffic to ECS tasks
- **API Gateway**: REST API endpoint for backend (alternative to ALB)
- **Lambda** (optional): Serverless backend alternative for cost optimization

**Storage:**
- **RDS PostgreSQL**: Primary relational database (users, conversations, messages)
- **DynamoDB** (alternative): NoSQL option for flexible schema
- **S3**: Static asset storage, Terraform state backend
- **ElastiCache Redis** (optional): Session caching, rate limiting

**Networking:**
- **VPC**: Isolated network with public and private subnets
- **CloudFront**: CDN for frontend static assets
- **Route 53**: DNS management
- **Certificate Manager**: SSL/TLS certificates

**Security:**
- **Secrets Manager**: Store OAuth client secrets, database credentials
- **IAM Roles**: Service-to-service authentication
- **Security Groups**: Network access control
- **WAF** (optional): Web application firewall

### Terraform Structure

```
terraform/
├── main.tf              # Main configuration
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── provider.tf          # AWS provider config
├── modules/
│   ├── vpc/            # VPC, subnets, routing
│   ├── ecs/            # ECS cluster, services, tasks
│   ├── rds/            # Database instance
│   ├── s3/             # S3 buckets
│   ├── cloudfront/     # CDN distribution
│   └── iam/            # IAM roles and policies
└── environments/
    ├── dev.tfvars
    └── prod.tfvars
```

**Key Terraform Resources:**
```hcl
# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "agentic-assistant-cluster"
}

# ECS Task Definition - Backend
resource "aws_ecs_task_definition" "backend" {
  family                   = "backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  
  container_definitions = jsonencode([{
    name  = "backend"
    image = "${aws_ecr_repository.backend.repository_url}:latest"
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    environment = [
      { name = "DATABASE_URL", value = "..." },
      { name = "GOOGLE_CLIENT_ID", value = "..." }
    ]
    secrets = [
      { name = "GOOGLE_CLIENT_SECRET", valueFrom = aws_secretsmanager_secret.google_oauth.arn }
    ]
  }])
}

# RDS PostgreSQL
resource "aws_db_instance" "main" {
  identifier           = "agentic-assistant-db"
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  db_name              = "assistant"
  username             = "admin"
  password             = random_password.db_password.result
  skip_final_snapshot  = true
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name = aws_db_subnet_group.main.name
}
```

### CI/CD Pipeline (GitHub Actions)

**Workflow File: `.github/workflows/deploy.yml`**
```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/
  
  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push backend
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: agentic-assistant-backend
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd backend
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
      
      - name: Build and push frontend
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: agentic-assistant-frontend
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd frontend
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
  
  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Update ECS service - Backend
        run: |
          aws ecs update-service \
            --cluster agentic-assistant-cluster \
            --service backend-service \
            --force-new-deployment
      
      - name: Update ECS service - Frontend
        run: |
          aws ecs update-service \
            --cluster agentic-assistant-cluster \
            --service frontend-service \
            --force-new-deployment
      
      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster agentic-assistant-cluster \
            --services backend-service frontend-service
```

### Docker Configuration

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified several areas of redundancy:

1. **Token refresh properties (7.5 and 8.5)**: Both Gmail and Calendar have identical token refresh requirements - these can be combined into a single OAuth token refresh property
2. **Memory metadata properties (10.2, 11.3)**: Both chat-based and data-based memory storage require metadata - these can be combined into a comprehensive memory storage property
3. **API authentication properties (7.1, 8.1)**: Both Gmail and Calendar use OAuth tokens for authentication - these can be combined into a single Google API authentication property
4. **Memory application properties (9.2, 12.3)**: Both specifically about applying communication style to drafts - these are redundant
5. **Error logging structure (15.1)**: Subsumes general error handling requirements

The following properties represent the unique, non-redundant correctness requirements for the system.

### Authentication Properties

**Property 1: OAuth Session Creation**
*For any* successful OAuth authorization response from Google, the system should create a session with encrypted access and refresh tokens that expire at the specified time.
**Validates: Requirements 1.2**

**Property 2: Session Expiry Handling**
*For any* expired session, when a user attempts an authenticated action, the system should prompt for re-authentication before proceeding.
**Validates: Requirements 1.4**

**Property 3: Logout Cleanup**
*For any* user logout action, the system should revoke the session and clear all stored tokens, such that subsequent requests require re-authentication.
**Validates: Requirements 1.5**

### Conversation Properties

**Property 4: Message Processing**
*For any* user message sent to the agent, the system should process it and return a response within the timeout period.
**Validates: Requirements 2.1, 2.3**

**Property 5: Conversation History Preservation**
*For any* sequence of messages in a conversation, the system should maintain the complete history in order, such that later messages can reference earlier context.
**Validates: Requirements 2.2**

**Property 6: User Isolation**
*For any* two distinct users with concurrent active sessions, the system should ensure that user A's conversation context is never visible to or mixed with user B's context.
**Validates: Requirements 2.4**

### MCP Integration Properties

**Property 7: Tool Result Incorporation**
*For any* MCP server tool execution that returns a result, the agent should incorporate that result into its response to the user.
**Validates: Requirements 3.3**

**Property 8: Tool Routing**
*For any* agent action requiring external tool execution, the system should route the request to the appropriate MCP server based on the action type.
**Validates: Requirements 3.2**

### Data Persistence Properties

**Property 9: Conversation Persistence**
*For any* conversation with messages, the system should store all messages with timestamps and user associations, such that they can be retrieved after system restart.
**Validates: Requirements 4.2, 4.5**

**Property 10: Memory Entry Structure**
*For any* memory entry stored in the system, it should contain content, category, source, confidence score, and timestamp metadata.
**Validates: Requirements 4.3, 10.2, 11.3**

**Property 11: Schema Migration Safety**
*For any* database schema migration, all existing user data should remain accessible and unchanged after the migration completes.
**Validates: Requirements 4.6**

### Google API Integration Properties

**Property 12: Google API Authentication**
*For any* request to Gmail or Calendar APIs, the system should authenticate using the user's stored OAuth tokens.
**Validates: Requirements 7.1, 8.1**

**Property 13: OAuth Token Refresh**
*For any* expired OAuth token, when an API request is made, the system should automatically refresh the token using the refresh token before retrying the request.
**Validates: Requirements 7.5, 8.5**

**Property 14: Email Query Filtering**
*For any* email search with specified criteria (sender, date, subject), the system should return only emails matching all specified criteria.
**Validates: Requirements 7.2**

**Property 15: Email Content Formatting**
*For any* email displayed in the chat interface, the system should format it with clear structure showing sender, subject, timestamp, and body.
**Validates: Requirements 7.3**

**Property 16: Calendar Event Query**
*For any* calendar event query with a time range, the system should return only events that overlap with the specified time range.
**Validates: Requirements 8.2**

**Property 17: Calendar Event Completeness**
*For any* calendar event displayed, the system should show title, start time, end time, location (if present), and attendees.
**Validates: Requirements 8.3**

### Email Drafting Properties

**Property 18: Draft Generation from Instructions**
*For any* user request to draft an email with specific instructions, the generated draft should address all points mentioned in the instructions.
**Validates: Requirements 9.1**

**Property 19: Draft Style Application**
*For any* email draft request, if the user has stored communication style preferences in memory, the draft should reflect those style preferences.
**Validates: Requirements 9.2, 12.3**

**Property 20: Draft Structure Completeness**
*For any* generated email draft, it should contain a subject line, greeting, body, and closing signature.
**Validates: Requirements 9.4**

**Property 21: No Unsolicited Sending**
*For any* email draft created by the system, it should never be sent without explicit user confirmation.
**Validates: Requirements 9.5**

### Memory Learning Properties (Chat)

**Property 22: Explicit Preference Extraction**
*For any* user message containing an explicit preference statement (e.g., "I prefer X", "I hate Y"), the system should extract and store that preference in the memory store.
**Validates: Requirements 10.1**

**Property 23: Preference Update on Contradiction**
*For any* new user preference that contradicts an existing stored preference, the system should update the existing memory entry with the new preference and increase its confidence.
**Validates: Requirements 10.3**

**Property 24: Memory Retrieval for Requests**
*For any* user request, the system should query the memory store and retrieve preferences relevant to that request.
**Validates: Requirements 10.4, 12.1**

**Property 25: Preference Application to Actions**
*For any* agent action (scheduling, drafting, prioritizing), if relevant preferences exist in memory, the action should respect those preferences.
**Validates: Requirements 10.5, 12.4, 12.5**

### Memory Learning Properties (Data Extraction)

**Property 26: Email Information Extraction**
*For any* email read by the agent, the system should extract and store key information such as project names, deadlines, and important contacts mentioned in the email.
**Validates: Requirements 11.1**

**Property 27: Calendar Pattern Recognition**
*For any* set of calendar events viewed by the agent, the system should identify patterns such as recurring meetings and preferred meeting times.
**Validates: Requirements 11.2**

**Property 28: Extraction Confidence Scoring**
*For any* information extracted from emails or calendar, the system should assign a confidence score based on extraction quality and clarity.
**Validates: Requirements 11.4**

**Property 29: Confidence Increase on Repetition**
*For any* piece of information that appears in multiple sources (emails, calendar, chat), the system should increase the confidence score of that memory entry.
**Validates: Requirements 11.5**

**Property 30: Extracted Context Application**
*For any* user query related to previously extracted information (projects, deadlines, contacts), the agent should use that extracted context in its response.
**Validates: Requirements 11.6**

### Memory Retrieval Properties

**Property 31: Memory Prioritization**
*For any* query that matches multiple memory entries, the system should prioritize entries by confidence score (higher first) and recency (newer first) when confidence is equal.
**Validates: Requirements 12.2**

**Property 32: Memory-Influenced Reasoning**
*For any* agent response that uses memory context to inform its answer, the response should include an explanation of how the memory influenced the reasoning.
**Validates: Requirements 12.6**

### User Interface Properties

**Property 33: Typing Indicator Display**
*For any* user message being processed by the agent, the system should display a typing indicator until the response is ready.
**Validates: Requirements 13.2**

**Property 34: Interface Load Time**
*For any* initial page load, the chat interface should be fully rendered and interactive within 3 seconds.
**Validates: Requirements 13.6**

### Security Properties

**Property 35: Token Encryption at Rest**
*For any* OAuth token stored in the database, it should be encrypted using AES-256 or equivalent encryption standard.
**Validates: Requirements 14.1**

**Property 36: Password Hashing**
*For any* password stored in the system, it should be hashed using bcrypt with a salt, never stored in plaintext.
**Validates: Requirements 14.3**

**Property 37: Rate Limiting**
*For any* API endpoint, if a user exceeds the rate limit threshold (e.g., 100 requests per minute), subsequent requests should be rejected with a 429 status code.
**Validates: Requirements 14.4**

**Property 38: Security Event Logging**
*For any* security-relevant event (failed login, token refresh failure, rate limit exceeded), the system should create a log entry with timestamp and user context.
**Validates: Requirements 14.5**

**Property 39: Email Content Minimization**
*For any* email processed by the system, only extracted key information should be stored long-term; full email content should not be retained beyond the current session.
**Validates: Requirements 14.6**

**Property 40: Account Deletion Completeness**
*For any* user account deletion request, all associated data (conversations, messages, memory entries, sessions) should be removed from the database within 24 hours.
**Validates: Requirements 14.7**

### Error Handling Properties

**Property 41: Error Logging Structure**
*For any* error that occurs during system operation, the system should log it with timestamp, user context (if available), error type, and stack trace.
**Validates: Requirements 15.1**

**Property 42: Safe Error Messages**
*For any* error returned to the user, the error message should be user-friendly and should not expose internal system details (stack traces, database queries, API keys).
**Validates: Requirements 15.2**

**Property 43: Metrics Tracking**
*For any* API request, the system should track and store metrics including response time, success/failure status, and endpoint called.
**Validates: Requirements 15.4**

**Property 44: Circuit Breaker Activation**
*For any* external API (Gmail, Calendar), if consecutive failures exceed a threshold (e.g., 5 failures), the system should open a circuit breaker and stop making requests for a cooldown period.
**Validates: Requirements 15.6**

## Error Handling

### Error Categories and Strategies

**1. Authentication Errors**
- **OAuth Failures**: Display user-friendly message, provide retry button, log failure details
- **Token Expiry**: Automatically attempt refresh, prompt for re-auth if refresh fails
- **Invalid Credentials**: Clear session, redirect to login, log security event

**2. API Errors**
- **Gmail/Calendar API Failures**: Implement exponential backoff, use circuit breakers, inform user of temporary unavailability
- **Rate Limit Exceeded**: Queue requests, inform user of delay, implement client-side rate limiting
- **Network Timeouts**: Retry with exponential backoff (max 3 retries), fallback to cached data if available

**3. Database Errors**
- **Connection Failures**: Implement connection pooling with retry logic, alert administrators
- **Query Failures**: Log full error context, return generic error to user, rollback transactions
- **Migration Failures**: Halt deployment, alert administrators, maintain backup for rollback

**4. Agent Processing Errors**
- **LLM API Failures**: Retry with exponential backoff, fallback to simpler response, inform user
- **Tool Execution Failures**: Log tool error, inform user which action failed, suggest alternatives
- **Memory Extraction Failures**: Log extraction error, continue without storing memory, don't block user interaction

**5. User Input Errors**
- **Invalid Message Format**: Return helpful error explaining expected format
- **Empty Messages**: Prevent submission on frontend, validate on backend
- **Malicious Input**: Sanitize input, log security event, rate limit user if pattern detected

### Error Response Format

```python
class ErrorResponse(BaseModel):
    error: str  # User-friendly error message
    error_code: str  # Machine-readable error code (e.g., "AUTH_FAILED")
    request_id: str  # For support/debugging
    retry_after: Optional[int] = None  # Seconds to wait before retry (for rate limits)
    
# Example error responses
{
    "error": "Unable to access your Gmail. Please reconnect your Google account.",
    "error_code": "GMAIL_AUTH_FAILED",
    "request_id": "req_abc123"
}

{
    "error": "Too many requests. Please wait a moment before trying again.",
    "error_code": "RATE_LIMIT_EXCEEDED",
    "request_id": "req_def456",
    "retry_after": 60
}
```

### Circuit Breaker Implementation

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise CircuitBreakerOpenError("Service temporarily unavailable")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise e
```

### Logging Strategy

**Log Levels:**
- **DEBUG**: Detailed information for debugging (not in production)
- **INFO**: General informational messages (user login, API calls)
- **WARNING**: Unexpected but handled situations (token refresh, retry attempts)
- **ERROR**: Errors that affect functionality (API failures, database errors)
- **CRITICAL**: System-wide failures requiring immediate attention

**Structured Logging Format:**
```python
{
    "timestamp": "2024-01-15T10:30:45Z",
    "level": "ERROR",
    "service": "backend",
    "user_id": "user_123",
    "request_id": "req_abc123",
    "error_type": "GmailAPIError",
    "message": "Failed to fetch emails",
    "stack_trace": "...",
    "context": {
        "query": "from:example@gmail.com",
        "attempt": 2
    }
}
```

## Testing Strategy

### Dual Testing Approach

The system requires both **unit tests** and **property-based tests** for comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs using randomized testing

Both approaches are complementary and necessary. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across a wide input space.

### Property-Based Testing Configuration

**Framework**: Use `hypothesis` for Python backend testing

**Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property
- Tag format: `# Feature: contextual-agentic-assistant, Property {number}: {property_text}`

**Example Property Test:**
```python
from hypothesis import given, strategies as st
import pytest

# Feature: contextual-agentic-assistant, Property 5: Conversation History Preservation
@given(
    messages=st.lists(
        st.text(min_size=1, max_size=500),
        min_size=1,
        max_size=20
    )
)
@pytest.mark.property_test
def test_conversation_history_preservation(messages):
    """
    For any sequence of messages in a conversation, the system should 
    maintain the complete history in order.
    """
    conversation_id = create_conversation()
    
    # Send all messages
    for msg in messages:
        send_message(conversation_id, msg)
    
    # Retrieve history
    history = get_conversation_history(conversation_id)
    
    # Verify all messages present in order
    assert len(history) == len(messages)
    for i, msg in enumerate(messages):
        assert history[i].content == msg
```

### Unit Testing Strategy

**Focus Areas for Unit Tests:**
1. **Specific Examples**: Test concrete scenarios (e.g., test user login flow with specific credentials)
2. **Edge Cases**: Empty inputs, boundary values, special characters
3. **Error Conditions**: API failures, network timeouts, invalid tokens
4. **Integration Points**: Component interactions, database operations

**Example Unit Test:**
```python
def test_oauth_callback_with_valid_code():
    """Test OAuth callback with a valid authorization code"""
    code = "valid_auth_code_123"
    response = client.post("/api/auth/callback", json={"code": code})
    
    assert response.status_code == 200
    assert "token" in response.json()
    assert "user" in response.json()
    
    # Verify session created
    session = get_session_by_token(response.json()["token"])
    assert session is not None
    assert session.access_token_encrypted is not None
```

### Test Coverage Goals

- **Unit Test Coverage**: Minimum 80% code coverage
- **Property Test Coverage**: All 44 correctness properties implemented
- **Integration Test Coverage**: All API endpoints tested
- **E2E Test Coverage**: Critical user flows (login, chat, email reading)

### Testing Phases

**Phase 1 - Foundation Testing:**
- Authentication flow (OAuth, session management)
- Chat interface (message sending, history)
- Database operations (CRUD for all models)
- Infrastructure (health checks, deployment verification)

**Phase 2 - Integration Testing:**
- Gmail API integration (read, search, format)
- Calendar API integration (list events, check availability)
- MCP server tool execution
- Token refresh flows

**Phase 3 - Memory System Testing:**
- Preference extraction from chat
- Information extraction from emails/calendar
- Memory retrieval and prioritization
- Memory application to actions (drafts, suggestions)

### CI/CD Testing Integration

```yaml
# In .github/workflows/deploy.yml
- name: Run Unit Tests
  run: |
    cd backend
    pytest tests/unit/ -v --cov=. --cov-report=xml

- name: Run Property Tests
  run: |
    cd backend
    pytest tests/property/ -v --hypothesis-profile=ci

- name: Run Integration Tests
  run: |
    cd backend
    pytest tests/integration/ -v

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./backend/coverage.xml
```

### Manual Testing Checklist

**Pre-Deployment Verification:**
- [ ] User can log in via Google OAuth
- [ ] User can send messages and receive responses
- [ ] Conversation history persists across page refreshes
- [ ] Gmail integration works (read emails)
- [ ] Calendar integration works (view events)
- [ ] Memory system stores preferences from chat
- [ ] Memory system extracts info from emails
- [ ] Drafts apply learned communication style
- [ ] System accessible via public HTTPS URL
- [ ] CI/CD pipeline completes successfully
- [ ] AWS Console shows all services running

## Deployment Considerations

### Environment Variables

```bash
# Backend Environment Variables
DATABASE_URL=postgresql://user:pass@host:5432/dbname
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=stored-in-secrets-manager
GOOGLE_REDIRECT_URI=https://your-domain.com/api/auth/callback
JWT_SECRET_KEY=stored-in-secrets-manager
OPENAI_API_KEY=stored-in-secrets-manager
ENVIRONMENT=production
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=100
SESSION_TIMEOUT_HOURS=24
```

### Secrets Management

All sensitive values stored in AWS Secrets Manager:
- Google OAuth client secret
- Database credentials
- JWT secret key
- OpenAI API key
- Encryption keys for token storage

### Monitoring and Observability

**CloudWatch Metrics:**
- API request count and latency
- Error rates by endpoint
- Database connection pool usage
- Memory usage and CPU utilization
- LLM API call count and latency

**CloudWatch Alarms:**
- High error rate (> 5% of requests)
- High latency (p99 > 5 seconds)
- Database connection failures
- ECS task failures
- Low disk space

**Logging:**
- All logs sent to CloudWatch Logs
- Structured JSON format for easy parsing
- Log retention: 30 days
- Critical errors trigger SNS notifications

### Scaling Considerations

**Horizontal Scaling:**
- ECS Fargate auto-scaling based on CPU/memory
- Target: 70% CPU utilization
- Min tasks: 2, Max tasks: 10

**Database Scaling:**
- RDS read replicas for read-heavy workloads
- Connection pooling (max 20 connections per backend instance)
- Query optimization and indexing

**Caching Strategy:**
- Redis for session storage (optional)
- CloudFront for frontend static assets
- Memory cache for frequently accessed user preferences

### Cost Optimization

**Phase 1 (MVP):**
- ECS Fargate: 2 tasks (0.5 vCPU, 1GB RAM each) ≈ $30/month
- RDS t3.micro: ≈ $15/month
- API Gateway: ≈ $3.50/1M requests
- CloudFront: ≈ $0.085/GB
- **Estimated Total: $50-100/month**

**Phase 3 (Full Features):**
- Additional compute for memory processing
- Vector database for embeddings
- Increased API Gateway usage
- **Estimated Total: $150-300/month**

### Disaster Recovery

**Backup Strategy:**
- RDS automated backups (7-day retention)
- Daily snapshots of critical data
- Terraform state stored in S3 with versioning

**Recovery Procedures:**
- Database restore from snapshot (< 30 minutes)
- Infrastructure recreation via Terraform (< 15 minutes)
- Application redeployment via CI/CD (< 10 minutes)
- **Total RTO: < 1 hour**

## Security Considerations

### Authentication Security

- OAuth 2.0 with PKCE flow
- Tokens encrypted at rest using AES-256
- Tokens transmitted only over HTTPS
- Session timeout after 24 hours of inactivity
- Refresh token rotation on each use

### API Security

- Rate limiting per user (100 requests/minute)
- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- XSS prevention (output encoding)
- CSRF protection (SameSite cookies)

### Data Privacy

- Email content not stored long-term
- Memory extraction only stores key facts, not full content
- User data isolated by user_id
- Account deletion removes all user data
- GDPR compliance considerations

### Infrastructure Security

- VPC with private subnets for database
- Security groups restrict access
- IAM roles with least privilege
- Secrets in AWS Secrets Manager
- CloudTrail for audit logging
- WAF for DDoS protection (optional)

## Future Enhancements

### Phase 4 Possibilities

1. **Multi-modal Memory**: Store and retrieve images, documents, voice notes
2. **Proactive Assistance**: Agent initiates conversations based on calendar/email patterns
3. **Team Collaboration**: Shared memory across team members
4. **Advanced Analytics**: Insights dashboard on communication patterns
5. **Mobile App**: Native iOS/Android applications
6. **Voice Interface**: Speech-to-text and text-to-speech integration
7. **Third-party Integrations**: Slack, Microsoft Teams, Notion, etc.

### Scalability Roadmap

1. **Microservices Split**: Separate memory service, agent service, API service
2. **Event-Driven Architecture**: Use SQS/SNS for async processing
3. **Multi-region Deployment**: Global availability and reduced latency
4. **Advanced Caching**: Redis cluster for distributed caching
5. **GraphQL API**: More flexible frontend queries
