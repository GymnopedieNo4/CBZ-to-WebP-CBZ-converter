import os
import zipfile
import threading
from PIL import Image

## File formats to be converted to JPEG, see formats readable by Pillow in: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
INPUT_FORMAT = (".webp", ".png", ".bmp", ".dib", ".tif", ".tiff") 
ZIP_TRESHOLD = 1    # Set the minimum amount of INPUT_FORMAT files inside the Zip to mark it for conversion
JPEG_PROGRESSIVE = False  # True or False for progressive JPEG, might net slightly smaller filesize if True
JPEG_QUALITY = 75         # 0-95 Image quality, higher produces larger size but closer to source quality
JPEG_OPTIMIZE = True      # True or False, encoder will make an extra pass netting smaller filesize if True
FALLBACK_FLAG = True    # True or False, if True will continuously convert at decreasing quality until FALLBACK_RATIO is achieved
FALLBACK_RATIO = 0.8    # Maximum filesize ratio of Converted to Original files that will cause the converter...
FALLBACK_INCREMENT = 5  # ...to convert again at decreasing increments of each FALLBACK_INCREMENT for even smaller filesize


def thread_job(Jobs_list, Output_path, JPEG_current_quality):
    '''
    Open and convert image files with Pillow.
    Takes: - Jobs_list, iterable whose elements are full paths to image files.
           - Output_path, path-like object of a destination folder to save the resulting image file.
           - JPEG_current_quality, integer of the resulting JPEG saving quality
    NO returns
    '''
    for Job in Jobs_list:
        Converted_filename = os.path.splitext(os.path.basename(Job))[0] + ".jpg"
        Converted_path = os.path.abspath(Output_path + os.sep + Converted_filename)
        image_object = Image.open(Job).convert("RGB")
        image_object.save(Converted_path, format="jpeg", quality=JPEG_current_quality, optimize=JPEG_OPTIMIZE, progressive=JPEG_PROGRESSIVE)


def thread_manager(Jobs_list_for_T1, Jobs_list_for_T2, Jobs_list_for_T3, Jobs_list_for_T4, Output_path, JPEG_current_quality):
    '''
    Main manager for threading functions.
    Takes: - 4 Jobs_list, iterables whose elements are full paths to image files
           - Output_path, path-like object of a destination folder to save the resulting image file.
           - JPEG_current_quality, integer of the resulting JPEG saving quality 
    NO returns
    '''
    Thread_obj_1 = threading.Thread(target=thread_job, args=(Jobs_list_for_T1, Output_path, JPEG_current_quality))
    Thread_obj_2 = threading.Thread(target=thread_job, args=(Jobs_list_for_T2, Output_path, JPEG_current_quality))
    Thread_obj_3 = threading.Thread(target=thread_job, args=(Jobs_list_for_T3, Output_path, JPEG_current_quality))
    Thread_obj_4 = threading.Thread(target=thread_job, args=(Jobs_list_for_T4, Output_path, JPEG_current_quality))
    Thread_obj_1.start()
    Thread_obj_2.start()
    Thread_obj_3.start()
    Thread_obj_4.start()
    Thread_obj_1.join()
    Thread_obj_2.join()
    Thread_obj_3.join()
    Thread_obj_4.join()


def check_zip_content(Input_path):
    '''
    Check .CBZ & .ZIP files within path if it contains image files within acceptable ZIP_TRESHOLD.
    Takes: - Input_path, path-like object of a target folder & subfolders to check.
    Returns: - Match_paths_list, a list containing path-like objects of CBZ & ZIP within treshold.
    '''
    Match_paths_list = []
    for root, dirs, files in os.walk(Input_path):
        for file in files:
            Match_flag = False
            Match_flag_count = 0
            File_lowercase = file.lower()
            if File_lowercase.endswith(".zip") or File_lowercase.endswith(".cbz"):
                File_path = os.path.abspath(os.path.join(root, file))
                with zipfile.ZipFile(File_path, 'r') as Zip_object:
                    for Archive_content in Zip_object.namelist():
                        Archive_content_ext = os.path.splitext(Archive_content.lower())[1]
                        if Archive_content_ext in INPUT_FORMAT:
                            Match_flag_count += 1
                        if Match_flag_count >= ZIP_TRESHOLD:
                            Match_flag = True
                            break
                if Match_flag == True:
                    Match_paths_list.append(File_path)
    
    return Match_paths_list


def get_JPEG_files_size(Input_path):
    '''
    Get total size of JPEG files within a folder & its subfolder
    Takes: - Input_path, path-like object of folder to be measured
    Returns: - files_size, an integer of total files size in bytes
    '''
    files_size = 0
    for root, dirs, files in os.walk(Input_path): 
        for file in files:
            file_path = os.path.abspath(os.path.join(root, file))
            if file.lower().endswith(".jpg"):
                files_size += os.path.getsize(file_path)
    return files_size


def main():
    print("\n    ===============================================================")
    print("    ||  MULTI-FORMAT .cbz/.zip to JPEG Multi-threaded Converter  ||")
    print("    ===============================================================\n")
    print("!CAUTION! This script will change the folder structures inside the newly converted Zip file into simple root->files structure!")
    Input_path = input("Please enter the INPUT folder/directory containing .cbz/.zip files:\n> ")
    Input_path = Input_path.strip('"')
    assert os.path.exists(Input_path), "WARNING! Couldn't find the directory/Permission not obtained at the designated input."
    
    print("!CAUTION! This script will OVERWRITE any file sharing the same name & extension in TARGET/OUTPUT folder!")
    Target_path = input("Please enter the TARGET folder/directory to place the converted files:\n> ")
    Target_path = Target_path.strip('"')
    assert os.path.exists(Target_path), "WARNING! Couldn't find the directory/Permission not obtained at the designated input."
    
    print("!CAUTION! This script will DELETE any files & folders inside TEMP folder after completion!")
    Temp_path = input("Please enter the empty TEMP folder/directory for temporary files needed during conversion:\n> ")
    Temp_path = Temp_path.strip('"')
    if not os.path.exists(Temp_path):
        os.makedirs(Temp_path)
    
    
    print("\n~~Checking the CBZ/ZIP for files of accepted formats inside within treshold...")
    Match_paths_list = check_zip_content(Input_path)
    
    Match_total_count = len(Match_paths_list)
    print(f"~Found {Match_total_count} archives with atleast {ZIP_TRESHOLD} accepted file within.")
    print("~~Starting the conversion process...")
    print("~Establishing TEMP folders.")
    Extracted_path = Temp_path + os.sep + "extracted"
    Converted_path = Temp_path + os.sep + "converted"
    Not_converted_path = Temp_path + os.sep + "not_converted"
    if not os.path.exists(Extracted_path):
        os.makedirs(Extracted_path)
    if not os.path.exists(Converted_path):
        os.makedirs(Converted_path)
    if not os.path.exists(Not_converted_path):
        os.makedirs(Not_converted_path)
    
    
    Convert_count = 0
    for Match_path in Match_paths_list:
        Match_filename = os.path.basename(Match_path)
        Convert_count += 1
        print(f"\n>>PROCESSING {Convert_count} OF {Match_total_count}: {Match_filename}")
        print(">Extracting archive to temp folder & moving the non-converted files...")
        with zipfile.ZipFile(Match_path, 'r') as Zip_object:
            Zip_object.extractall(path=Extracted_path)
        
        ## Parsing extracted files for files to convert and moving out files NOT to be converted
        To_convert_files_list, Not_converted_files_list = [], []
        original_filecount, original_filesize = 0, 0
        for root, dirs, files in os.walk(Extracted_path):
            for file in files:
                original_filecount += 1
                file_path = os.path.abspath(os.path.join(root, file))
                file_ext = os.path.splitext(file.lower())[1]
                if file_ext in INPUT_FORMAT:
                    To_convert_files_list.append(file_path)
                    original_filesize += os.path.getsize(file_path)
                else:
                    new_path = Not_converted_path + os.sep + file
                    os.rename(file_path, new_path)
                    Not_converted_files_list.append(new_path)
        
        print(f">Converting the images to JPEG with params: quality={JPEG_QUALITY}, optimize={JPEG_OPTIMIZE}, progressive={JPEG_PROGRESSIVE}")
        ## Dividing the job sequence to each threads, bellow is a list containing integers between 0 to len(To_convert_files_list)-1
        Sequence = list(range(len(To_convert_files_list)))
        ## 4 is thread count, Jobs_sequence is the master nested list containing list for each thread e.g. 5 by 2 =[[0,2,4],[1,3]]
        Jobs_sequence = [Sequence[a_var::4] for a_var in range(4)]
        Jobs_list_for_T1 = []
        Jobs_list_for_T2 = []
        Jobs_list_for_T3 = []
        Jobs_list_for_T4 = []
        for Seq_item in Jobs_sequence[0]:
            Jobs_list_for_T1.append(To_convert_files_list[Seq_item])
        for Seq_item in Jobs_sequence[1]:
            Jobs_list_for_T2.append(To_convert_files_list[Seq_item])
        for Seq_item in Jobs_sequence[2]:
            Jobs_list_for_T2.append(To_convert_files_list[Seq_item])
        for Seq_item in Jobs_sequence[3]:
            Jobs_list_for_T2.append(To_convert_files_list[Seq_item])
        
        
        ## First conversion, check if converted size is not acceptable then repeat ############
        JPEG_current_quality = JPEG_QUALITY
        thread_manager(Jobs_list_for_T1, Jobs_list_for_T2, Jobs_list_for_T3, Jobs_list_for_T4, Converted_path, JPEG_current_quality)
        converted_filesize = get_JPEG_files_size(Converted_path)
        
        ## No need for deletion since Pillow .save will overwrites the file ###################
        if FALLBACK_FLAG == True:
            while converted_filesize > (original_filesize * FALLBACK_RATIO):
                JPEG_current_quality -= FALLBACK_INCREMENT
                if JPEG_current_quality >= 1:
                    print(f"~Re-converting with quality of {JPEG_current_quality} as converted files are larger than the {FALLBACK_RATIO} ratio. ({(converted_filesize/(1024*1024.0)):.2f}MB to {(original_filesize/(1024*1024.0)):.2f}MB)")
                    
                    thread_manager(Jobs_list_for_T1, Jobs_list_for_T2, Jobs_list_for_T3, Jobs_list_for_T4, Converted_path, JPEG_current_quality)
                    converted_filesize = get_JPEG_files_size(Converted_path)
        
        
        ## Moving the not-converted files to be zipped together
        for filepath in Not_converted_files_list:
            new_path = Converted_path + os.sep + os.path.basename(filepath)
            os.rename(filepath, new_path)
        
        
        print(">Creating the new CBZ/ZIP archive containing converted files...")
        ## Stripping the input path/ROOT from original archive path to create 'relative path'
        relative_Target_filepath = Match_path[len(Input_path):]
        Target_filepath = Target_path + relative_Target_filepath
        Target_directory = Target_filepath.rsplit(os.sep, 1)[0]
        ## Create the directory/folders if it doesn't exist
        if not os.path.exists(Target_directory):
            os.makedirs(Target_directory)
        new_filecount = 0
        with zipfile.ZipFile(Target_filepath, 'w') as Zip_object:
            for root, dirs, files in os.walk(Converted_path):
                for file in files:
                    new_filecount += 1
                    file_path = os.path.abspath(os.path.join(root, file))
                    Zip_object.write(file_path, arcname=file)
        
        
        print(">Cleaning up the TEMP folders...")
        Deletion_files = []
        for root, dirs, files in os.walk(Temp_path):
            for file in files:
                file_path = os.path.abspath(os.path.join(root, file))
                Deletion_files.append(file_path)
        ## TO DO: Only deletes files related to the operation and leaves everything else as is
        for each_file in Deletion_files:
            os.remove(each_file) 
        
        
        original_archive_size = os.path.getsize(Match_path)/(1024*1024.0) #Divide to Megabytes size, .0 for float
        new_archive_filesize = os.path.getsize(Target_filepath)/(1024*1024.0)
        size_ratio_percent = (new_archive_filesize/original_archive_size)*100
        if new_archive_filesize >= original_archive_size:
            print(f"\n  !!!WARNING!!!  Converted archive filesize is {(size_ratio_percent-100):.2f}% larger than original filesize! ({new_archive_filesize:.2f}MB to {original_archive_size:.2f}MB)\n")
        else:
            print(f">Conversion successful! New archive is {(100-size_ratio_percent):.2f}% smaller than original filesize. ({new_archive_filesize:.2f}MB to {original_archive_size:.2f}MB)")
        
        if original_filecount != new_filecount:
            print("\n##############################################################################################")
            print("  !!!WARNING!!!  CONVERTED ARCHIVE FILECOUNT DOESN'T MATCH THE ORIGINAL ARCHIVE FILECOUNT!!!  Please check the above file for errors!\n")
    
    
    print("\n\n---------------------------------------------------------------------------------")
    print(f"~~Conversion process completed! {Match_total_count} resulting archives can be found in:\n  {Target_path}")
    print("~~Deleting TEMP folder!")
    for root, dirs, files in os.walk(Temp_path):
        for dir in dirs:
            Empty_folder = os.path.abspath(os.path.join(root, dir))
            try:
                os.rmdir(Empty_folder)
            except OSError:
                pass


if __name__ == '__main__':
    main()
    input('Press ANY KEY to exit')