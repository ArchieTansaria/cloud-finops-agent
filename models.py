from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class InstanceType(str, Enum):
    T3_MICRO = "t3.micro"
    T3_MEDIUM = "t3.medium"
    M5_LARGE = "m5.large"
    M5_XLARGE = "m5.xlarge"
    C5_2XLARGE = "c5.2xlarge"

class Instance(BaseModel):
    id: str = Field(description="Unique identifier for the instance.")
    type: InstanceType = Field(description="The AWS instance type which dictates computing power and cost.")
    cpu_utilization: float = Field(description="Current CPU utilization as a percentage (0.0 to 100.0).")
    memory_utilization: float = Field(description="Current Memory utilization as a percentage (0.0 to 100.0).")
    is_mission_critical: bool = Field(description="If True, this instance must never be modified or terminated.")
    cost_per_hour: float = Field(description="The current hourly cost of running this instance.")

class Observation(BaseModel):
    infrastructure: List[Instance] = Field(description="List of all currently running cloud instances.")
    total_hourly_cost: float = Field(description="Total hourly aggregate cost of the infrastructure.")
    active_alerts: List[str] = Field(description="Active alerts, such as SLA breaches or max capacity warnings.")

class ActionType(str, Enum):
    TERMINATE = "terminate"
    RESIZE = "resize"
    WAIT = "wait"

class Action(BaseModel):
    type: ActionType = Field(description="The operation to perform. 'wait' ends the step without changes.")
    instance_id: Optional[str] = Field(default=None, description="The ID of the instance to modify. Required for terminate and resize.")
    new_type: Optional[InstanceType] = Field(default=None, description="The new instance type. Required only for resize action.")

class Reward(BaseModel):
    score: float = Field(description="A float value representing task performance (0.0 to 1.0).")

class State(BaseModel):
    budget_saved: float = Field(description="Total dollars saved compared to original setup.")
    sla_breaches: int = Field(description="Number of times instances breached max CPU or mission critical rules.")
    steps_taken: int = Field(description="Number of actions executed.")
    original_infrastructure_state: List[Instance] = Field(description="The starting state to verify against.")
