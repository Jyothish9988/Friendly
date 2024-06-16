# Import necessary modules
import os

from nudenet import NudeDetector
import cv2
from django.core.exceptions import ValidationError
from django.db import transaction
import threading
import logging
from background_task import background

from home.models import Post

logger = logging.getLogger(__name__)


# Define the function to classify nudity
def classify_nudity(post_id):
    try:
        from .models import Post  # Import inside the function to avoid circular import

        with transaction.atomic():
            post = Post.objects.select_for_update().get(id=post_id)  # Lock the post row for update

            if post.image:
                # Initialize the nude detector
                nude_detector = NudeDetector()

                # Read the image
                image_path = post.image.path

                print(f"Processing image for Post {post_id} at path: {image_path}")
                logger.info(f"Processing image for Post {post_id} at path: {image_path}")

                image = cv2.imread(image_path)

                if image is None:
                    print(f"Error loading image for Post {post_id} at path: {image_path}")
                    logger.error(f"Error loading image for Post {post_id} at path: {image_path}")
                    return

                print(f"Image loaded successfully for Post {post_id}")
                logger.info(f"Image loaded successfully for Post {post_id}")

                # Detect nudity in the image
                try:
                    detections = nude_detector.detect(image_path)
                except Exception as detection_error:
                    print(f"Error detecting nudity for Post {post_id}: {detection_error}")
                    logger.error(f"Error detecting nudity for Post {post_id}: {detection_error}")
                    return

                print(f"Nudity detections for Post {post_id}: {detections}")
                logger.info(f"Nudity detections for Post {post_id}: {detections}")

                # Define classes to ignore
                ignore_classes = ['FACE_MALE', 'FACE_FEMALE', 'FEMALE_BREAST_COVERED', 'ARMPITS_EXPOSED']

                # Check if any explicit nudity is detected
                nudity_detected = any(d['class'] not in ignore_classes for d in detections)
                print(f"Nudity detected for Post {post_id}: {nudity_detected}")
                logger.info(f"Nudity detected for Post {post_id}: {nudity_detected}")

                # Update the 'lim' field based on detection (with validation)
                new_lim = 'yes' if nudity_detected else 'no'
                try:
                    post.lim = new_lim
                    post.report = 'Explicit Image'
                    post.full_clean()  # Validate the model before saving
                    post.save()
                    print(f"'lim' field updated for Post {post_id}")
                    logger.info(f"'lim' field updated for Post {post_id}")
                except ValidationError as e:
                    print(f"Error updating 'lim' field for Post {post_id}: {e}")
                    logger.error(f"Error updating 'lim' field for Post {post_id}: {e}")

    except Exception as e:
        print(f"Error in classify_nudity task: {e}")
        logger.error(f"Error in classify_nudity task: {e}")


# Define a function to run classify_nudity in a thread
def run_classification_in_thread(post_id):
    thread = threading.Thread(target=classify_nudity, args=(post_id,))
    thread.start()



def video_classify_nudity(post_id):
    frames_dir = 'video_frames'  # Define frames_dir outside the try block
    try:
        with transaction.atomic():
            post = Post.objects.select_for_update().get(id=post_id)  # Lock the post row for update

            if post.video:  # Assuming the Post model has a 'video' field
                # Initialize the nude detector
                nude_detector = NudeDetector()

                # Get the video path
                video_path = post.video.path

                print(f"Processing video for Post {post_id} at path: {video_path}")
                logger.info(f"Processing video for Post {post_id} at path: {video_path}")

                # Create a directory to save frames
                os.makedirs(frames_dir, exist_ok=True)

                # Open the video file
                video_capture = cv2.VideoCapture(video_path)

                # Check if the video file is opened successfully
                if not video_capture.isOpened():
                    print(f"Error: Couldn't open the video file for Post {post_id} at path: {video_path}")
                    logger.error(f"Error: Couldn't open the video file for Post {post_id} at path: {video_path}")
                    return

                nudity_detected = False
                nudity_class = None

                # Loop through the video frames
                while True:
                    # Read a frame from the video
                    ret, frame = video_capture.read()

                    # If no frame is read, end of the video
                    if not ret:
                        break

                    # Save the frame as an image temporarily
                    frame_filename = os.path.join(frames_dir,
                                                  f"frame_{int(video_capture.get(cv2.CAP_PROP_POS_FRAMES))}.jpg")
                    cv2.imwrite(frame_filename, frame)

                    # Detect nudity in the frame
                    try:
                        detections = nude_detector.detect(frame_filename)
                    except Exception as detection_error:
                        print(f"Error detecting nudity for Post {post_id}: {detection_error}")
                        logger.error(f"Error detecting nudity for Post {post_id}: {detection_error}")
                        return

                    # Define classes to ignore
                    ignore_classes = ['FACE_MALE', 'FACE_FEMALE', 'FEMALE_BREAST_COVERED', 'ARMPITS_EXPOSED',
                                      'FEET_EXPOSED', 'FEET_COVERED']

                    # Check if any explicit nudity is detected
                    for d in detections:
                        if d['class'] not in ignore_classes:
                            nudity_detected = True
                            nudity_class = d['class']
                            break

                    # If nudity detected, break the loop
                    if nudity_detected:
                        break

                # Release the video capture
                video_capture.release()

                # Update the 'lim' field based on detection (with validation)
                new_lim = 'yes' if nudity_detected else 'no'
                try:
                    post.lim = new_lim
                    post.report = 'Explicit video'
                    post.full_clean()  # Validate the model before saving
                    post.save()
                    print(f"'lim' field updated for Post {post_id}")
                    logger.info(f"'lim' field updated for Post {post_id}")
                except ValidationError as e:
                    print(f"Error updating 'lim' field for Post {post_id}: {e}")
                    logger.error(f"Error updating 'lim' field for Post {post_id}: {e}")

                if nudity_detected:
                    print(f"Explicit nudity detected in the video for Post {post_id}. Nudity Class: {nudity_class}")
                    logger.info(
                        f"Explicit nudity detected in the video for Post {post_id}. Nudity Class: {nudity_class}")
                else:
                    print(f"No explicit nudity detected in the video for Post {post_id}.")
                    logger.info(f"No explicit nudity detected in the video for Post {post_id}.")

    except Exception as e:
        print(f"Error in video_classify_nudity task: {e}")
        logger.error(f"Error in video_classify_nudity task: {e}")
    finally:
        # Clean up: Remove the frame files
        if os.path.exists(frames_dir):
            for filename in os.listdir(frames_dir):
                file_path = os.path.join(frames_dir, filename)
                try:
                    os.remove(file_path)
                except Exception as cleanup_error:
                    print(f"Error while cleaning up frame files: {cleanup_error}")
                    logger.error(f"Error while cleaning up frame files: {cleanup_error}")
            print("Frame files cleaned up.")


