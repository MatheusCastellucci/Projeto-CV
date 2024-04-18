import sys

from icrawler.builtin import GoogleImageCrawler

def main():
    google_crawler = GoogleImageCrawler(storage={'root_dir': 'crawled'})
    google_crawler.crawl(keyword='pig', max_num=100)
    return 0

if __name__ == '__main__':
    sys.exit(main())
