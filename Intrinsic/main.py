# main.py
import argparse
import yaml
from src.generator import generate_chessboard_pdf
from src.capture import capture_images
from src.solver import run_calibration

def load_config():
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Camera Calibration Framework")
    parser.add_argument('--step', choices=['generate', 'capture', 'calibrate'], required=True,
                        help="Specify workflow execution stage.")
    
    args = parser.parse_args()
    config = load_config()
    
    if args.step == 'generate':
        generate_chessboard_pdf(config)
    elif args.step == 'capture':
        print("\n=== Starting Image Capture Session ===")
        capture_images(config)
    elif args.step == 'calibrate':
        run_calibration(config)