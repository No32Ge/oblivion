PROGRAM_TEMPLATES = {
    "data_processor": {
        "description": "通用数据处理程序",
        "template": """import pandas as pd

def process_data(input_file, output_file):
    df = pd.read_csv(input_file)
    # 数据处理逻辑
    df.to_csv(output_file)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    process_data(args.input, args.output)
""",
        "dependencies": ["pandas"]
    },
    "web_scraper": {
        "template": """import requests
from bs4 import BeautifulSoup
# ...网页抓取模板...
"""
    }
}