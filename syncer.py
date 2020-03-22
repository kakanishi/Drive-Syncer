from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import glob
import os
import re
import argparse


def set_up_drive():
    default_settings_file = 'settings.yaml'
    default_credentials_file = 'credentials.txt'
    parser = argparse.ArgumentParser()
    parser.add_argument("setting_file",
                        nargs='?',
                        default=default_settings_file,
                        help="location of the settings.yaml file")
    parser.add_argument("credentials_file",
                        nargs='?',
                        default=default_credentials_file,
                        help="location of the credentials.txt file")

    settings_file = parser.parse_args().setting_file
    credentials_file = parser.parse_args().credentials_file
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


def main():
    drive = set_up_drive()

    drive_target_dir_id = '1aZxrIFzzQ1y2TNEHjdlUEvr6D1Jpuhho'
    query = f"'{drive_target_dir_id}' in parents and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()
    for file1 in file_list:
        file1.Delete()

    sync_dir_path = os.path.join(os.path.expanduser('~'), 'Google-Drive',
                                 '_notebook')
    for filename in glob.glob(os.path.join(sync_dir_path, '*.md')):
        # Removing first 10 characters in reg ex to get rid of the _notebook\
        name_without_path = re.search(r"_notebook[^.]+\.\w+",
                                      filename).group()[10:]
        print(name_without_path)
        g_file = drive.CreateFile({"parents": [{"id": drive_target_dir_id}]})
        g_file.SetContentFile(filename)
        g_file['title'] = name_without_path
        g_file.Upload()


if __name__ == '__main__':
    main()
