# video2pdfslides

## Description

This project converts a video presentation into a deck of pdf slides by capturing screenshots of unique frames.
[YouTube demo](https://www.youtube.com/watch?v=Q0BIPYLoSBs)

## Setup

pip install -r requirements.txt

## Steps to run the code

python video2pdfslides.py <video_path>

It will capture screenshots of unique frames and save it output folder...once screenshots are captured the program is paused and the user is asked to manually verify the screenshots and delete any duplicate images. Once this is done the program continues and creates a pdf out of the screenshots.

## Example

There are two sample video avilable in "./input", you can test the code using these input by running

```python video2pdfslides.py "./input/Test Video 1.mp4" (4 unique slide)
python video2pdfslides.py "./input/Test Video 2.mp4" (19 unique slide)"```

## More

The default parameters works for a typical video presentation. But if the video presentation has lots of animations, the default parametrs won't give a good results, you may notice duplicate/missing slides. Don't worry, you can make it work for any video presentation, even the ones with animations, you just need to fine tune and figure out the right set of parametrs, The 3 most important parameters that I would recommend to get play around is "MIN_PERCENT", "MAX_PERCENT", "FGBG_HISTORY". The description of these variables can be found in code comments.

## Parameters suggested by a YouTube commentor

"""To capture statquest slides best parameters i could find are: 
    FRAME_RATE = 5, 
    FGBG_HISTORY = FRAME_RATE * 6, 
    MIN_PERCENT = 0.2, 
    MAX_PERCENT = 0.6."""

## Original developer contact info

kaushik jeyaraman: <kaushikjjj@gmail.com>

## Additions

""" Original default parameters
*   FRAME_RATE=3                  # no.of frames per second that needs to be processed, fewer the count faster the speed
*   WARMUP=FRAME_RATE             # initial number of frames to be skipped
*   FGBG_HISTORY=FRAME_RATE * 15  # no.of frames in background object
*   VAR_THRESHOLD=16              # Threshold on the squared Mahalanobis distance between the pixel and the model to decide whether a pixel is well described by the background model.
*   DETECT_SHADOWS=False          # If true, the algorithm will detect shadows and mark them.
*   MIN_PERCENT=0.1               # min % of diff between foreground and background to detect if motion has stopped
*   MAX_PERCENT=3                 # max % of diff between foreground and background to detect if frame is still in motion
"""

""" Suggested parameters from YouTube commenter
*   https://www.youtube.com/watch?v=Q0BIPYLoSBs
*   FRAME_RATE = 5
*   FGBG_HISTORY = FRAME_RATE * 6
*   MIN_PERCENT = 0.2
*   MAX_PERCENT = 0.6  
"""

OUTPUT_SLIDES_DIR='./output'      # Default = './output'
SLIDE_IMAGE_PREFIX='Image_'       # Default = 
SLIDE_COUNT_INCREMENT=10          # Default = 1; using 10 to make it easier to insert missed images 
                                    #   into the sequence in the output folder
INCLUDE_TIME_STAMP=False          # Include the time of the video whan image was captured
                                    #   Default = True = 'screenshoots_count:03'
