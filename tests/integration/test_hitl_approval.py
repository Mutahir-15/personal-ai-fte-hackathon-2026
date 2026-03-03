import time
import shutil
import json
import logging
from pathlib import Path
from src.config.settings import Config
from src.lib.approval_manager import ApprovalManager
from src.services.approval_watcher import ApprovalWatcher

def test_hitl_approval_flow():
    # Enable logging to see output from watcher/handler
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    print("Starting HITL Approval Integration Test...")
    
    # 1. Initialize manager and watcher
    manager = ApprovalManager(dry_run=False)
    watcher = ApprovalWatcher(dry_run=False)
    watcher.start()
    
    try:
        # 2. Create a dummy approval request
        print("Creating dummy approval request...")
        request_path = manager.create_request(
            skill="test-skill",
            action="test-action",
            description="Testing the HITL approval flow.",
            input_data={"param": "value"}
        )
        request_path = Path(request_path)
        request_id = request_path.stem
        
        print(f"Request created: {request_id} at {request_path}")
        
        # Verify it's in the pending queue
        queue = manager._get_queue()
        print(f"Pending queue after creation: {list(queue['pending'].keys())}")
        assert request_id in queue["pending"], "Request should be in pending queue"
        
        # 3. Simulate human approval (move file from Pending to Approved)
        print("Simulating human approval (moving file)...")
        approved_path = Config.APPROVED_DIR / request_path.name
        shutil.move(request_path, approved_path)
        print(f"File moved to: {approved_path}")
        
        # 4. Wait for watcher to detect and process
        print("Waiting for ApprovalWatcher to detect change (10s)...")
        time.sleep(10)
        
        # 5. Verify state update
        queue = manager._get_queue()
        print(f"Pending keys after wait: {list(queue['pending'].keys())}")
        print(f"Completed keys after wait: {list(queue['completed'].keys())}")
        assert request_id not in queue["pending"], "Request should no longer be pending"
        assert request_id in queue["completed"], "Request should be in completed queue"
        assert queue["completed"][request_id]["status"] == "approved"
        
        print("SUCCESS: HITL Approval flow verified.")
        
    finally:
        watcher.stop()
        # Cleanup
        if 'approved_path' in locals() and approved_path.exists():
            approved_path.unlink()
        if 'request_path' in locals() and request_path.exists():
            request_path.unlink()

if __name__ == "__main__":
    test_hitl_approval_flow()
