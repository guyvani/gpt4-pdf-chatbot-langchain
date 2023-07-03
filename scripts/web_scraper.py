import csv
import random
import time
from xml.etree import ElementTree

import numpy as np
import requests
from bs4 import BeautifulSoup


class WebScraper:
    """A class for web scraping using Python's requests and
    BeautifulSoup.

    This class provides methods for scraping a list of URLs obtained
    from a website's sitemap and saving scraped content to text files.
    It also provides functionality to save a mapping between URLs and
    corresponding text file names to a CSV file, and to save the URL
    list to a numpy file.

    Methods
    -------
    get_urls_in_sitemap(sitemap_url: str) -> list:
        Fetch URLs from a website's sitemap.
    scrape_webpage(url: str) -> str:
        Scrape and process a webpage and return its text content.
    save_to_files(urls: list):
        Save webpages to text files and create a mapping file.
    """

    def get_urls_in_sitemap(self, sitemap_url):
        """Fetch URLs from a website's sitemap.

        Parameters
        ----------
        sitemap_url : str
            The URL of the website's sitemap.xml file.

        Returns
        -------
        list
            A list of URLs obtained from the sitemap.
        """
        response = requests.get(sitemap_url)
        sitemap = ElementTree.fromstring(response.content)

        url_tag = "{http://www.sitemaps.org/schemas/sitemap/0.9}url"
        loc_tag = "{http://www.sitemaps.org/schemas/sitemap/0.9}loc"

        urls = sitemap.findall(f".//{url_tag}")
        urls = [
            url.find(loc_tag).text
            for url in urls
            if url.find(loc_tag) is not None
            and "/search" not in url.find(loc_tag).text
        ]

        return urls

    def scrape_webpage(self, url):
        """Scrape and process a webpage and return its text content.

        Parameters
        ----------
        url : str
            The URL of the webpage to be scraped.

        Returns
        -------
        str
            The text content of the scraped webpage.
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        relevant_tags = soup.find_all(["h1", "p"])

        MIN_WORD_COUNT = 10
        text = " ".join(tag.get_text() for tag in relevant_tags)
        sentences = text.split("\n")
        filtered_sentences = [
            s for s in sentences if len(s.split()) >= MIN_WORD_COUNT
        ]

        filtered_text = " ".join(filtered_sentences)

        return filtered_text

    def save_to_files(self, urls):
        """Save webpages to text files and create a mapping file.

        This method scrapes each URL in the given list, saves the
        scraped content to a text file, and adds the URL and
        corresponding file name to a mapping. It then saves this mapping
        to a CSV file and the URL list to a numpy file.

        Parameters
        ----------
        urls : list
            The list of URLs to be scraped.
        """
        np.save("data/url_list.npy", np.array(urls))

        url_to_file_map = {}

        for idx, url in enumerate(urls):
            try:
                text = self.scrape_webpage(url)
            except Exception as e:
                print(f"Failed to scrape webpage: {url}, due to: {str(e)}")
                continue

            filename = f"data/webpage_{idx}.txt"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"Successfully wrote file: {filename}")

                # Add the url and filename to the map
                url_to_file_map[url] = filename
            except Exception as e:
                print(f"Failed to write file: {filename}, due to: {str(e)}")

            # Add a delay between 3 to 7 seconds
            time.sleep(random.randint(3, 7))

        # Write the mapping to a CSV file
        try:
            with open(
                "data/url_to_file_map.csv", "w", newline="", encoding="utf-8"
            ) as f:
                writer = csv.writer(f)
                writer.writerow(["URL", "Document"])
                for url, filename in url_to_file_map.items():
                    writer.writerow([url, filename])
        except Exception as e:
            print(f"Failed to write URL to file map, due to: {str(e)}")
