import os
import time
import cv2
import imutils
import shutil
import img2pdf
import argparse
from pathlib import Path
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv()

# DEFINE CONSTANTS; default environment values = source code values
# Outputs
OUTPUT_SLIDES_DIR = os.environ.get('ENV_OUTPUT_SLIDES_DIR', './output')
SLIDE_IMAGE_PREFIX = os.environ.get('ENV_SLIDE_IMAGE_PREFIX',
                                    'screenshoots_count:03')
SLIDE_COUNT_INCREMENT = int(os.environ.get('ENV_SLIDE_COUNT_INCREMENT', '1'))
INCLUDE_TIME_STAMP = os.environ.get('ENV_INCLUDE_TIME_STAMP', True).lower() in ['true', 't', '1']
# Capture
FRAME_RATE = int(os.environ.get('ENV_FRAME_RATE', '3'))
WARMUP = int(os.environ.get('ENV_WARMUP', FRAME_RATE))
FGBG_HISTORY = int(os.environ.get('ENV_FGBG_HISTORY', FRAME_RATE * 15))
VAR_THRESHOLD = int(os.environ.get('ENV_VAR_THRESHOLD', '16'))
DETECT_SHADOWS = os.environ.get('ENV_DETECT_SHADOWS', False).lower() in ['true', 't', '1']
MIN_PERCENT = Decimal(os.environ.get('ENV_MIN_PERCENT', '0.1'))
MAX_PERCENT = Decimal(os.environ.get('ENV_MAX_PERCENT', '3.0'))
MANUAL_INSPECTION = os.environ.get('ENV_MANUAL_INSPECTION', False).lower() in ['true', 't', '1']


def initialize_output_folder(video_path):
    '''Clean the output folder if already exists'''
    output_folder_path = Path(OUTPUT_SLIDES_DIR) / video_path.rsplit('/')[-1].split('.')[0]
    output_folder_path_images = output_folder_path / 'images'

    # BACKLOG: add try/catch
    if output_folder_path.exists():
        shutil.rmtree(str(output_folder_path))

    output_folder_path.mkdir(parents=True, exist_ok=True)
    output_folder_path_images.mkdir(exist_ok=True)

    return output_folder_path, output_folder_path_images


def get_frames(video_path):
    '''A function to return the frames from a video located at video_path
    this function skips frames as defined in FRAME_RATE'''

    # BACKLOG: add try/catch

    # Open a pointer to the video file initialize the width and height of
    #   the frame
    vs = cv2.VideoCapture(video_path)
    if not vs.isOpened():
        raise Exception(f"Unable to open file {video_path}")

    total_frames = vs.get(cv2.CAP_PROP_FRAME_COUNT)
    frame_time = 0
    frame_count = 0
    total_frames = int(total_frames)
    print("total_frames: ", f"{total_frames:,}")

    # loop over the frames of the video
    while True:
        # grab a frame from the video
        vs.set(cv2.CAP_PROP_POS_MSEC, frame_time * 1000)
        # move frame to a timestamp
        frame_time += 1/FRAME_RATE

        (_, frame) = vs.read()
        # if the frame is None, then we have reached the end of the video file
        if frame is None:
            break

        frame_count += 1
        yield frame_count, frame_time, frame

    vs.release()


def detect_unique_screenshots(video_path, output_folder_path_images):
    ''''''
    # Initialize fgbg a Background object with Parameters
    # history = The number of frames history that effects the
    #   background subtractor
    # varThreshold = Threshold on the squared Mahalanobis distance
    #   between the pixel and the model to decide whether a pixel
    #   is well described by the background model. This parameter
    #   does not affect the background update.
    # detectShadows = If true, the algorithm will detect shadows
    #   and mark them. It decreases the speed a bit, so if you do
    #   not need this feature, set the parameter to false.

    fgbg = cv2.createBackgroundSubtractorMOG2(history=FGBG_HISTORY,
                                              varThreshold=VAR_THRESHOLD,
                                              detectShadows=DETECT_SHADOWS)
    captured = False
    start_time = time.time()
    (W, H) = (None, None)

    screenshoots_count = SLIDE_COUNT_INCREMENT
    for frame_count, frame_time, frame in get_frames(video_path):

        # BACKLOG: add try/catch

        # Clone the original frame (so we can save it later),
        orig = frame.copy()
        # Resize the frame
        frame = imutils.resize(frame, width=600)
        mask = fgbg.apply(frame)

        # apply the background subtractor
        # apply a series of erosions and dilations to eliminate noise
        # eroded_mask = cv2.erode(mask, None, iterations=2)
        # mask = cv2.dilate(mask, None, iterations=2)

        # if the width and height are empty, grab the spatial dimensions
        if W is None or H is None:
            (H, W) = mask.shape[:2]

        # compute the percentage of the mask that is "foreground"
        p_diff = (cv2.countNonZero(mask) / float(W * H)) * 100

        # If p_diff less than N% then motion has stopped,
        #   thus capture the frame
        if p_diff < MIN_PERCENT and not captured and frame_count > WARMUP:
            # BACKLOG: add try/catch
            captured = True
            file_count = get_file_count(screenshoots_count)
            filename = f"{SLIDE_IMAGE_PREFIX}{file_count}{output_time_stamp(frame_time)}.png"

            image_path = output_folder_path_images / filename

            print("Saving image", file_count)

            try:
                cv2.imwrite(str(image_path), orig)
                screenshoots_count += SLIDE_COUNT_INCREMENT
            except Exception as e:
                print(f"Error occurred while converting screenshots to PDF: {e}")
                print(f"image_path: {image_path}")

        # Otherwise, either the scene is changing or we're still in warmup
        # mode so let's wait until the scene has settled or we're finished
        # building the background model
        elif captured and p_diff >= MAX_PERCENT:
            captured = False
    print(f"{int(screenshoots_count/SLIDE_COUNT_INCREMENT)} screenshots captured!")
    print(f"Time taken {round(time.time()-start_time, 1)}s")
    return


def get_file_count(current_slide_number):
    # ensure correct sequencing for PDF page order
    match current_slide_number:
        case x if 10 <= x <= 99:
            return f"0{x}.0"
        case y if y >= 100:
            return f"{y}.0"
        case _:
            return f"00{current_slide_number}.0"


def output_time_stamp(vframe_time):
    match INCLUDE_TIME_STAMP:
        case False:
            return ''
        case _:
            return f"_{round(vframe_time/60, 2)}"


def convert_screenshots_to_pdf(output_folder_path, output_folder_path_images):
    # BACKLOG: add try/catch

    print('Converting images to pdf...')
    pdf_filename = output_folder_path.name + '.pdf' # Use the folder name as the PDF filename
    pdf_path = output_folder_path / pdf_filename    # specify the file path

    try:
        png_files = sorted(output_folder_path_images.glob('*.png'))
        with pdf_path.open('wb') as f:  # use the pdf_path to create the file
            f.write(img2pdf.convert([str(p) for p in png_files]))
        print('PDF created and saved at:', pdf_path)
    except Exception as e:
        print(f'Error occurred while converting screenshots to PDF: {e}')


if __name__ == '__main__':
    #   video_path = "./input/Test Video 2.mp4"
    #   choice = 'Y'
    #   output_folder_screenshot_path = initialize_output_folder(video_path)
    # BACKLOG: add try/catch
    parser = argparse.ArgumentParser('video_path')
    parser.add_argument('video_path',
                        help="""Path of video to be converted
                            to PDF slides""",
                        type=str)
    args = parser.parse_args()
    video_path = args.video_path

    print('video_path', video_path)
    output_folder_path, output_folder_path_images = initialize_output_folder(video_path)
    detect_unique_screenshots(video_path, output_folder_path_images)

    if MANUAL_INSPECTION:
        print('Please manually verify screenshots and delete duplicates')
        while True:
            # BACKLOG: add try/catch

            choice = input('Press Y to continue and N to terminate: ')
            choice = choice.upper().strip()
            if choice in ['Y', 'N']:
                break
            else:
                print('Please enter a valid choice')

        if choice == 'N':
            exit
    # Put a bow on that PDF!
    convert_screenshots_to_pdf(output_folder_path, output_folder_path_images)
