import argparse
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup
import requests
import seleniumrequests


def main():
    """
    The tool is intended to extract all links (complete and relative ones) from HTML tag attributes
    """

    # Retrieving parameters
    links = []
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--method', action='store', help='What method to use in request', default='GET')
    parser.add_argument('-u', '--url', action='store', help='URL to call with the specified method')
    parser.add_argument('-w', action='store_true', help='Use Chrome webdriver', default=False)

    try:
        # Defining and splitting variables from the incoming url
        args = parser.parse_args()
        url = args.url
        method = args.method

        # checking for the supported methods
        if not method.upper() in ['GET', 'POST', 'OPTIONS', 'PUT', 'DELETE']:
            raise ValueError("Method %s is not supported." % method)

        # requesting the url
        requests.packages.urllib3.disable_warnings()  # suppressing unsafe HTTPS warnings

        if args.w: # if the -w switch is present - switch to webdriver instead of requests module
            print('[+] Starting up a webdriver')
            driver = seleniumrequests.Chrome('chromedriver.exe')
            print('[+] Retrieving ' + url)
            response = driver.request(method, url, verify=False)  # get the response
        else:
            print('[+] Retrieving ' + url)
            response = requests.request(method, url, verify=False)  # get the response

        url = response.url.rstrip('/')  # if there was a redirect - acquire the URL from the response

        # neat print headers
        print("[+] Received the response HTTP %d" % response.status_code)
        for header in response.headers:
            print(header + ':', response.headers[header])

        raw_html = response.content
        parsed_html = BeautifulSoup(raw_html, "html.parser")

        # gathering a list of links from specific elements
        script_elements = [element['src'] for element in parsed_html.select('script[src]')]
        anchor_elements = [element['href'] for element in parsed_html.select('a[href]')]
        link_elements = [element['href'] for element in parsed_html.select('link[href]')]
        form_elements = [element['action'] for element in parsed_html.select('form[action]')]
        links = script_elements + anchor_elements + link_elements + form_elements

        # removing bookmarks, non-interesting schemes and '/'
        print('[+] Tidying up the links')
        links = [link for link in links if
                 not link[0] == '#' and
                 not urlparse(link).scheme in ['mailto', 'skype', 'tel'] and
                 not link == '/']
        links = [urljoin(url, link) for link in links]  # gathering links together

    except Exception as e:
        print("[-] Something went wrong: %s" % e)

    except KeyboardInterrupt:
        print("[x] Exiting by user command")

    # final links count and listing
    print("[+] %d unique links extracted (%d duplicates removed):" % (len(set(links)), len(links) - len(set(links))))
    for link in set(links):
        print(link)
    return links

if __name__ == "__main__":
    print('[*] Starting the main module')
    main()
