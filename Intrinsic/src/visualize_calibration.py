# src/visualize_calibration.py
import cv2
import numpy as np
import json
import os

def load_calibration(json_path):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Missing calibration profile at: {json_path}")
        
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    # Convert lists back into NumPy arrays for OpenCV
    mtx = np.array(data['intrinsic_matrix_K'], dtype=np.float32)
    dist = np.array(data['distortion_coefficients_D'], dtype=np.float32)
    return mtx, dist

def main():
    profile_path = 'Intrinsic\\data\\output\\camera_calibration_profile.json'
    
    try:
        mtx, dist = load_calibration(profile_path)
        print("Successfully loaded calibration parameters.")
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    # Initialize webcam with DirectShow to preserve your manual exposure settings
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print("\n--- Calibration Visualization Running ---")
    print("Hold up a straight line, grid, or target pattern to see the flattening effect.")
    print("Press 'q' to quit.")

    # Pre-calculate the optimal new camera matrix for undistortion to prevent recalculating every frame
    # alpha=0 retains all pixels but may introduce black edges where distortion is removed
    h, w = 1080, 1920
    new_camera_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 0, (w, h))

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # 1. Apply the intrinsic calibration math to flatten the image
        undistorted_frame = cv2.undistort(frame, mtx, dist, None, new_camera_mtx)

        # 2. Add visual baseline helper lines to both screens to make verification easy
        # We will draw a blue bounding box near the edges where distortion is most severe
        padding = 50
        cv2.rectangle(frame, (padding, padding), (w - padding, h - padding), (255, 0, 0), 2)
        cv2.rectangle(undistorted_frame, (padding, padding), (w - padding, h - padding), (0, 255, 0), 2)

        # 3. Add text labels
        cv2.putText(frame, "RAW DISTORTED (Notice Curved Edges)", (30, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(undistorted_frame, "CALIBRATED (Perfectly Straight)", (30, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2, cv2.LINE_AA)

        # 4. Resize frames down for side-by-side display on a standard desktop monitor
        display_w, display_h = 640, 360
        frame_sm = cv2.resize(frame, (display_w, display_h))
        undistorted_sm = cv2.resize(undistorted_frame, (display_w, display_h))

        # Combine side-by-side
        comparison_view = np.hstack((frame_sm, undistorted_sm))

        # Show the comparison window
        cv2.imshow('Calibration Real-Time Interpretation', comparison_view)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()