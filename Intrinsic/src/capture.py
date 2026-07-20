# # src/capture.py
# import cv2
# import os

# def capture_images(config):
#     cam_index = config['camera']['index']
#     width, height = config['camera']['resolution']
#     autofocus = config['camera'].get('autofocus', 0)
#     focus_val = config['camera'].get('manual_focus_val', 15)
    
#     # Open camera with DirectShow backend for stable Windows hardware control
#     cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
    
#     # Configure hardware parameters explicitly
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
#     cap.set(cv2.CAP_PROP_AUTOFOCUS, autofocus)
#     cap.set(cv2.CAP_PROP_FOCUS, focus_val)
    
#     if not cap.isOpened():
#         print(f"Error: Could not open camera source index {cam_index} via CAP_DSHOW")
#         return

#     # Keep paths matching your framework's directory structure
#     output_dir = 'data/raw_images'
#     os.makedirs(output_dir, exist_ok=True)
    
#     existing_files = os.listdir(output_dir)
#     count = sum(1 for f in existing_files if f.startswith('calib_') and (f.endswith('.jpg') or f.endswith('.png')))

#     print("\n=== Calibration Image Capture Tool (Hardware Locked) ===")
#     print(f"Resolution: {width}x{height} | Autofocus: Disabled | Focus Value: {focus_val}")
#     print("Instructions:")
#     print("  [S]  - Capture and save current frame")
#     print("  [Q]  - Quit capture session")
#     print(f"Saving pristine frames directly to: '{output_dir}/'\n")

#     # Display preview dimensions scaled down so 1080p fits on your monitor cleanly
#     disp_w, disp_h = 960, 540

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Failed to grab video frame.")
#             break
            
#         display_frame = frame.copy()
#         status_text = f"Frames Saved: {count}"
#         cv2.putText(display_frame, status_text, (20, 40), 
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
#         preview = cv2.resize(display_frame, (disp_w, disp_h))
#         cv2.imshow("Camera Viewfinder (S to Capture, Q to Quit)", preview)
        
#         key = cv2.waitKey(1) & 0xFF
        
#         if key == ord('q') or key == 27:  # Q or ESC to stop
#             break
#         elif key == ord('s'):  # S to save snapshot
#             filename = f"{output_dir}/calib_{count:02d}.jpg"
#             # Save the raw, unscaled 'frame', not the 'preview' or 'display_frame'
#             cv2.imwrite(filename, frame)
#             print(f"Saved: {filename}")
#             count += 1

#     cap.release()
#     cv2.destroyAllWindows()
#     print(f"\nCapture session complete. Total frames available: {count}")



# src/capture.py
import cv2
import os

def capture_images(config):
    cam_index = config['camera']['index']
    width, height = config['camera']['resolution']
    autofocus = config['camera'].get('autofocus', 0)
    focus_val = config['camera'].get('manual_focus_val', 15)
    
    # Retrieve exposure settings from configuration file
    auto_exposure = config['camera'].get('auto_exposure', 0)  # Default to manual (0)
    exposure_val = config['camera'].get('exposure_val', -6)   # Default baseline step
    
    # Open camera with DirectShow backend for stable Windows hardware control
    cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print(f"Error: Could not open camera source index {cam_index} via CAP_DSHOW")
        return

    # Configure hardware parameters explicitly
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, autofocus)
    cap.set(cv2.CAP_PROP_FOCUS, focus_val)
    
    # Apply exposure configurations to lock hardware shutter intervals
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, auto_exposure)
    cap.set(cv2.CAP_PROP_EXPOSURE, exposure_val)
    
    # Keep paths matching your framework's directory structure
    output_dir = 'data/raw_images'
    os.makedirs(output_dir, exist_ok=True)
    
    existing_files = os.listdir(output_dir)
    count = sum(1 for f in existing_files if f.startswith('calib_') and (f.endswith('.jpg') or f.endswith('.png')))

    print("\n=== Calibration Image Capture Tool (Hardware Locked) ===")
    print(f"Resolution: {width}x{height}")
    print(f"Autofocus: {'Enabled' if autofocus == 1 else 'Disabled'} | Focus Value: {focus_val}")
    print(f"Auto-Exposure: {'Enabled' if auto_exposure == 1 else 'Disabled'} | Exposure Value: {exposure_val}")
    print("Instructions:")
    print("  [S]  - Capture and save current frame")
    print("  [Q]  - Quit capture session")
    print(f"Saving pristine frames directly to: '{output_dir}/'\n")

    # Display preview dimensions scaled down so 1080p fits on your monitor cleanly
    disp_w, disp_h = 960, 540

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab video frame.")
            break
            
        display_frame = frame.copy()
        status_text = f"Frames Saved: {count}"
        cv2.putText(display_frame, status_text, (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        preview = cv2.resize(display_frame, (disp_w, disp_h))
        cv2.imshow("Camera Viewfinder (S to Capture, Q to Quit)", preview)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == 27:  # Q or ESC to stop
            break
        elif key == ord('s'):  # S to save snapshot
            filename = f"{output_dir}/calib_{count:02d}.jpg"
            # Save the raw, unscaled 'frame', not the 'preview' or 'display_frame'
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")
            count += 1

    cap.release()
    cv2.destroyAllWindows()
    print(f"\nCapture session complete. Total frames available: {count}")