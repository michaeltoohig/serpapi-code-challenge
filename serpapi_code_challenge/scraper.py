import re
import json
import argparse
import logging
from dataclasses import asdict, dataclass, field
from typing import Union

from bs4 import BeautifulSoup, Tag

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DropEmptyArrayEncoder(json.JSONEncoder):
    """Drop empty array values from CarouselItem before encoding JSON."""

    def default(self, obj):
        if isinstance(obj, CarouselItem):
            d = asdict(obj)
            return {k: v for k, v in d.items() if v != []}
        return super().default(obj)


@dataclass
class CarouselItem:
    """A Google scrolling carousel item."""

    name: str
    link: str
    image: str | None
    extensions: list = field(default_factory=list)

    @classmethod
    def create(cls, name: str, link: str, image: str | None, year: str | None):
        item = cls(name=name, link=link, image=image)
        if year is not None:
            setattr(item, "extensions", [year])
        return item


def gather_carousel_image_sources(soup):
    """Returns a dict of image IDs and their associated base64 encoded thumbnail."""
    images = {}

    # matches for base64 encoded thumbnails and associated array of image IDs.
    pattern = r"\(function\s*\(\)\s*{\s*var\s*s\s*=\s*'(.*?)';\s*var ii\s*=\s*\[(.*?)\]"

    script_tags = soup.find_all("script", string=re.compile("_setImagesSrc"))
    logger.debug(
        f"Gathered {len(script_tags)} script tags containing '_setImagesSrc' function"
    )
    for script_tag in script_tags:
        matches = re.findall(pattern, script_tag.string)
        for b64img, img_ids_str in matches:
            # separates the string of a JS array of image IDs into a list.
            for img_id in re.findall(r"'([^']*)'", img_ids_str):
                logger.debug(f"Gathered thumbnail for image ID {img_id}")
                images[img_id] = b64img

    return images


def gather_carousel_item_tags(soup) -> list[Tag]:
    """Returns a list of `a` tags from a `g-scrolling-carousel`."""
    appbar = soup.find(id="appbar")
    if not appbar:
        logger.info("HTML does not contain 'appbar' element")
        return []
    carousel = appbar.find("g-scrolling-carousel")
    if not carousel:
        logger.info("HTML does not contain a Google scrolling carousel")
        return []

    return carousel.find_all("a")


def parse_item_title(title: str) -> Union[str, str | None]:
    """Returns a tuple containing the carousel item's name and extensions from a given `title` attribute.
    Expected values follow "{name} ({extensions})" format.
    """
    pattern = r"^(.*?)(?:\s*\((.*?)\))?$"
    match = re.match(pattern, title)
    name, year = match.groups()
    return name.strip(), year


def get_carousel_item_image(tag: Tag, images) -> str | None:
    """Returns the base64 encoded thumbnail of the given carousel item tag."""
    if not tag.img:
        return None
    img_id = tag.img.attrs.get("id", None)
    return images.get(img_id, None)


def build_carousel_item(tag: Tag, images: dict[str, str]) -> CarouselItem:
    """Returns a CarouselItem from the given carousel item tag and array of thumbnail images."""
    title = tag.attrs["title"]
    logger.info(f"Scraping carousel item '{title}'")
    name, year = parse_item_title(title)
    href = tag.attrs.get("href", None)
    link = f"https://www.google.com{href}"
    image = get_carousel_item_image(tag, images)
    return CarouselItem.create(name=name, link=link, image=image, year=year)


def parse_google_result_page(html: str) -> list[CarouselItem]:
    """Returns list of CarouselItems from the given Google results page HTML."""
    soup = BeautifulSoup(html, "html.parser")

    images = gather_carousel_image_sources(soup)
    logger.info(f"Gathered {len(images)} thumbnail images in script tags")
    carousel_item_tags = gather_carousel_item_tags(soup)
    logger.info(f"Gathered {len(carousel_item_tags)} carousel items in HTML")

    results = []
    for carousel_item_tag in carousel_item_tags:
        carousel_item = build_carousel_item(carousel_item_tag, images)
        results.append(carousel_item)

    return results


def save_results_to_json(results: list[CarouselItem], output_file: str):
    """Writes list of given CarouselItems to JSON using a custom encoder."""
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, cls=DropEmptyArrayEncoder)


def process_html_file(input_file: str, output_file: str):
    """Scrapes given HTML file for CarouselItems and writes results as JSON to given output file."""
    try:
        with open(input_file, "r") as f:
            html = f.read()
    except FileNotFoundError:
        logger.error(f"Input file '{input_file}' not found.")
        return
    except IOError:
        logger.error(f"Unable to read input file '{input_file}'.")
        return

    results = parse_google_result_page(html)

    try:
        save_results_to_json(results, output_file)
    except IOError:
        logger.error(f"Unable to write output file '{output_file}'.")
        return


def main():
    parser = argparse.ArgumentParser(
        description="Process Google search result HTML and extract carousel items."
    )
    parser.add_argument("input_file", help="Path to the input HTML file")
    parser.add_argument("output_file", help="Path to the output JSON file")
    args = parser.parse_args()

    if not args.input_file.endswith(".html"):
        logger.error("Input file must be an HTML file.")
        return

    if not args.output_file.endswith(".json"):
        logger.error("Output file must be a JSON file.")
        return

    process_html_file(args.input_file, args.output_file)
    logger.info("Done")


if __name__ == "__main__":
    main()
