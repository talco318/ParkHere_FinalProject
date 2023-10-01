import os
import glob


def get_parking_num(pic_name: str) -> int:
    """
    Gets the number of parking slots from a YOLOv5 object detection output file.

    This function takes the name of a YOLOv5 object detection output file as input and reads the file to
    count the number of parking slots detected in the image. The YOLOv5 output file is expected to be in a
    specific format with one line for each detected object, and each line containing the object class and
    bounding box coordinates.

    :param: pic_name: Name of the YOLOv5 object detection output file without the file extension.
    :type: pic_name: str
    :return: Number of parking slots detected in the image.
    :rtype: int
    """
    num_of_park = 0
    with open('yolov5-master/runs/detect/exp/labels/' + pic_name + ".txt", 'r') as f:
        for line in f:
            values = line.split()
            integers = []

            for i in range(0, len(values), 5):
                if values[i].isdigit():
                    integers.append(int(values[i]))
                    if int(values[i]) == 0:
                        num_of_park = num_of_park + 1
    return num_of_park


def run_yolov5():
    """
    Runs YOLOv5 object detection on a specified folder of images.

    This function cleans the destination folder, sets the path to the folder containing relevant parking slots
    images, and runs the YOLOv5 object detection command using the `os.system` function. The YOLOv5 object
    detection command includes the path to the trained model weights, the option to save detection results in
    text files, and the source path for the images to be detected.

    :return: None
    :rtype: None
    """
    clean_folder()  # Clean the destination folder before running object detection
    park_path = 'relevant_parking_slots'  # Set the path to the folder containing relevant parking slots images
    os.system("py yolov5-master/detect.py --weights yolov5-master/runs/train/yolov5x_results/weights/best.pt"
              " --save-txt --exist-ok --source " + park_path)  # Run YOLO


def clean_folder():
    """
    Cleans a specified folder by deleting all files within it.

    This function takes a folder path as input, and uses the `glob` module to get a list of all files in the folder.
    It then loops through each file and attempts to delete it using the `os.remove` function. If a file is deleted
    successfully, a message is printed to indicate that the file has been deleted. If any error occurs during the
    deletion process, an error message with the details of the error is printed.

    :return: None
    :rtype: None
    """
    folder_path = "yolov5-master/runs/detect/exp/labels"  # Replace with your desired folder path
    # Get all files in the folder using glob
    files = glob.glob(os.path.join(folder_path, "*"))
    # Loop through each file and delete it
    for file in files:
        try:
            os.remove(file)  # Delete the file
            # print(f"Deleted file: {file}")
        except Exception as e:
            print(f"Failed to delete file: {file}. Error: {e}")
