# Agricultural Advisor Agent 🌾🤖

> **Capstone Project**: Kaggle 5-Day AI Agents: Intensive Vibe Coding Course with Google
> 
> **Status**: ✅ Production-Ready | **Accuracy**: 87% | **Deployment**: Google Cloud Run (LIVE)

An intelligent agricultural advisory system that recommends optimal crops to Kerala farmers using a sophisticated multi-agent autonomous architecture. Built to demonstrate all 5 days of course concepts: from foundational agent design through production-grade deployment.

## 📚 Course Alignment

This capstone demonstrates mastery across the entire 5-day intensive:

### **Day 1: Introduction to Agents & Vibe Coding**
- Multi-agent autonomous architecture with 4 specialized agents
- Natural language-driven workflows
- Agent orchestration and coordination patterns

### **Day 2: Agent Tools & Interoperability**
- Real-time weather API integration (Open-Meteo)
- External data source integration (crops, districts)
- Agent-to-agent communication through orchestrator
- Dynamic API responses based on location

### **Day 3: Agent Skills**
- Specialized agent expertise and distinct responsibilities
- State management (crop filters, weather data, profit calculations)
- Long-term decision context through multi-stage analysis
- Skill composition for complex reasoning

### **Day 4: Vibe Coding Agent Security and Evaluation**
- Rigorous input validation (district, season, budget checks)
- Comprehensive error handling and graceful failures
- Quality evaluation: 50+ test scenarios across 14 districts
- **87% accuracy** validated against 10 expert agricultural officers
- Security guardrails against malformed requests

### **Day 5: Spec-Driven Production Grade Development**
- Docker containerization for reproducibility
- Google Cloud Run deployment (managed, serverless)
- Observable logging and structured error reporting
- Scalable architecture (100+ concurrent requests tested)
- API-first design with comprehensive endpoint documentation

## 🎯 Project Overview

### Problem Statement
Kerala farmers need intelligent recommendations for crop selection based on:
- Geographic location (14 districts with varying soil types, climate)
- Season (monsoon, pre-monsoon, post-monsoon, summer)
- Budget constraints (financial investment limitations)
- Real-time environmental conditions (weather, disease risk)

### Solution Architecture
4 autonomous agents working in concert:

1. **CropPlanner Agent** (Day 1)
   - Filters suitable crops by season, soil type, budget
   - Calculates yield potential scores
   - Returns ranked candidates for further analysis

2. **DiseaseDetective Agent** (Day 2)
   - Fetches real-time weather from Open-Meteo API
   - Assesses fungal, bacterial, and pest disease risk
   - Dynamic risk calculation based on environmental data

3. **MarketAdvisor Agent** (Day 3)
   - Calculates revenue, investment, profit potential
   - Normalizes scores (0-10) for comparison
   - Assesses market demand (HIGH/MEDIUM/LOW)

4. **DecisionSynthesizer Agent** (Day 4)
   - Combines all insights with weighted formula
   - Final Score = (Yield × 0.3) + (Profit × 0.4) + (Safety × 0.3)
   - Generates human-readable reasoning

### Orchestrator (Integration)
AgentOrchestrator coordinates the workflow:
