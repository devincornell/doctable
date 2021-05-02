
import sys
sys.path.append('..')
import doctable


if __name__ == '__main__':
    drive = doctable.Drive('credentials/client_secret_4175.json')

    target_folder_id = '1Z8QJV5B9bt-tPAwH99Y6AWYNAAh5QdWM'
    drive.print_files(target_folder_id)
    drive.upload_file('tmp.txt', target_folder_id)
