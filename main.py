import re
import json
from pathlib import Path
from typing import Any, Union

from bs4 import BeautifulSoup, Tag


def grather_carousel_image_sources(soup) -> dict[str, str]:
    script_tag = soup.find("script", string=re.compile("_setImagesSrc"))

    if not script_tag or not script_tag.string:
        return []

    pattern = re.compile(
        r"\(function\s*\(\)\s*{\s*var\s+s\s*=\s*\'([^\']+)\';\s*var\s+ii\s*=\s*\[\'([^\']+)\'\];"
    )
    matches = pattern.findall(script_tag.string)

    images = {}
    for b64img, img_id in matches:
        images[img_id] = b64img
    return images


def grather_carousel_items(soup) -> list[Tag]:
    appbar = soup.find(id="appbar")
    if not appbar:
        return []
    carousel = appbar.find("g-scrolling-carousel")
    if not carousel:
        return []

    return carousel.find_all("a")


def scrape_item_title(title: str) -> Union[str, str | None]:
    pattern = r"^(.*?)\s*(?:\((\d{4})\))?$"
    match = re.match(pattern, title)
    name, year = match.groups()
    return name.strip(), year


def scrape_item_image(img_tag, images) -> str | None:
    if not img_tag:
        return None
    img_id = img_tag.attrs.get("id", None)
    return images.get(img_id, None)


def scrape_carousel_item(tag: Tag, images: dict[str, str]) -> dict[str, Any]:
    result = {}
    name, year = scrape_item_title(tag.attrs.get("title"))
    result["name"] = name
    if year:
        result["extensions"] = [year]
    result["link"] = tag.attrs.get("href", None)
    result["image"] = scrape_item_image(tag.img, images)
    return result


def scrape_google_result_page(html: str):
    soup = BeautifulSoup(html, "html.parser")

    images = grather_carousel_image_sources(soup)
    carousel_item_tags = grather_carousel_items(soup)

    results = []
    for carousel_item_tag in carousel_item_tags:
        carousel_item = scrape_carousel_item(carousel_item_tag, images)
        results.append(carousel_item)

    return results


def write_results(results: list[dict[str, Any]]):
    json_str = json.dumps({"artworks": results}, indent=2)
    with open("output.json", "w") as f:
        f.write(json_str[1:-1])


def main(html: str):
    results = scrape_google_result_page(html)
    write_results(results)


if __name__ == "__main__":
    TARGET_HTML_FILE = Path("./files/van-gogh-paintings.html")

    html = TARGET_HTML_FILE.read_text()
    main(html)
