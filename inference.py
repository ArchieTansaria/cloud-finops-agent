import os
import json
from openai import OpenAI
from env import CloudFinOpsEnv
from models import Action, ActionType, Observation

def main():
    api_key = os.getenv("OPENAI_API_KEY", "dummy-key")
    base_url = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("MODEL_NAME", "gpt-4o")
    hf_token = os.getenv("HF_TOKEN")
    local_image = os.getenv("LOCAL_IMAGE_NAME")
    
    # Instantiate the client
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    tasks = ["zombie_slayer_easy", "right_size_medium", "sla_defender_hard"]
    
    for task_id in tasks:
        print(f"[START] task={task_id}")
        env = CloudFinOpsEnv(task_id=task_id)
        obs = env.reset()
        
        episode_reward = 0.0
        done = False
        
        # Real inference loop using OpenAI
        # We use a system prompt to describe the environment and task goal.
        messages = [
            {"role": "system", "content": "You are a Cloud FinOps expert agent. Your goal is to optimize cloud infrastructure costs. "
                                          "You must analyze the Observation and return an Action to resize or terminate instances. "
                                          "Respect SLAs: never touch mission critical instances. Keep CPU usage <= 85%. "
                                          "Return 'wait' when you are done making changes."}
        ]
        
        while not done:
            # Add current observation to history
            messages.append({"role": "user", "content": f"Observation: {obs.model_dump_json()}"})
            
            try:
                # Call OpenAI with structured outputs enforcing the Action model
                completion = client.beta.chat.completions.parse(
                    model=model,
                    messages=messages,
                    response_format=Action,
                )
                act = completion.choices[0].message.parsed
                
                # If API fails to parse, default to WAIT
                if act is None:
                    act = Action(type=ActionType.WAIT)
                    
            except Exception as e:
                print(f"[ERROR] API Call failed: {e}")
                act = Action(type=ActionType.WAIT)
                
            print(f"[STEP] action={act.model_dump_json()}")
            
            # Step the environment
            obs, reward, done, info = env.step(act)
            episode_reward = reward
            
            # Add agent's action and reward info back to the history
            messages.append({
                "role": "assistant", 
                "content": act.model_dump_json()
            })
            messages.append({
                "role": "user",
                "content": f"Reward: {reward:.2f}. Info: {info}. Did the action succeed? Proceed with the next action."
            })
                
        print(f"[END] reward={episode_reward:.2f}")

if __name__ == "__main__":
    main()
