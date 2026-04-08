---
title: Cloud FinOps OpenEnv
emoji: 🌩️
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Cloud FinOps & Cost Optimization Agent (OpenEnv)

## Environment Description and Motivation

The **Cloud FinOps Agent** is an OpenEnv native simulation of a critical real-world enterprise task: optimizing cloud computing infrastructure efficiently.
Companies waste millions of dollars annually on overprovisioned or completely idle cloud instances. This environment challenges reinforcement learning agents and LLMs to identify "zombie" infrastructure and dynamically "right-size" instances, strictly balancing cost savings against hard operational limits (such as max CPU constraints and High-Availability SLAs).

This is NOT a toy environment. It perfectly mathematically maps to actual FinOps challenges faced by AWS/GCP engineers daily.

## Setup and Usage Instructions

1. **Install OpenEnv & Requirements**
    ```bash
    pip install -r requirements.txt
    ```
2. **Validate the Environment Spec**
    ```bash
    openenv validate
    ```
3. **Run the Baseline Agent Locally**
    ```bash
    export OPENAI_API_KEY="your-key"
    python inference.py
    ```
4. **Build and Test the Docker Container**
    ```bash
    docker build -t finops_agent .
    docker run -e OPENAI_API_KEY="dummy" finops_agent
    ```

## Action and Observation Space

- **Observation Space**: A list of active Cloud `Instance` objects (metadata: `id`, `type`, `cpu_utilization`, `is_mission_critical`, `cost_per_hour`).
- **Action Space**: `terminate` (turn off the instance), `resize` (downgrade or upgrade the instance to another tier), or `wait` (end the optimization cycle).

## Tasks

We have defined 3 deterministic tasks escalating in complexity:

1. **The Zombie Slayer (Easy):**
    - _Goal:_ Terminate only the instances with 0.0% CPU utilization.
    - _Penalty:_ High penalty for terminating active workloads.

2. **The Right Sizer (Medium):**
    - _Goal:_ Resize severely overprovisioned instances (e.g., M5.XLARGE running at 4% capacity) to smaller, cheaper instances (e.g., T3.MICRO) to maximize dollar savings.
    - _Penalty:_ Auto-fails if any instance breaches 85% simulated CPU load.

3. **The SLA Defender (Hard):**
    - _Goal:_ Optimize a complex web application stack containing "mission_critical" databases.
    - _Penalty:_ Instant `0.0` score if the agent touches a `mission_critical` instance, requiring precision planning.

## Baseline Scores

Our provided `inference.py` achieves perfect scores (`1.0`) on all 3 tasks natively by correctly adhering to the grading thresholds and avoiding SLA breaches.

## Deploying to HuggingFace

Because we've fully containerized this application and correctly defined `openenv.yaml`, deploying to Hugging Face Spaces requires simply uploading this repository and selecting "Docker" space type.
