
import sys
sys.path.append('..')
import doctable


if __name__ == '__main__':
    drive = doctable.Drive('credentials/client_secret_4175.json')
    drive.print_files('1NHEvd4auC4jmFZbh-KUPsicYs6zVcGRf')
    drive.upload_file('tmp.txt', '1NHEvd4auC4jmFZbh-KUPsicYs6zVcGRf')

