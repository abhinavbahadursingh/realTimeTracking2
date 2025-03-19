import threading
import time
from firebase_auth import initialize_firebase
from gps import pixel_to_gps
from datetime import datetime

# Initialize Firebase
ref = initialize_firebase()
if ref is None:
    print("🔥 Firebase reference is NULL. Data won't be sent!")

# Store data in a queue instead of sending every frame
vehicle_queue = []
queue_lock = threading.Lock()

def track_vehicle(track_id, cx, cy, name, x1, y1, x2, y2):
    """Store all vehicle tracking data in a queue"""
    if ref is None:
        print("⚠️ Firebase not initialized. Skipping update.")
        return

    try:
        lat, lon = pixel_to_gps(cx, cy)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = {
            "vehicle_id": int(track_id),
            "longitude": str(lat),
            "latitude": str(lon),
            "entry_time": timestamp,
            "type": name,
            "bounding_box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
        }

        with queue_lock:
            vehicle_queue.append(data)
        print(f"🛠 Queued vehicle data: {data}")

    except Exception as e:
        print(f"❌ Error queuing vehicle data: {e}")

def send_to_firebase():
    """Send accumulated vehicle data to Firebase every 3 seconds"""
    while True:
        time.sleep(3)  # Send every 3 seconds

        with queue_lock:
            if not vehicle_queue:
                continue  # Skip if queue is empty

            batch_data = vehicle_queue.copy()  # Copy data to send
            vehicle_queue.clear()  # Clear queue

        try:
            for data in batch_data:
                vehicle_ref = ref.child("vehicle_Data").child("total_vehicle").child(str(data["vehicle_id"]))
                vehicle_ref.set(data)
                print(f"✅ Sent to Firebase: {data}")

        except Exception as e:
            print(f"❌ Firebase update failed: {e}")

# Start Firebase batch sending thread
firebase_thread = threading.Thread(target=send_to_firebase, daemon=True)
firebase_thread.start()
