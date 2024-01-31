#!/usr/bin/python3
"""
Fabric script that distributes an archive to your web servers
"""

from fabric.api import env, put, run, local
from os.path import exists
from datetime import datetime

env.hosts = ['18.204.9.29', '35.153.57.44']
env.user = 'ubuntu'
env.key_filename = '/home/Isaiah19/.ssh/id_rsa'  

def do_pack():
    """
    Create a compressed archive of web_static folder
    """
    try:
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        local("mkdir -p versions")
        filename = "versions/web_static_{}.tgz".format(current_time)
        local("tar -cvzf {} web_static".format(filename))
        return filename
    except:
        return None

def do_deploy(archive_path):
    """
    Deploy the web_static archive to web servers
    """
    if not exists(archive_path):
        return False

    try:
        # Upload the archive to /tmp/ directory on the web server
        put(archive_path, '/tmp/')

        # Create folder to uncompress the archive
        folder_name = archive_path.split('/')[-1].split('.')[0]
        run("mkdir -p /data/web_static/releases/{}/".format(folder_name))

        # Uncompress the archive to the folder on the web server
        run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/".format(
            archive_path.split('/')[-1], folder_name))

        # Remove the archive from the web server
        run("rm /tmp/{}".format(archive_path.split('/')[-1]))

        # Move contents to the proper location
        run("mv /data/web_static/releases/{}/web_static/* /data/web_static/releases/{}/"
            .format(folder_name, folder_name))

        # Remove the old symbolic link
        run("rm -rf /data/web_static/current")

        # Create a new symbolic link
        run("ln -s /data/web_static/releases/{}/ /data/web_static/current".format(folder_name))

        print("New version deployed!")

        return True
    except Exception as e:
        print(e)
        return False

if __name__ == "__main__":
    # Example usage:
    archive_path = do_pack()
    if archive_path:
        do_deploy(archive_path)

