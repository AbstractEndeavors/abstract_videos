import os
from urllib.parse import quote  # to URL-encode spaces, etc.

BASE_URL = "https://typicallyoutliers.com"
PDFS_DIR = '/var/www/typicallyoutliers/frontend/public/pdfs/'
IMGS_DIR = '/var/www/typicallyoutliers/frontend/public/imgs/'
TEXT_DIR = '/var/www/typicallyoutliers/frontend/public/repository/text_dir/'
VIDEO_DIR = '/var/www/typicallyoutliers/frontend/public/repository/Video/'
REPO_DIR   = "/var/www/typicallyoutliers/frontend/public/repository/"
DIR_LINKS = {REPO_DIR:'repository',TEXT_DIR:'infos',VIDEO_DIR:'videos',PDFS_DIR:'pdfs',IMGS_DIR:'imgs'}
# map each extension to the URL prefix you want:
EXT_TO_PREFIX = {
    # images → /infos/
    **dict.fromkeys(
        {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'},
        'infos'
    ),
    # videos → /videos/
    **dict.fromkeys(
        {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'},
        'videos'
    ),
    # pdfs → /pdfs/
    '.pdf': 'pdfs',
    # audio → /audios/   (if you want)
    **dict.fromkeys({'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'}, 'audios'),
    # documents → /docs/
    **dict.fromkeys({'.doc', '.docx', '.txt', '.rtf'}, 'docs'),
    # presentations → /slides/
    **dict.fromkeys({'.ppt', '.pptx'}, 'slides'),
    # spreadsheets → /sheets/
    **dict.fromkeys({'.xls', '.xlsx', '.csv'}, 'sheets')
}

def generate_media_url(fs_path: str) -> str | None:
    """
    Given an absolute path under public/repository/,
    return the external URL for it (or None if it's outside).
    """
    # make sure we have a normalized absolute path
    fs_path = os.path.abspath(fs_path)
    
    # ensure it's actually under your repository folder
    if not fs_path.startswith(REPO_DIR):
        return None

    # compute the relative path inside repository/ and URL-encode it
    rel_path = fs_path[len(REPO_DIR):]
    rel_path = quote(rel_path.replace(os.sep, '/'))

    # pick a prefix based on extension, default to "repository"
    ext = os.path.splitext(fs_path)[1].lower()
    prefix = EXT_TO_PREFIX.get(ext, 'repository')

    # build the final URL
    return f"{BASE_URL}/{prefix}/{rel_path}"

def get_link(path):
    if path:
        for key,value in DIR_LINKS.items():
            if path.startswith(key):
                rel_path = path[len(key):]
                link = f"{BASE_URL}/{value}/{rel_path}"
                return link
