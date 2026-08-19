# AI Media Factory

# Event Bus Architecture

Version: 1.0

Status: Future Architecture


---

# 1. Overview


Event Bus is the communication layer between independent system components.


The purpose:

- reduce coupling between modules
- allow asynchronous processing
- enable autonomous AI agents
- support horizontal scaling


Future architecture:


Component

↓

Event Bus

↓

Component



---

# 2. Current State


Current implementation:


Modular monolith.


Communication:


Services

↓

Direct method calls


No message broker is currently used.


---

# 3. Future State


Future communication model:


Research Agent

↓

Event Bus

↓

Writing Agent

↓

Event Bus

↓

Image Agent

↓

Event Bus

↓

Publishing Agent

↓

Event Bus

↓

Analytics Agent



---

# 4. Event Principles


Every event must:


- have a unique name
- contain structured data
- have timestamp
- have source component
- have event version


Example:


```json
{
  "event": "research.topic.created",
  "version": "1.0",
  "source": "research_engine",
  "timestamp": "2026-07-23T12:00:00",
  "payload": {}
}
5. Event Naming Convention

Format:

component.action.object

Examples:

research.topic.created

writing.post.generated

image.asset.created

telegram.post.published

analytics.metrics.collected

6. Core Events
Research Events

research.topic.created

Triggered when new research topic is saved.

Payload:

topic_id
title
score
sources
Writing Events

writing.brief.created

writing.post.generated

Payload:

draft_id
topic_id
content
Image Events

image.generation.requested

image.asset.created

Payload:

draft_id
image_path
model
Publishing Events

telegram.publish.requested

telegram.post.published

Payload:

channel_id
message_id
timestamp
Analytics Events

analytics.metrics.collected

Payload:

publication_id
views
engagement
7. Event Consumers

Components subscribe to required events.

Example:

Research Engine:

Produces:

research.topic.created

Writing Engine:

Consumes:

research.topic.created

Produces:

writing.post.generated

Image Engine:

Consumes:

writing.post.generated

8. Event Storage

Future options:

Redis Streams

NATS

RabbitMQ

Kafka

Current recommendation:

NATS for scalable event communication.

9. Reliability Rules

Events must support:

retry mechanism
duplicate protection
failure logging
delivery confirmation
10. Agent Communication

AI agents must not communicate directly.

Forbidden:

Research Agent

↓

Writing Agent

Correct:

Research Agent

↓

Event Bus

↓

Writing Agent

11. Future Agent Architecture

Planned agents:

Manager Agent

Responsibilities:

coordinate agents
assign tasks
monitor workflow
Research Agent

Responsibilities:

discover information
analyze sources
Writing Agent

Responsibilities:

create content
Image Agent

Responsibilities:

create visuals
Publishing Agent

Responsibilities:

publish content
Analytics Agent

Responsibilities:

analyze results
12. Migration Strategy

Migration from current architecture:

Phase 1:

Direct service communication

↓

Phase 2:

Internal event abstraction

↓

Phase 3:

Message broker

↓

Phase 4:

Distributed AI agents

13. Event Bus Rules

When adding a new event:

Required:

document event
define producer
define consumer
define schema
update architecture documentation
End of Event Bus Architecture

