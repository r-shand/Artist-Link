from cx_Freeze import setup, Executable

# Include any additional files or folders you want to package with your app
include_files = [
    "always_send.txt",
    "filter.txt",
    "list.csv",
    "login-information.json",
    "scrapelist.csv",
    "scrapesettings.txt",
    "settings.txt",
    "email-templates",
    "images"
]

options = {
    "build_exe": {
        "include_files": include_files,
    }
}

setup(
    name="ArtistLink",
    version="0.0.0",
    description="Artist Scraper + Sender",
    options=options,
    executables=[Executable("ArtistLink.py", base="Win32GUI")]
)