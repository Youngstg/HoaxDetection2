#!/usr/bin/env python3
"""
Auto-Retrain Scheduler

This scheduler periodically checks if there are enough admin-labeled samples
to trigger automatic model retraining.

Features:
- Checks training queue status every N hours
- Auto-triggers retraining when threshold (50 samples) is met
- Only uses admin-labeled data (NOT user-checked data)
- Uses incremental training (builds on previous model)
- Logs all activities

Usage:
    # Run once (for cron job):
    python auto_retrain_scheduler.py

    # Run continuously (daemon mode):
    python auto_retrain_scheduler.py --daemon --interval 6

    # Force retrain regardless of threshold:
    python auto_retrain_scheduler.py --force
"""

import os
import sys
import time
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('retrain_scheduler.log')
    ]
)
logger = logging.getLogger(__name__)


def check_and_retrain(force: bool = False) -> dict:
    """
    Check training queue and trigger retraining if threshold is met.

    Args:
        force: If True, retrain even if threshold not met

    Returns:
        dict with status information
    """
    from app.services.training_service import training_service

    logger.info("=" * 60)
    logger.info("AUTO-RETRAIN SCHEDULER CHECK")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Get current status
    status = training_service.get_training_queue_status()

    logger.info(f"Training Queue Status:")
    logger.info(f"  - Pending samples: {status.total_pending}")
    logger.info(f"  - Already trained: {status.total_trained}")
    logger.info(f"  - Threshold: {status.threshold}")
    logger.info(f"  - Ready for training: {status.ready_for_training}")

    # Check if we should retrain
    if not status.ready_for_training and not force:
        logger.info(f"Not enough samples for training. Need {status.threshold}, have {status.total_pending}")
        return {
            "action": "skip",
            "reason": f"Need {status.threshold} samples, have {status.total_pending}",
            "pending": status.total_pending,
            "threshold": status.threshold
        }

    if status.total_pending == 0:
        logger.info("No pending training data available")
        return {
            "action": "skip",
            "reason": "No pending training data",
            "pending": 0,
            "threshold": status.threshold
        }

    # Trigger retraining
    logger.info("=" * 60)
    logger.info("TRIGGERING MODEL RETRAINING")
    logger.info("=" * 60)

    try:
        result = training_service.check_and_trigger_retrain()

        if result.success:
            logger.info("RETRAINING COMPLETED SUCCESSFULLY!")
            logger.info(f"  - Samples used: {result.samples_used}")
            logger.info(f"  - Accuracy: {result.accuracy:.4f}" if result.accuracy else "")
            logger.info(f"  - F1 Score: {result.f1_score:.4f}" if result.f1_score else "")

            # Save to history
            training_service.save_training_history(result)

            return {
                "action": "retrained",
                "success": True,
                "samples_used": result.samples_used,
                "accuracy": result.accuracy,
                "f1_score": result.f1_score
            }
        else:
            logger.error(f"RETRAINING FAILED: {result.message}")
            return {
                "action": "failed",
                "success": False,
                "error": result.message
            }

    except Exception as e:
        logger.error(f"Error during retraining: {e}")
        return {
            "action": "error",
            "success": False,
            "error": str(e)
        }


def run_daemon(interval_hours: int = 6):
    """
    Run scheduler as daemon, checking every N hours.

    Args:
        interval_hours: Hours between checks
    """
    logger.info("=" * 60)
    logger.info("AUTO-RETRAIN SCHEDULER DAEMON STARTED")
    logger.info(f"Check interval: {interval_hours} hours")
    logger.info("=" * 60)

    interval_seconds = interval_hours * 3600

    while True:
        try:
            result = check_and_retrain()
            logger.info(f"Check result: {result['action']}")

        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")

        logger.info(f"Next check in {interval_hours} hours...")
        time.sleep(interval_seconds)


def main():
    parser = argparse.ArgumentParser(
        description="Auto-Retrain Scheduler for Hoax Detection Model"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as daemon (continuous mode)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=6,
        help="Check interval in hours (default: 6)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force retrain regardless of threshold"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Only show training queue status, don't retrain"
    )

    args = parser.parse_args()

    # Initialize Firebase
    from app.utils.firebase_config import initialize_firebase
    initialize_firebase()

    if args.status:
        # Only show status
        from app.services.training_service import training_service
        status = training_service.get_training_queue_status()
        print("\n" + "=" * 50)
        print("TRAINING QUEUE STATUS")
        print("=" * 50)
        print(f"Pending samples:    {status.total_pending}")
        print(f"Already trained:    {status.total_trained}")
        print(f"Threshold:          {status.threshold}")
        print(f"Ready for training: {'YES' if status.ready_for_training else 'NO'}")
        print("=" * 50)
        return

    if args.daemon:
        run_daemon(interval_hours=args.interval)
    else:
        result = check_and_retrain(force=args.force)
        print(f"\nResult: {result}")


if __name__ == "__main__":
    main()
