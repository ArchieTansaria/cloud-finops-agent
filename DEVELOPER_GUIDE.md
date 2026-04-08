# Developer Guide: Cloud FinOps OpenEnv

Welcome to the **Cloud FinOps & Cost Optimization Agent (OpenEnv)**! This document is intended to provide complete context, architectural details, and a set of actionable next steps for any developers joining the project. 

The environment was built for the **Meta & Scaler Hackathon**.

---

## 🏗️ Project Overview

This environment evaluates reinforcement learning (RL) agents or LLMs as **Cloud FinOps Engineers**. Given a fleet of cloud compute instances, the agent must optimize costs by terminating zombie/idle resources or dynamically resizing instances based on CPU utilization heuristics.

However, the agent must strictly respect **hard operational limits**:
1. It cannot breach an 85% simulated CPU load.
2. It must not modify or terminate instances flagged as `is_mission_critical`.

Most core functionalities are already working and integrated with the OpenEnv specifications perfectly. 

## 📂 File Structure and Context

Here is a breakdown of the active files and modules in this repository:

### 1. `env.py` (Core Environment Simulator)
This is the heart of the logic, encapsulating the `CloudFinOpsEnv` class. 
- **Initialization**: Provides initial infra states across 3 specific tasks (`zombie_slayer_easy`, `right_size_medium`, `sla_defender_hard`).
- **`step()` function**: Processes an Agent's action (Terminate, Resize, or Wait). It calculates metrics, checks for SLA breaches, dynamically calculates the new CPU utilization percentages after a resize, and updates costs.
- **Reward Function `_calculate_reward()`**: Returns a standardized float score from `0.0` to `1.0` depending on cost savings minus penalties (e.g., instant `0.0` for SLA breaches).

### 2. `models.py` (Pydantic Schema Definitions)
All state management and API communication rely on strongly typed Models ensuring predictable, safe agent operations.
- `InstanceType` ENUMs map perfectly to common AWS EC2 families (`t3.micro`, `c5.2xlarge`, etc.).
- Defines standard OpenEnv components: `Observation`, `Action`, `Reward`, and `State`. Note that `memory_utilization` is tracked but less prominently scored at the moment.

### 3. `openenv.yaml` (Environment Spec)
The OpenEnv configuration connecting the OpenEnv framework to our python models and environment.
- Configures schema mappings and exposes the 3 distinct tasks to evaluator scripts.

### 4. `README.md`
The user-facing documentation for setting up the environment, describing the tasks, and outlining baseline inference.

### 5. `requirements.txt` & `Dockerfile`
Standard infrastructure elements. The Dockerfile ensures rapid containerization, crucial for deployment to **Hugging Face Spaces**. OpenEnv utilizes `app_port: 7860` as indicated in the `README`.

---

## 🚀 How it Works (The Lifecycle)

1. **Reset**: OpenEnv initializes `CloudFinOpsEnv` passing a `task_id`.
2. **Observation emission**: The environment provides a Pydantic `Observation` containing the current infra list, total cost, and any alerts.
3. **Agent Action**: The agent issues a structured `Action` (`type="resize"`, `instance_id="i-101"`, `new_type="t3.micro"`).
4. **Environment Execution**: The environment recomputes specs. (i.e. changing from an M5.XLARGE to T3.MICRO shifts raw computing requirements and inherently spikes the CPU%). If it breaches >85% CPU, an alert is triggered, and a penalty is logged in state.
5. **Reward Calculation**: An algorithmic assessment returns the episode's resulting score based strictly on the savings-to-SLA-breach ratio. 

---

## 📝 TODOs & Future Improvements

As discussed earlier, most core things are functional, but here are the immediate hand-over tasks for the next developer:

- [ ] **Memory Utilization Scoring**: Right now, `cpu_utilization` controls the scaling equations and SLA checks. Implement logic so that `memory_utilization` limits (e.g. >90%) also block down-scaling or trigger SLA breaches.
- [ ] **Expanded Instance Catalogs**: Add deeper AWS mapping or generic GCP instances into `models.py:InstanceType` and `env.py:INSTANCE_SPECS` to create more granular resizing scenarios.
- [ ] **Stress Testing Inference Script**: Improve `inference.py` bounds/prompting to robustly handle the "SLA Defender Hard" task logic.
- [ ] **Variable Workload Simulation**: Currently, the simulation works on static step evaluations. An advanced extension would randomly surge CPU loads during the optimization steps to simulate unpredictable web traffic.
- [ ] **Hugging Face Deployment Verification**: Ensure the Docker Space starts successfully on HF, properly binding the OpenEnv UI/server to port 7860.

---
*Good luck, and feel free to reach out to the original team if you encounter any roadblocks!*
