
import sys
sys.path.append('..')
import doctable


if __name__ == '__main__':
    drive = doctable.Drive('credentials/client_secret_4175.json')

    target_folder_id = '1Z8QJV5B9bt-tPAwH99Y6AWYNAAh5QdWM'
    target_folder_id = '1PmxI2qgqAymh6zaHma0960SNHJRBduKr'
    drive.print_files(target_folder_id)
    drive.upload_file('/econ/home/d/dc326/research/data/nonprofits/irs_xml_dbv2_v0.db.zip', target_folder_id)
    #drive.download_file()
