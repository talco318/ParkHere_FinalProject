import csv
import glob
import os

import locations as loc
from snapshot import Snapshot
from locations import Location
import yolo_funcs
import firebase_admin
from firebase_admin import storage, credentials


def manager(address: str):
    """
      Manages the process of finding the best parking spot near the given address.

      This function takes an address as input and performs a series of tasks to find the best parking spot near the given
      address. It first uses a function to retrieve the latitude and longitude coordinates of the given address. Then, it
      uses these coordinates to generate an array of snapshots of the area within a 1000-meter radius. The function
      copies the good photos from this array to another folder. Next, it runs a YOLOv5 function to detect the number of
      available parking slots in each snapshot. It then runs a function to grade each snapshot based on its suitability
      for parking. The function keeps track of the snapshot with the highest grade and updates the best snapshot and its
      grade accordingly. Finally, the function translates the location of the best snapshot to an address and prints it
      to the console.

      :param: address: The address for which to find the best parking spot.
      :type: address: str
      :return: address_to_parking: The best parking spot.
      :rtype: address_to_parking: str
      """
    lat, lng = loc.get_lat_long(address)
    dest_loc = Location(lat, lng)
    snaps_arr = create_arr(dest_loc)
    download_relevant_imgs(snaps_arr)
    best_snap = None
    best_grade = 0
    yolo_funcs.run_yolov5()
    for snap in snaps_arr:
        print()
        snap.available_slots = yolo_funcs.get_parking_num(snap.name)
        print("available parking slots: ", snap.available_slots)
        print("snap after update available: ", snap)
        snap_grade = gradeSnap(address, snap)
        print("the snap grade is: ", snap_grade)
        if best_grade < snap_grade:
            best_snap = snap
            best_grade = snap_grade

    print("\n\nBest snap:", best_snap,  "\n\n")
    print("--------------------------------------------------------------------------")
    print("The best parking for you available in", loc.get_address(best_snap.location))
    print("--------------------------------------------------------------------------")
    return loc.get_address(best_snap.location)




def gradeSnap(des_string: str, snap: Snapshot) -> float:
    """
    Calculates the suitability score of a parking spot snapshot based on various factors.

    :param: des_string: The destination address for which the parking spot is being evaluated.
    :type: des_string: str
    :param: snap: The parking spot snapshot to be evaluated.
    :type: snap: Snapshot
    :return: The suitability score of the parking spot snapshot.
    :rtype: float
    """
    if snap.available_slots == 0:
        return 0
    time_to_dest = loc.get_travel_time(des_string, loc.get_address(snap.location))
    avg_time_to_park, searching_by_hour = loc.values_from_ds(snap.location.latitude, snap.location.longitude)
    parking_num = yolo_funcs.get_parking_num(snap.name)
    print("searching_by_hour: ", searching_by_hour, ", avg time to park: ", avg_time_to_park, ", time to dest: ",
          time_to_dest)
    if searching_by_hour is not None:
        grade = parking_num * 0.6 + ((60 - avg_time_to_park) * 0.1) - (searching_by_hour * 0.1 * 60) + (
                    (60 - time_to_dest) * 0.2)

    else:
        grade = parking_num * 0.65 + ((60 - avg_time_to_park) * 0.1) + ((60 - time_to_dest) * 0.25)
    return grade


def create_arr(destination: Location):
    """
    Creates an array of parking spot snapshots within a 1km radius of the given destination location.

    This function reads data from a CSV file ('Searching_for_parking.csv') and checks each row to see if the
    parking spot's location (defined by the 'Latitude_SW' and 'Longitude_SW' columns) is within a 1km radius
    of the given destination location. If it is, a new parking spot snapshot with the location and other details
    is created and added to an array.

    :param: destination: The destination location for which the parking spot snapshots are being created.
    :type: destination: Location
    :return: An array of parking spot snapshots within a 1km radius of the destination location.
    :rtype: list of Snapshot
    """
    snap_arr = []
    print("_______________________________")
    with open('Searching_for_parking.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            latitude_sw = float(row['Latitude_SW'])
            longitude_sw = float(row['Longitude_SW'])
            current_loc = Location(latitude_sw, longitude_sw)
            if loc.get_distance(destination, current_loc) < 1:  # means 1km
                # print("distance between them: ", loc.get_distance(dest, current_loc))
                # name_of_snap = str(current_loc.latitude) + ',' + str(current_loc.longitude) + ".jpg"
                name_of_snap = str(current_loc.latitude) + ',' + str(current_loc.longitude)
                new_snap = Snapshot(name=name_of_snap, location=current_loc, available_slots=0)
                snap_arr.append(new_snap)
                print("new snap in the arr: ", new_snap)
    print("_______________________________")

    return snap_arr


def clean_folder():
    """
    Deletes all files within a specified folder.

    This function takes a folder path as input and uses the `glob` module to get a list of all files within
    the folder. It then iterates through each file and attempts to delete it using the `os.remove` function.
    If the file is successfully deleted, a message is printed indicating which file was deleted. If an error
    occurs while deleting a file, an error message is printed with details of the file and the specific error.
    """

    folder_path = "relevant_parking_slots"  # Replace with your desired folder path
    # Get all files in the folder using glob
    files = glob.glob(os.path.join(folder_path, "*"))
    # Loop through each file and delete it
    for file in files:
        try:
            os.remove(file)  # Delete the file
            # print(f"Deleted file: {file}")
        except Exception as e:
            print(f"Failed to delete file: {file}. Error: {e}")


def download_relevant_imgs(snap_arr):
    """
    Downloads relevant images from a list of Snapshots.

    This function takes a list of Snapshots as input and downloads relevant images for each Snapshot. It first
    calls the `clean_folder` function to delete all files in a specified folder. Then, for each Snapshot in the
    input list, it calls the `download_image` function to download the image associated with the Snapshot's name.

    :param: snap_arr: List of Snapshots to download images for.
    :type: snap_arr: list[Snapshot]
    :return: None
    """
    clean_folder()
    for snap in snap_arr:
        download_image(snap.name)


def download_image(image_name):
    """
    Downloads an image from a cloud storage bucket.

    This function takes an image name as input and downloads the image file with the given name from a cloud
    storage bucket. The downloaded image file is saved to a local folder with the same name.

    :param: image_name: Name of the image to download.
    :type: image_name: str
    :return: None
    """
    # src_folder = 'parking'
    dst_folder = 'relevant_parking_slots'
    image_name = image_name + ".jpg"

    # create the destination folder if it doesn't exist
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    bucket = storage.bucket()
    print("searching the name ", image_name, " in the server")
    blob = bucket.get_blob(image_name)
    local_folder_path = 'relevant_parking_slots'

    blob.download_to_filename(os.path.join(local_folder_path, image_name))





def rename_jpg_files(csv_file, folder_path):
    """
    Renames JPG files in a folder based on CSV data.

    :param: csv_file: The path to the CSV file containing Latitude_SW and Longitude_SW values.
    :type: csv_file: str
    :param: folder_path: The path to the folder containing the JPG files to be renamed.
    :type: folder_path: str
    :return: True if all files are successfully renamed, False otherwise.
    :rtype: bool
    """
    # Read CSV file
    names_arr = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract Latitude_SW and Longitude_SW values from CSV row
            latitude_sw = row["Latitude_SW"]
            longitude_sw = row["Longitude_SW"]

            # Construct new filename from Latitude_SW and Longitude_SW values
            new_filename = f"{latitude_sw},{longitude_sw}"
            names_arr.append(new_filename)
            # Get list of JPG files in input path

        files = os.listdir(folder_path)

        # Iterate through the files and rename them
        for i, file in enumerate(files):
            # Construct the new file name
            new_name = os.path.join(folder_path, names_arr[i] + os.path.splitext(file)[1])
            # Rename the file
            if os.path.exists(os.path.join(folder_path, names_arr[i], '.jpg')):
                print(f"File {new_filename} already exists in the directory. Skipping renaming.")
                continue
            os.rename(os.path.join(folder_path, file), new_name)
            print(f'Renamed {file} to {names_arr[i]}')
    return True
