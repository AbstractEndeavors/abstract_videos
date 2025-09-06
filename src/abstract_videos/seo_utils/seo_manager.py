from abstract_utilities import safe_dump_to_file
from .seo_services import get_seo_data  # adjust import path as needed

class SEOManager:
    """
    Orchestrates the SEO/meta-data generation step for videos:
      1) fetch required context vars,
      2) check if SEO data needs to be generated,
      3) call get_seo_data to build all meta fields,
      4) persist updated info_data.
    """
    def fetch_vars(self, req=None, info_data=None):
        # These are the inputs get_seo_data expects besides info_data
        keys = [
            'uploader', 'domain', 'categories', 'videos_url',
            'repository_dir', 'directory_links', 'videos_dir',
            'infos_dir', 'base_url', 'generator', 'LEDTokenizer',
            'LEDForConditionalGeneration'
        ]
        new_data, info_data = get_key_vars(keys, req=req, info_data=info_data)
        return new_data, info_data

    def run(self, req=None, info_data=None):
        # 1) gather context
        new_data, info_data = self.fetch_vars(req=req, info_data=info_data)
        # 2) only run if we haven't generated SEO yet
        run_flag = info_data.get('seo_description') is None
        if not run_flag:
            return info_data

        # 3) build all SEO/meta fields in one shot
        updated_info = get_seo_data(
            info_data=info_data,
            **new_data
        )

        # 4) persist back to info.json
        out_path = get_video_info_path(**updated_info)
        safe_dump_to_file(data=updated_info, file_path=out_path)

        return updated_info
