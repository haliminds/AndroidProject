import os
import shutil
import subprocess
import click
from PIL import Image

TEMPLATEPROJECTNAME = "TemplateProject"
GRADLE_LAUNCH = "gradlew.bat"
GRADLE_OPTION = ":app:assembleDebug"

LOGO_RES = {"h": 72, "m": 48, "xh": 96, "xxh": 144, "xxxh": 192}


def replace_str_in_file(fileinout, oldstr, newstr):
    # Read in the file
    with open(fileinout, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace(oldstr, newstr)

    # Write the file out again
    with open(fileinout, 'w') as file:
        file.write(filedata)


@click.command()
@click.argument("projectname", required=True)
@click.option(
    "--html_folder",
    required=False,
    help="HTML folder for new project",
)
@click.option(
    "--logo_folder",
    required=False,
    help="HTML folder for new project",
)
def launch(projectname="", html_folder=None, logo_folder=None):
    """
    Create new Android project from Template Project

    :param projectname: name of new project
    :param html_folder: the name of html_folder
    """

    # copy folder
    shutil.copytree(TEMPLATEPROJECTNAME, projectname)

    # copy html to asset if html_folder is given
    if html_folder is not None and os.path.isdir(html_folder):
        assert(os.path.exists(os.path.join(html_folder, "index.html"))), \
            "no index.html found. Please verify your html folder, it must contains main html page called \"index.html\""
        dst_asset = os.path.join(projectname, "app", "src", "main", "assets")
        shutil.copytree(html_folder, dst_asset)

    # Copy and rescale logo
    if logo_folder is not None and os.path.isdir(logo_folder):
        # verify if ic_launcher and ic_launcher_round exist
        img_list = [
            os.path.join(logo_folder, "ic_launcher.png"),
            os.path.join(logo_folder, "ic_launcher_round.png")
        ]
        for img in img_list:
            assert (os.path.exists(img)), "no {} found.".format(os.path.basename(img))
            for prefix, size in LOGO_RES.items():
                dst = os.path.join(projectname, "app", "src", "main", "res", "mipmap-"+prefix+"dpi", os.path.basename(img))
                im = Image.open(img)
                im.thumbnail((size,size), Image.LANCZOS)
                im.save(dst, "PNG")


    # Rename files
    shutil.move(os.path.join(projectname, TEMPLATEPROJECTNAME+".iml"), os.path.join(projectname, projectname+".iml"))
    src_java = os.path.join(projectname, "app","src","main","java","com",TEMPLATEPROJECTNAME.lower())
    dest_java = os.path.join(projectname, "app", "src", "main", "java", "com", projectname.lower())
    shutil.move(src_java, dest_java)

    # replace string in file
    fileinout_list = [
        os.path.join(projectname, "app", "build.gradle"),
        os.path.join(projectname, "app", "src", "main", "AndroidManifest.xml"),
        os.path.join(projectname, "app", "src", "main", "java", "com", projectname.lower(), "MainActivity.java"),
        os.path.join(projectname, "app", "src", "main", "res", "layout", "activity_main.xml")
    ]
    for fileinout in fileinout_list:
        replace_str_in_file(fileinout, TEMPLATEPROJECTNAME.lower(), projectname.lower())

    # launch compilation
    return_code = subprocess.run([GRADLE_LAUNCH, GRADLE_OPTION], shell=True, cwd=os.path.join(os.getcwd(), projectname))

    if return_code:
        apk_folder = os.path.join(projectname, "app", "build", "outputs", "apk", "debug")
        assert(os.path.exists(os.path.join(apk_folder, "app-debug.apk")))
        os.startfile(apk_folder)


if __name__ == "__main__":
    launch()
