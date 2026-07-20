# src/solver.py
import cv2
import numpy as np
import glob
import json
import os

def run_calibration(config):
    # Calculate internal intersections dynamically (9x7 squares yields 8x6 intersections)
    cols = config['board']['squares_x']
    rows = config['board']['squares_y']
    inner_corners = (cols - 1, rows - 1)
    sq_size = config['board']['square_size_mm']
    use_sb = config['processing']['use_modern_sb']
    
    # Termination criteria for classic sub-pixel refinement
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    obj_points = []  # 3D points in real-world space (mm)
    img_points = []  # 2D points in image plane (pixels)
    
    # 3D coordinates template mapping (Z=0 plane)
    objp = np.zeros((inner_corners[0] * inner_corners[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:inner_corners[0], 0:inner_corners[1]].T.reshape(-1, 2) * sq_size
    
    # Gather calibration frames
    images = glob.glob('data/raw_images/*.jpg') + glob.glob('data/raw_images/*.png')
    if not images:
        raise FileNotFoundError("No calibration images found in 'data/raw_images/'!")
        
    print(f"Analyzing {len(images)} frames for {inner_corners[0]}x{inner_corners[1]} pattern intersections...")
    
    valid_frames = 0
    img_shape = None
    
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        if img_shape is None:
            img_shape = gray.shape[::-1]
            
        ret = False
        corners = None
        
        # 1. Try Modern Sector-Based Detector First
        if use_sb:
            ret, corners = cv2.findChessboardCornersSB(
                gray, inner_corners, 
                cv2.CALIB_CB_EXHAUSTIVE + cv2.CALIB_CB_ACCURACY
            )
            if ret:
                valid_frames += 1
                obj_points.append(objp)
                # findChessboardCornersSB handles sub-pixel localization natively.
                # Appending directly to avoid warping data via cornerSubPix.
                img_points.append(corners)
                continue
        
        # 2. Fallback to Classic Engine if Modern fails or is turned off
        if not ret:
            ret, corners = cv2.findChessboardCorners(
                gray, inner_corners, 
                cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FILTER_QUADS
            )
            if ret:
                valid_frames += 1
                obj_points.append(objp)
                # Manual sub-pixel refinement is strictly needed for the legacy engine
                refined_corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                img_points.append(refined_corners)
            else:
                print(f"Skipped frame: {fname}")
                
    if valid_frames < 5:
        print(f"\nError: Only detected pattern in {valid_frames} frames. Check image quality.")
        return
        
    print(f"\nCalibrating using {valid_frames} valid frames...")
    
    # Execute camera calibration camera matrix solver
    ret, K, D, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, img_shape, None, None)
    
    # Structural profile formatting
    profile = {
        "camera_metadata": {
            "device": config['camera']['name'],
            "resolution": list(img_shape)
        },
        "intrinsic_matrix_K": K.tolist(),
        "distortion_coefficients_D": D.flatten().tolist(),
        "reprojection_error_rms": ret
    }
    
    # Write calibration configuration output file
    os.makedirs('data/output', exist_ok=True)
    output_path = 'data/output/camera_calibration_profile.json'
    with open(output_path, 'w') as f:
        json.dump(profile, f, indent=4)
        
    print("Calibration Completed successfully!")
    print(f"Results saved to: {output_path}")
    print(f"RMS: {ret:.4f} pixels")