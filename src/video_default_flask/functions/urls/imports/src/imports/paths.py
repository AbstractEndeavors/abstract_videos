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
