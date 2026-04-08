from fastapi import FastAPI
from env import CloudFinOpsEnv
from models import Action

app = FastAPI(title="Cloud FinOps OpenEnv API")

# Initialize default env
env = CloudFinOpsEnv(task_id="zombie_slayer_easy")

@app.get("/")
def read_root():
    """Automated ping to Space URL - must return 200"""
    return {"status": "ok", "environment": "Cloud FinOps Agent", "ready": True}

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.post("/reset")
def reset():
    """Respond to reset() calls"""
    obs = env.reset()
    return {"observation": obs.model_dump()}

@app.post("/step")
def step(action: Action):
    """Respond to step() calls"""
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def state():
    """Respond to state() calls"""
    return {"state": env.state().model_dump()}
