from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import asyncio
from enum import Enum
import pytz

# Define UTC timezone as a constant
UTC = pytz.UTC

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class TaskManager:
    """Manages tasks across all agents"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.tasks = {}
        self.task_counter = 0
        self.task_queue = asyncio.Queue()
        self.processing = False
        
    def _get_current_time(self) -> datetime:
        """Get current time in UTC"""
        return datetime.now(UTC)
    
    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime to ISO format string"""
        return dt.isoformat()
    
    def create_task(self, task_data: Dict) -> str:
        """Create a new task"""
        self.task_counter += 1
        task_id = f"TASK-{self.task_counter:04d}"
        
        current_time = self._get_current_time()
        task = {
            "id": task_id,
            "created_at": self._format_datetime(current_time),
            "status": TaskStatus.PENDING.value,
            "priority": task_data.get("priority", TaskPriority.MEDIUM.value),
            "assigned_to": task_data.get("assigned_to", None),
            "data": task_data,
            "results": None,
            "updated_at": self._format_datetime(current_time)
        }
        
        self.tasks[task_id] = task
        return task_id
    
    async def assign_task(self, task_id: str, agent: str) -> Dict:
        """Assign task to specific agent"""
        if task_id not in self.tasks:
            return {"error": "Task not found"}
        
        task = self.tasks[task_id]
        current_time = self._get_current_time()
        
        task["assigned_to"] = agent
        task["status"] = TaskStatus.IN_PROGRESS.value
        task["updated_at"] = self._format_datetime(current_time)
        
        # Process task with assigned agent
        result = await self.orchestrator.route_to_agent(agent, task["data"])
        
        task["results"] = result
        task["status"] = TaskStatus.COMPLETED.value
        task["completed_at"] = self._format_datetime(self._get_current_time())
        
        return result
    
    async def auto_assign_task(self, task_id: str) -> Dict:
        """Automatically assign task to most appropriate agent"""
        if task_id not in self.tasks:
            return {"error": "Task not found"}
        
        task = self.tasks[task_id]
        result = await self.orchestrator.analyze_and_route(task["data"])
        
        # Update task with result
        task["results"] = result
        task["status"] = TaskStatus.COMPLETED.value
        task["completed_at"] = self._format_datetime(self._get_current_time())
        task["assigned_to"] = result.get("sender", "unknown")
        
        return result
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get task status"""
        if task_id not in self.tasks:
            return {"error": "Task not found"}
        
        return {
            "id": task_id,
            "status": self.tasks[task_id]["status"],
            "assigned_to": self.tasks[task_id]["assigned_to"],
            "created_at": self.tasks[task_id]["created_at"],
            "updated_at": self.tasks[task_id]["updated_at"]
        }
    
    def get_all_tasks(self, status: Optional[TaskStatus] = None) -> List[Dict]:
        """Get all tasks, optionally filtered by status"""
        tasks = []
        
        for task_id, task in self.tasks.items():
            if status is None or task["status"] == status.value:
                tasks.append({
                    "id": task_id,
                    "status": task["status"],
                    "priority": task["priority"],
                    "assigned_to": task["assigned_to"],
                    "created_at": task["created_at"],
                    "type": task["data"].get("type", "general")
                })
        
        return sorted(tasks, key=lambda x: x["priority"], reverse=True)
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """Update task status"""
        if task_id not in self.tasks:
            return False
        
        self.tasks[task_id]["status"] = status.value
        self.tasks[task_id]["updated_at"] = self._format_datetime(self._get_current_time())
        return True
    
    def get_agent_tasks(self, agent: str) -> List[Dict]:
        """Get all tasks assigned to specific agent"""
        agent_tasks = []
        
        for task_id, task in self.tasks.items():
            if task["assigned_to"] == agent:
                agent_tasks.append({
                    "id": task_id,
                    "status": task["status"],
                    "priority": task["priority"],
                    "created_at": task["created_at"],
                    "type": task["data"].get("type", "general")
                })
        
        return agent_tasks
    
    def get_task_metrics(self) -> Dict:
        """Get task metrics"""
        metrics = {
            "total_tasks": len(self.tasks),
            "by_status": {},
            "by_agent": {},
            "average_completion_time": None,
            "overdue_tasks": 0
        }
        
        completion_times = []
        
        for task in self.tasks.values():
            # Count by status
            status = task["status"]
            metrics["by_status"][status] = metrics["by_status"].get(status, 0) + 1
            
            # Count by agent
            agent = task.get("assigned_to", "unassigned")
            metrics["by_agent"][agent] = metrics["by_agent"].get(agent, 0) + 1
            
            # Calculate completion time
            if task["status"] == TaskStatus.COMPLETED.value and "completed_at" in task:
                created = datetime.fromisoformat(task["created_at"]).replace(tzinfo=UTC)
                completed = datetime.fromisoformat(task["completed_at"]).replace(tzinfo=UTC)
                completion_times.append((completed - created).total_seconds())
        
        # Calculate average completion time
        if completion_times:
            avg_seconds = sum(completion_times) / len(completion_times)
            metrics["average_completion_time"] = str(timedelta(seconds=int(avg_seconds)))
        
        return metrics
    
    async def process_task_queue(self):
        """Process tasks from queue"""
        self.processing = True
        
        while self.processing:
            try:
                # Get task from queue with timeout
                task_data = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
                
                # Create and auto-assign task
                task_id = self.create_task(task_data)
                await self.auto_assign_task(task_id)
                
            except asyncio.TimeoutError:
                # No tasks in queue, continue
                continue
            except Exception as e:
                print(f"Error processing task: {e}")
    
    def stop_processing(self):
        """Stop processing task queue"""
        self.processing = False
    
    async def add_to_queue(self, task_data: Dict):
        """Add task to processing queue"""
        await self.task_queue.put(task_data)
    
    def export_tasks(self, format: str = "json") -> str:
        """Export tasks in specified format"""
        if format == "json":
            return json.dumps(self.tasks, indent=2)
        elif format == "summary":
            summary = []
            for task_id, task in self.tasks.items():
                summary.append(
                    f"{task_id}: {task['status']} - "
                    f"Assigned to: {task.get('assigned_to', 'None')} - "
                    f"Type: {task['data'].get('type', 'general')}"
                )
            return "\n".join(summary)
        else:
            return "Unsupported format"