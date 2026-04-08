import copy
from typing import Any, Tuple, Dict, List
from models import Instance, Observation, Action, ActionType, Reward, State, InstanceType

# Simulated specs for instance types
INSTANCE_SPECS = {
    InstanceType.T3_MICRO: {"cpu_capacity": 10.0, "cost": 0.01},
    InstanceType.T3_MEDIUM: {"cpu_capacity": 40.0, "cost": 0.04},
    InstanceType.M5_LARGE: {"cpu_capacity": 100.0, "cost": 0.10},
    InstanceType.M5_XLARGE: {"cpu_capacity": 200.0, "cost": 0.20},
    InstanceType.C5_2XLARGE: {"cpu_capacity": 400.0, "cost": 0.35},
}

class CloudFinOpsEnv:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self._current_state = None
        self._active_alerts = []
        self._step_count = 0
        self._done = False
        
    def _get_initial_infra(self):
        if self.task_id == "zombie_slayer_easy":
            return [
                Instance(id="i-001", type=InstanceType.T3_MEDIUM, cpu_utilization=0.0, memory_utilization=0.0, is_mission_critical=False, cost_per_hour=0.04),
                Instance(id="i-002", type=InstanceType.M5_LARGE, cpu_utilization=45.0, memory_utilization=60.0, is_mission_critical=False, cost_per_hour=0.10),
                Instance(id="i-003", type=InstanceType.C5_2XLARGE, cpu_utilization=0.0, memory_utilization=0.0, is_mission_critical=False, cost_per_hour=0.35),
            ]
        elif self.task_id == "right_size_medium":
            return [
                Instance(id="i-101", type=InstanceType.M5_XLARGE, cpu_utilization=4.0, memory_utilization=10.0, is_mission_critical=False, cost_per_hour=0.20),
                Instance(id="i-102", type=InstanceType.C5_2XLARGE, cpu_utilization=5.0, memory_utilization=8.0, is_mission_critical=False, cost_per_hour=0.35),
            ]
        else: # sla_defender_hard
            return [
                Instance(id="db-master", type=InstanceType.M5_XLARGE, cpu_utilization=70.0, memory_utilization=80.0, is_mission_critical=True, cost_per_hour=0.20),
                Instance(id="worker-1", type=InstanceType.M5_LARGE, cpu_utilization=15.0, memory_utilization=20.0, is_mission_critical=False, cost_per_hour=0.10),
                Instance(id="worker-2", type=InstanceType.M5_LARGE, cpu_utilization=10.0, memory_utilization=15.0, is_mission_critical=False, cost_per_hour=0.10),
            ]

    def reset(self) -> Observation:
        infra = self._get_initial_infra()
        self._step_count = 0
        self._active_alerts = []
        self._done = False
        self._current_state = State(
            budget_saved=0.0,
            sla_breaches=0,
            steps_taken=0,
            original_infrastructure_state=copy.deepcopy(infra)
        )
        return self._build_observation(infra)

    def _build_observation(self, infra) -> Observation:
        total_cost = sum(i.cost_per_hour for i in infra)
        return Observation(infrastructure=infra, total_hourly_cost=total_cost, active_alerts=self._active_alerts)

    def state(self) -> State:
        return self._current_state

    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        if self._done:
            obs = self._build_observation(self._current_state.original_infrastructure_state)
            return obs, 0.0, True, {"msg": "Episode already done."}

        self._step_count += 1
        self._current_state.steps_taken += 1
        self._active_alerts.clear()
        
        current_infra = self._build_observation(self._current_state.original_infrastructure_state).infrastructure
        new_infra = []
        modified = False

        if action.type == ActionType.WAIT:
            self._done = True
            new_infra = copy.deepcopy(current_infra)
        else:
            for inst in current_infra:
                if inst.id == action.instance_id:
                    modified = True
                    if inst.is_mission_critical:
                        self._active_alerts.append(f"SLA BREACH: Attempted to touch mission critical instance {inst.id}")
                        self._current_state.sla_breaches += 1
                        new_infra.append(inst)
                    elif action.type == ActionType.TERMINATE:
                        if inst.cpu_utilization > 0.0 and self.task_id == "zombie_slayer_easy":
                            self._active_alerts.append(f"SLA BREACH: Terminated active instance {inst.id}!")
                            self._current_state.sla_breaches += 1
                    elif action.type == ActionType.RESIZE:
                        if not action.new_type:
                            self._active_alerts.append("Error: Action resize missing new_type")
                            new_infra.append(inst)
                            continue
                        
                        old_spec = INSTANCE_SPECS[inst.type]
                        new_spec = INSTANCE_SPECS[action.new_type]
                        
                        raw_workload = (inst.cpu_utilization / 100.0) * old_spec['cpu_capacity']
                        new_cpu_util = (raw_workload / new_spec['cpu_capacity']) * 100.0
                        
                        if new_cpu_util > 85.0:
                            self._active_alerts.append(f"SLA BREACH: Resizing {inst.id} to {action.new_type} pushes CPU to {new_cpu_util:.1f}% (>85%)")
                            self._current_state.sla_breaches += 1
                        
                        inst.type = action.new_type
                        inst.cpu_utilization = new_cpu_util
                        inst.cost_per_hour = new_spec['cost']
                        new_infra.append(inst)
                else:
                    new_infra.append(inst)

        if not modified and action.type != ActionType.WAIT:
            self._active_alerts.append(f"Error: Instance {action.instance_id} not found.")

        if self._step_count >= 5 or action.type == ActionType.WAIT:
            self._done = True
            
        reward_val = self._calculate_reward(new_infra)
        
        self._current_state.original_infrastructure_state = new_infra
        obs = self._build_observation(new_infra)
        info = {"sla_breaches": self._current_state.sla_breaches}
        
        return obs, float(reward_val), self._done, info

    def _calculate_reward(self, current_infra: List[Instance]) -> float:
        if self.task_id == "zombie_slayer_easy":
            idle_ids = ["i-001", "i-003"]
            active_id = "i-002"
            infra_ids = [i.id for i in current_infra]
            score = 0.0
            if "i-001" not in infra_ids: score += 0.5
            if "i-003" not in infra_ids: score += 0.5
            if active_id not in infra_ids: score -= 1.0 # HUGE PENALTY
            return max(0.0, score)
            
        elif self.task_id == "right_size_medium":
            start_cost = 0.55
            cur_cost = sum(i.cost_per_hour for i in current_infra)
            if self._current_state.sla_breaches > 0:
                return 0.0
            
            savings = max(0.0, start_cost - cur_cost)
            score = min(1.0, savings / 0.50)
            return score
            
        else: # sla_defender_hard
            if self._current_state.sla_breaches > 0:
                return 0.0
            cur_cost = sum(i.cost_per_hour for i in current_infra)
            savings = max(0.0, 0.40 - cur_cost)
            score = min(1.0, savings / 0.12)
            return score
