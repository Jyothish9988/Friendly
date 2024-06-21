import os
import cv2
from django.core.exceptions import ValidationError
from django.db import transaction
import threading
import logging
from nudenet import NudeDetector
from home.models import Post

logger = logging.getLogger(__name__)


def classify_nudity(post_id):
    try:
        from .models import Post

        with transaction.atomic():
            post = Post.objects.select_for_update().get(id=post_id)

            if post.image:
                nude_detector = NudeDetector()
                image_path = post.image.path

                logger.info(f"Processing image for Post {post_id} at path: {image_path}")

                image = cv2.imread(image_path)

                if image is None:
                    logger.error(f"Error loading image for Post {post_id} at path: {image_path}")
                    return

                logger.info(f"Image loaded successfully for Post {post_id}")

                try:
                    detections = nude_detector.detect(image_path)
                except Exception as detection_error:
                    logger.error(f"Error detecting nudity for Post {post_id}: {detection_error}")
                    return

                logger.info(f"Nudity detections for Post {post_id}: {detections}")

                ignore_classes = ['FACE_MALE', 'FACE_FEMALE', 'FEMALE_BREAST_COVERED', 'ARMPITS_EXPOSED']

                nudity_detected = any(d['class'] not in ignore_classes for d in detections)

                logger.info(f"Nudity detected for Post {post_id}: {nudity_detected}")

                new_lim = 'yes' if nudity_detected else 'no'
                try:
                    post.lim = new_lim
                    post.report = 'Explicit Image'
                    post.full_clean()
                    post.save()
                    logger.info(f"'lim' field updated for Post {post_id}")
                except ValidationError as e:
                    logger.error(f"Error updating 'lim' field for Post {post_id}: {e}")

    except Exception as e:
        logger.error(f"Error in classify_nudity task: {e}")


def run_classification_in_thread(post_id):
    thread = threading.Thread(target=classify_nudity, args=(post_id,))
    thread.start()


def video_classify_nudity(post_id):
    frames_dir = 'video_frames'
    try:
        with transaction.atomic():
            post = Post.objects.select_for_update().get(id=post_id)

            if post.video:
                nude_detector = NudeDetector()
                video_path = post.video.path

                logger.info(f"Processing video for Post {post_id} at path: {video_path}")

                os.makedirs(frames_dir, exist_ok=True)

                video_capture = cv2.VideoCapture(video_path)

                if not video_capture.isOpened():
                    logger.error(f"Error: Couldn't open the video file for Post {post_id} at path: {video_path}")
                    return

                nudity_detected = False
                nudity_class = None

                while True:
                    ret, frame = video_capture.read()

                    if not ret:
                        break

                    frame_filename = os.path.join(frames_dir,
                                                  f"frame_{int(video_capture.get(cv2.CAP_PROP_POS_FRAMES))}.jpg")
                    cv2.imwrite(frame_filename, frame)

                    try:
                        detections = nude_detector.detect(frame_filename)
                    except Exception as detection_error:
                        logger.error(f"Error detecting nudity for Post {post_id}: {detection_error}")
                        return

                    ignore_classes = ['FACE_MALE', 'FACE_FEMALE', 'FEMALE_BREAST_COVERED', 'ARMPITS_EXPOSED',
                                      'FEET_EXPOSED', 'FEET_COVERED']

                    for d in detections:
                        if d['class'] not in ignore_classes:
                            nudity_detected = True
                            nudity_class = d['class']
                            break

                    if nudity_detected:
                        break

                video_capture.release()

                new_lim = 'yes' if nudity_detected else 'no'
                try:
                    post.lim = new_lim
                    post.report = 'Explicit video'
                    post.full_clean()
                    post.save()
                    logger.info(f"'lim' field updated for Post {post_id}")
                except ValidationError as e:
                    logger.error(f"Error updating 'lim' field for Post {post_id}: {e}")

                if nudity_detected:
                    logger.info(f"Explicit nudity detected in the video for Post {post_id}. Nudity Class: {nudity_class}")
                else:
                    logger.info(f"No explicit nudity detected in the video for Post {post_id}.")

    except Exception as e:
        logger.error(f"Error in video_classify_nudity task: {e}")
    finally:
        if os.path.exists(frames_dir):
            for filename in os.listdir(frames_dir):
                file_path = os.path.join(frames_dir, filename)
                try:
                    os.remove(file_path)
                except Exception as cleanup_error:
                    logger.error(f"Error while cleaning up frame files: {cleanup_error}")

