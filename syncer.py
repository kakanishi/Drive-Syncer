from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import glob
import os
import re
import argparse


# TODO: alter so this can take N directories & targets
def set_up_drive(settings_file, credentials_file):
    print(
        f'Settings File Location: {settings_file} Credentials File Location: {credentials_file}'
    )
    gauth = GoogleAuth(settings_file=settings_file)
    # Try to load saved client credentials
    gauth.LoadCredentialsFile(credentials_file)
    if gauth.credentials is None:
        # Authenticate if they're not there

        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.GetFlow()
        gauth.flow.params.update({'access_type': 'offline'})
        gauth.flow.params.update({'approval_prompt': 'force'})
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile(credentials_file)
    return GoogleDrive(gauth)


def get_drive_target_dir_id(drive, drive_folder):
    folder_query = "'root' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'"
    folder_list = drive.ListFile({"q": folder_query}).GetList()
    for folder in folder_list:
        if folder['title'] == drive_folder:
            drive_target_dir_id = folder['id']
    return drive_target_dir_id


def backup_dir(drive, drive_folder, folder_to_sync):
    drive_target_dir_id = get_drive_target_dir_id(drive, drive_folder)
    # Clean all old files in target
    query = f"'{drive_target_dir_id}' in parents and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()
    for file1 in file_list:
        file1.Delete()

    # Upload local files to drive
    for file_path in glob.glob(os.path.join(folder_to_sync, '*')):
        file_name = re.split('/', file_path)[-1]
        print(file_name)
        g_file = drive.CreateFile({"parents": [{"id": drive_target_dir_id}]})
        g_file.SetContentFile(file_path)
        g_file['title'] = file_name
        g_file.Upload()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("setting_file",
                        nargs='?',
                        default='settings.yaml',
                        help="location of the settings.yaml file")
    parser.add_argument("credentials_file",
                        nargs='?',
                        default='credentials.txt',
                        help="location of the credentials.txt file")
    parser.add_argument("drive_folder", help="Path to Folder in Drive that you want to backup to")
    parser.add_argument("folder_to_sync", help="Path to Local Folder you want to sync")
    settings_file = parser.parse_args().setting_file
    credentials_file = parser.parse_args().credentials_file
    drive_folder = parser.parse_args().drive_folder
    folder_to_sync = parser.parse_args().folder_to_sync
    drive = set_up_drive(settings_file, credentials_file)
    backup_dir(drive, drive_folder, folder_to_sync)


if __name__ == '__main__':
    main()
