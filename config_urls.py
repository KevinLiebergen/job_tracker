# config_urls.py

URL_CONFIG = [
    {
        "company": "Google",
        "base_url": "https://www.google.com/about/careers/applications/jobs/results/",
        "param_name": "q",     # Keyword parameter to use
        "parser": "google", # parser to use
    },
    {
        "company": "Amazon",
        "base_url": "https://www.amazon.jobs/es/search/",
        "param_name": "base_query",
        "parser": "amazon",
    },
    {
        "company": "Cloudflare",
        "base_url": "https://boards-api.greenhouse.io/v1/boards/cloudflare/jobs/",
        "param_name": "title",
        "parser": "cloudflare",
    },
]
