#!/usr/bin/env python3

# Thread: https://redd.it/f26802
# Description: Async, hackable script to download all the fruit images quickly (7584 images spread over 380 pages).


import aiofiles
import aiohttp
import asyncio

from bs4 import BeautifulSoup

BASE_URL = """https://usdawatercolors.nal.usda.gov"""
INIT_URL = (
    BASE_URL + """/pom/search.xhtml?start={}&searchText=&searchField=&sortField="""
)


def chunks(dl_links, n):
    for i in range(0, len(dl_links), n):
        yield dl_links[i : i + n]


def get_fruit_segment(page):
    soup = BeautifulSoup(page, "html.parser")
    for link in soup.find_all("a"):
        if link.get("href").startswith("/pom/catalog.xhtml?id="):
            if not link.get("href") in fruits:
                fruits.append(link.get("href"))


async def collection_helper(session, url):
    async with session.get(url) as response:
        return await response.text()


async def collect_fruits(page_segment):
    async with aiohttp.ClientSession() as session:
        page = await collection_helper(session, INIT_URL.format(page_segment))
        try:
            get_fruit_segment(page)
            print(
                "Collected fruit links from page segment starting at: start={}".format(
                    page_segment
                )
            )
        except Exception:
            # Do some exception handling if you feel like.
            pass


async def download_fruit_image(image_url):
    file_name = image_url.split("=")[1]
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                f = await aiofiles.open("{}.jpg".format(file_name), mode="wb+")
                await f.write(await response.read())
                print("Downloaded image {}.jpg".format(file_name))
                await f.close()


if __name__ == "__main__":

    fruits = []
    dl_links = []

    loop = asyncio.get_event_loop()
    page_segments = [i for i in range(0, 7600, 20)]

    print("\n\n---Starting link collection---\n")

    loop.run_until_complete(
        asyncio.gather(*[collect_fruits(args) for args in page_segments])
    )

    print("\n\n---Finished link collection---\n")
    print("Found {} total fruits".format(len(fruits)))

    # Write the list 'fruits' to a file at this point if you'd like.

    for fruit in fruits:
        dl_link = BASE_URL + fruit.split("&")[0]
        dl_link = dl_link.replace("catalog", "download")
        dl_links.append(dl_link)

    # Download in asynchronous bursts of 100 images, for sanity. Tweak CHUNK_SIZE if you'd like, best performance at 7584.

    CHUNK_SIZE = 100

    dl_links_chunked = list(chunks(dl_links, CHUNK_SIZE))

    print("\n\n---Starting image download, be patient---\n")

    for burst in dl_links_chunked:
        # Add a little delay here to be gentler on the server.
        loop.run_until_complete(
            asyncio.gather(*[download_fruit_image(args) for args in burst])
        )
