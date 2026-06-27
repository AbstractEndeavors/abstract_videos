from .init_imports import *
@dataclass(frozen=True)
class StorageConfig:
    videos_root: str
    documents_root: str
    registry_path: str
    js_runtime: str = "deno"  # or from env

    @classmethod
    def from_env(cls) -> "StorageConfig":
        missing = []
        default_videos_dir = get_default_videos_dir()
        registry_path = get_env_value("VIDEO_REGISTRY_PATH") or os.path.join(default_videos_dir,'video_registry.json')
        videos_root = get_env_value("VIDEOS_ROOT") or get_default_videos_dir()
        documents_root = get_env_value("DOCUMENTS_ROOT") or get_default_documents_dir()
        if not videos_root:
            missing.append("VIDEOS_ROOT")
        if not documents_root:
            missing.append("DOCUMENTS_ROOT")
        if not registry_path:
            missing.append("VIDEO_REGISTRY_PATH")
        if missing:
            raise EnvironmentError(
                f"Required env vars not set: {missing}. "
                f"Set them explicitly — no defaults are assumed."
            )
        return cls(
            videos_root=videos_root,
            documents_root=documents_root,
            registry_path=registry_path,
            js_runtime=get_env_value("YT_DLP_JS_RUNTIME") or "deno",
        )
    @classmethod
    def with_defaults(
        cls,
        videos_root: str = None,
        documents_root: str = None,
        registry_path: str = None,
        js_runtime: str = "deno",
    ) -> "StorageConfig":
        videos_root = videos_root or get_default_videos_dir()
        documents_root = documents_root or get_default_documents_dir()
        registry_path = registry_path or os.path.join(
            videos_root, "video_registry.json"
        )
        return cls(
            videos_root=videos_root,
            documents_root=documents_root,
            registry_path=registry_path,
            js_runtime=js_runtime,
        )
@dataclass(frozen=True)
class SiteConfig:
    site_name: str
    domain: str
    root_url: str
    media_root: str
    base_image_url: str

    @classmethod
    def from_env(cls) -> "SiteConfig":
        site_name = get_env_value("SITE_NAME")
        domain = get_env_value("SITE_DOMAIN")
        root_url = get_env_value("ROOT_URL")
        media_root = get_env_value("MEDIA_ROOT")
        base_image_url = get_env_value("BASE_IMAGE_URL")

        missing = [
            k for k, v in {
                "SITE_NAME": site_name,
                "SITE_DOMAIN": domain,
                "ROOT_URL": root_url,
                "MEDIA_ROOT": media_root,
                "BASE_IMAGE_URL": base_image_url,
            }.items() if not v
        ]
        if missing:
            raise EnvironmentError(f"Required env vars not set: {missing}")

        return cls(
            site_name=site_name,
            domain=domain,
            root_url=root_url,
            media_root=media_root,
            base_image_url=base_image_url,
        )

    # derived values — computed, not stored
    @property
    def video_media_root(self) -> str:
        return os.path.join(self.media_root, "videos")

    @property
    def video_public_url(self) -> str:
        return f"{self.root_url}/videos"

    @property
    def title_variants(self) -> list[str]:
        return title_variants_from_domain(self.domain)


@dataclass(frozen=True)
class AppConfig:
    site: SiteConfig
    storage: StorageConfig

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            site=SiteConfig.from_env(),
            storage=StorageConfig.from_env(),
        )

def get_videos_root(explicit: str | None = None, envPath: str | None = None) -> str:
    """
    Resolve the videos root with this priority:
      1) explicit arg
      2) env file (VIDEOS_ROOT or legacy DATA_DIRECTORY)
      3) process env (VIDEOS_ROOT or legacy DATA_DIRECTORY)
      4) hard default (/mnt/24T/media/DATA/videos)
    """
    # 1) explicit
    if explicit:
        os.makedirs(explicit, exist_ok=True)
        return explicit

    # 2) env file
    v_from_envfile = (
        get_env_value(key="VIDEOS_ROOT", path=envPath)
        or get_env_value(key="DATA_DIRECTORY", path=envPath)  # legacy
    )
    if v_from_envfile:
        os.makedirs(v_from_envfile, exist_ok=True)
        return v_from_envfile

    # 3) process env
    v_from_env = os.getenv("VIDEOS_ROOT") or os.getenv("DATA_DIRECTORY")  # legacy
    if v_from_env:
        os.makedirs(v_from_env, exist_ok=True)
        return v_from_env

    # 4) hard default
    os.makedirs(DEFAULT_VIDEOS_ROOT, exist_ok=True)
    return DEFAULT_VIDEOS_ROOT


def get_documents_root(explicit: str | None = None, envPath: str | None = None) -> str:
    """
    Same idea as get_videos_root, but for documents/registry.
    Priority: explicit -> env file DOCUMENTS_ROOT -> env DOCUMENTS_ROOT -> hard default.
    """
    if explicit:
        os.makedirs(explicit, exist_ok=True)
        return explicit

    d_from_envfile = get_env_value(key="DOCUMENTS_ROOT", path=envPath)
    if d_from_envfile:
        os.makedirs(d_from_envfile, exist_ok=True)
        return d_from_envfile

    d_from_env = os.getenv("DOCUMENTS_ROOT")
    if d_from_env:
        os.makedirs(d_from_env, exist_ok=True)
        return d_from_env

    os.makedirs(DEFAULT_DOCUMENTS_ROOT, exist_ok=True)
    return DEFAULT_DOCUMENTS_ROOT


def get_video_directory(key: str | None = None, envPath: str | None = None, videos_root: str | None = None) -> str:
    """
    Assure that a valid *videos* directory exists and return its path.

    Priority:
      - videos_root arg (if passed)
      - env file (VIDEOS_ROOT or legacy DATA_DIRECTORY)
      - process env (VIDEOS_ROOT or legacy DATA_DIRECTORY)
      - DEFAULT_VIDEOS_ROOT (/mnt/24T/media/DATA/videos)
    """
    # keep key/envPath for backward compatibility with callers that used an env file
    # but prefer the explicit arg if provided
    root = get_videos_root(explicit=videos_root, envPath=envPath)
    os.makedirs(root, exist_ok=True)
    logger.info(f"using videos root: {root}")
    return root
