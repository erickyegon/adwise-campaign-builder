# AdWise AI API Documentation

## Overview

The AdWise AI Digital Marketing Campaign Builder provides a comprehensive REST API for managing AI-powered marketing campaigns. This API includes advanced features like LangChain/LangGraph/LangServe integration, real-time streaming, and sophisticated workflow orchestration.

## Base URL

```
Production: https://api.adwise.ai/api/v1
Development: http://127.0.0.1:8002/api/v1
```

## Authentication

All API endpoints require authentication using JWT tokens.

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

### Using the Token
Include the token in the Authorization header:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Core Endpoints

### Campaigns

#### List Campaigns
```http
GET /api/v1/campaigns
```

**Query Parameters:**
- `search` (string): Search campaigns by name
- `status` (string): Filter by status (draft, active, paused, completed)
- `page` (integer): Page number (default: 1)
- `size` (integer): Items per page (default: 20)

**Response:**
```json
{
  "items": [
    {
      "id": "campaign_id",
      "name": "Summer Sale Campaign",
      "description": "Promotional campaign for summer products",
      "status": "active",
      "budget": 10000.0,
      "spent": 2500.0,
      "impressions": 50000,
      "clicks": 1250,
      "conversions": 125,
      "roas": 4.2,
      "start_date": "2024-06-01T00:00:00Z",
      "end_date": "2024-08-31T23:59:59Z",
      "created_at": "2024-05-15T10:30:00Z",
      "updated_at": "2024-06-15T14:20:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

#### Create Campaign
```http
POST /api/v1/campaigns
Content-Type: application/json

{
  "name": "New Campaign",
  "description": "Campaign description",
  "budget": 5000.0,
  "start_date": "2024-07-01T00:00:00Z",
  "end_date": "2024-07-31T23:59:59Z",
  "target_audience": {
    "age_range": "25-45",
    "interests": ["technology", "gadgets"],
    "location": "United States"
  },
  "channels": ["facebook", "google", "instagram"]
}
```

### AI Content Generation

#### Generate Ad Copy
```http
POST /api/v1/ai/generate-copy
Content-Type: application/json

{
  "prompt": "Create a compelling Facebook ad for eco-friendly water bottles",
  "content_type": "social_media_ad",
  "channel": "facebook",
  "target_audience": {
    "age": "25-40",
    "interests": ["sustainability", "fitness", "health"]
  },
  "brand_guidelines": {
    "tone": "friendly and encouraging",
    "style": "casual",
    "key_messages": ["eco-friendly", "sustainable", "healthy lifestyle"]
  }
}
```

**Response:**
```json
{
  "generated_content": {
    "headline": "🌱 Hydrate Sustainably with EcoBottle!",
    "body": "Join thousands who've made the switch to our 100% recycled water bottles. Perfect for your active lifestyle while protecting our planet. 💚",
    "call_to_action": "Shop Now & Save 20%",
    "visual_suggestions": [
      "Show bottle in natural outdoor setting",
      "Include recycling symbols",
      "Use green and blue color palette"
    ]
  },
  "performance_predictions": {
    "estimated_ctr": 2.8,
    "estimated_conversion_rate": 4.2,
    "confidence_score": 0.85
  },
  "optimization_suggestions": [
    "Consider A/B testing different CTAs",
    "Test with lifestyle imagery",
    "Include customer testimonials"
  ]
}
```

## Enhanced LangChain Endpoints

### Streaming Content Generation
```http
POST /api/v1/langchain/stream-content
Content-Type: application/json

{
  "prompt": "Create a comprehensive marketing campaign for a new fitness app",
  "content_type": "campaign_strategy",
  "channel": "multi_channel",
  "target_audience": {
    "demographics": "fitness enthusiasts aged 20-35",
    "interests": ["fitness", "health", "technology"]
  },
  "brand_guidelines": {
    "tone": "motivational and supportive",
    "values": ["health", "community", "achievement"]
  }
}
```

**Response:**
```json
{
  "session_id": "stream_session_123",
  "generation_id": "gen_456",
  "status": "streaming_started",
  "websocket_url": "/api/v1/langchain/ws/streaming/stream_session_123",
  "message": "Content generation started. Connect to WebSocket for real-time updates."
}
```

### LangGraph Workflow Execution
```http
POST /api/v1/langchain/workflow/execute
Content-Type: application/json

{
  "campaign_objective": "Launch awareness campaign for new sustainable fashion brand",
  "target_audience": {
    "demographics": "environmentally conscious millennials",
    "interests": ["sustainability", "fashion", "ethical shopping"],
    "income_level": "middle to upper-middle class"
  },
  "budget": 25000.0,
  "channels": ["instagram", "facebook", "google", "tiktok"],
  "brand_guidelines": {
    "tone": "authentic and inspiring",
    "colors": ["earth tones", "green", "beige"],
    "values": ["sustainability", "transparency", "quality"]
  },
  "enable_human_review": true,
  "enable_parallel_processing": true
}
```

**Response:**
```json
{
  "status": "completed",
  "workflow_id": "workflow_789",
  "campaign": {
    "strategy": "Multi-channel awareness campaign focusing on authentic storytelling and sustainable values...",
    "ads": [
      {
        "channel": "instagram",
        "content": "🌱 Fashion that doesn't cost the Earth. Discover our new sustainable collection made from 100% organic materials...",
        "format": "carousel",
        "generated_at": "2024-06-15T14:30:00Z"
      },
      {
        "channel": "facebook",
        "content": "Join the sustainable fashion revolution. Every piece tells a story of environmental responsibility...",
        "format": "single_image",
        "generated_at": "2024-06-15T14:30:15Z"
      }
    ],
    "budget_allocation": {
      "instagram": 8000.0,
      "facebook": 7000.0,
      "google": 6000.0,
      "tiktok": 4000.0
    },
    "optimization": [
      "Focus on video content for TikTok and Instagram",
      "Use user-generated content for authenticity",
      "Implement retargeting campaigns for website visitors"
    ],
    "competitor_insights": "Analysis shows competitors focusing on price over sustainability...",
    "brand_validation": [
      {
        "channel": "instagram",
        "validation": "✅ Tone consistent with brand guidelines\n✅ Sustainability messaging prominent\n⚠️ Consider adding specific product details"
      }
    ],
    "human_review_score": 92,
    "human_approved": true,
    "execution_time": "2024-06-15T14:35:00Z"
  }
}
```

### Conversational AI
```http
POST /api/v1/langchain/conversation
Content-Type: application/json

{
  "message": "How can I improve the performance of my Facebook ads for my e-commerce store?",
  "session_id": "conv_session_456",
  "context": {
    "current_campaign": "summer_sale_2024",
    "performance_data": {
      "ctr": 1.8,
      "conversion_rate": 2.1,
      "roas": 3.2,
      "budget_spent": 5000
    },
    "industry": "e-commerce",
    "product_category": "home_decor"
  }
}
```

**Response:**
```json
{
  "session_id": "conv_session_456",
  "response": "Based on your current performance data, here are specific recommendations to improve your Facebook ads:\n\n1. **Optimize Your CTR (currently 1.8%)**:\n   - Test different ad creatives with lifestyle imagery\n   - Use video content to showcase products in use\n   - Implement dynamic product ads for retargeting\n\n2. **Improve Conversion Rate (currently 2.1%)**:\n   - Optimize your landing page for mobile users\n   - Add customer reviews and social proof\n   - Implement exit-intent popups with discount offers\n\n3. **Boost ROAS (currently 3.2)**:\n   - Focus budget on your best-performing ad sets\n   - Implement lookalike audiences based on your best customers\n   - Use seasonal messaging for summer home decor trends\n\nWould you like me to help you create specific ad copy for any of these strategies?",
  "timestamp": "2024-06-15T14:40:00Z",
  "suggestions": [
    "Create video ads showcasing products",
    "Implement retargeting campaigns",
    "Optimize landing pages",
    "Use lookalike audiences"
  ]
}
```

## WebSocket Streaming

### Connect to Streaming
```javascript
const ws = new WebSocket('ws://127.0.0.1:8002/api/v1/langchain/ws/streaming/session_id');

ws.onopen = function() {
    console.log('Connected to streaming service');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'token':
            // New token from AI generation
            console.log('New token:', data.token);
            break;
        case 'chain_start':
            // Chain step started
            console.log('Chain started:', data.chain_name);
            break;
        case 'generation_complete':
            // Generation finished
            console.log('Complete:', data.result);
            break;
        case 'error':
            // Error occurred
            console.error('Error:', data.error);
            break;
    }
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};

ws.onclose = function() {
    console.log('WebSocket connection closed');
};
```

## Analytics

### Campaign Analytics
```http
GET /api/v1/analytics/campaigns/{campaign_id}?time_range=30d
```

**Response:**
```json
{
  "campaign_id": "campaign_123",
  "time_range": "30d",
  "metrics": {
    "impressions": 125000,
    "clicks": 3750,
    "conversions": 187,
    "spend": 2500.0,
    "revenue": 9350.0,
    "ctr": 3.0,
    "conversion_rate": 4.99,
    "cpc": 0.67,
    "roas": 3.74
  },
  "daily_breakdown": [
    {
      "date": "2024-06-01",
      "impressions": 4200,
      "clicks": 126,
      "conversions": 6,
      "spend": 84.50
    }
  ],
  "channel_performance": {
    "facebook": {
      "impressions": 50000,
      "clicks": 1500,
      "conversions": 75,
      "spend": 1000.0,
      "roas": 3.5
    },
    "google": {
      "impressions": 75000,
      "clicks": 2250,
      "conversions": 112,
      "spend": 1500.0,
      "roas": 4.0
    }
  }
}
```

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "budget",
        "message": "Budget must be greater than 0"
      }
    ]
  },
  "timestamp": "2024-06-15T14:45:00Z",
  "request_id": "req_123456"
}
```

### Common Error Codes
- `AUTHENTICATION_REQUIRED` (401): Missing or invalid authentication
- `PERMISSION_DENIED` (403): Insufficient permissions
- `VALIDATION_ERROR` (422): Invalid request data
- `RESOURCE_NOT_FOUND` (404): Requested resource doesn't exist
- `RATE_LIMIT_EXCEEDED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error

## Rate Limiting

API requests are rate limited:
- **Standard endpoints**: 100 requests per minute
- **AI generation endpoints**: 20 requests per minute
- **Streaming endpoints**: 10 concurrent connections

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1624025400
```

## SDKs and Libraries

### JavaScript/TypeScript
```bash
npm install @adwise/api-client
```

```javascript
import { AdWiseClient } from '@adwise/api-client';

const client = new AdWiseClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.adwise.ai'
});

// Generate campaign
const campaign = await client.campaigns.create({
  name: 'New Campaign',
  budget: 5000
});

// Generate AI content
const content = await client.ai.generateContent({
  prompt: 'Create Facebook ad copy',
  channel: 'facebook'
});
```

### Python
```bash
pip install adwise-python
```

```python
from adwise import AdWiseClient

client = AdWiseClient(api_key='your_api_key')

# Create campaign
campaign = client.campaigns.create(
    name='New Campaign',
    budget=5000
)

# Generate content
content = client.ai.generate_content(
    prompt='Create Facebook ad copy',
    channel='facebook'
)
```

## Support

- **Documentation**: https://docs.adwise.ai
- **API Status**: https://status.adwise.ai
- **Support**: support@adwise.ai
- **GitHub**: https://github.com/adwise-ai/api-examples
