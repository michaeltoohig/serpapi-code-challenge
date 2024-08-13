import json
from dataclasses import asdict

import pytest
from bs4 import BeautifulSoup

from serpapi_code_challenge.scraper import (
    CarouselItem,
    DropEmptyArrayEncoder,
    gather_carousel_image_sources,
    gather_carousel_item_tags,
    parse_item_title,
    get_carousel_item_image,
    build_carousel_item,
)


@pytest.fixture
def sample_html():
    return """
    <html>
        <body>
            <div id="appbar">
                <g-scrolling-carousel>
                    <a href="/test1" title="Item 1 (2021)">
                        <img id="img1" src="data:image/gif;base64,R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==">
                    </a>
                    <a href="/test2" title="Item 2">
                        <img id="img2" src="data:image/gif;base64,R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==">
                    </a>
                    <a href="/test3" title="Item 3 (2022-2024)">
                        <img id="img3" src="data:image/gif;base64,R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==">
                    </a>
                </g-scrolling-carousel>
            </div>
            <script>
                function _setImagesSrc(e, c) {
                    function f(a) {
                        a.onerror = function () {
                            a.style.display = "none";
                        };
                        a.src = c;
                    }
                    for (var g = 0, b = void 0; (b = e[g++]);) {
                        var d = document.getElementById(b);
                        d ? f(d) : ((google.iir = google.iir || {}), (google.iir[b] = c));
                    }
                }
                (function () {
                    var s = 'base64_encoded_image1';
                    var ii = ['img1'];
                    _setImagesSrc(ii, s);
                })();
                (function () {
                    var s = 'base64_encoded_image2';
                    var ii = ['img2','img3'];
                    _setImagesSrc(ii, s);
                })();
            </script>
        </body>
    </html>
    """


@pytest.fixture
def sample_soup(sample_html):
    return BeautifulSoup(sample_html, "html.parser")


def test_gather_carousel_image_sources(sample_soup):
    images = gather_carousel_image_sources(sample_soup)
    assert len(images) == 3
    assert images["img1"] == "base64_encoded_image1"
    assert images["img2"] == "base64_encoded_image2"
    assert images["img3"] == "base64_encoded_image2"


def test_gather_carousel_item_tags(sample_soup):
    items = gather_carousel_item_tags(sample_soup)
    assert len(items) == 3
    assert items[0].attrs["href"] == "/test1"
    assert items[1].attrs["href"] == "/test2"
    assert items[2].attrs["href"] == "/test3"


def test_parse_item_title():
    assert parse_item_title("Item 1 (2021)") == ("Item 1", "2021")
    assert parse_item_title("Item 2") == ("Item 2", None)
    assert parse_item_title("Item 3 (2022-2024)") == ("Item 3", "2022-2024")


def test_get_carousel_item_image():
    images = {"img1": "base64_encoded_image1"}
    carousel_item_tag = BeautifulSoup('<a href="#"><img id="img1"></a>', "html.parser")
    assert get_carousel_item_image(carousel_item_tag, images) == "base64_encoded_image1"
    carousel_item_tag = BeautifulSoup('<a href="#"></a>', "html.parser")
    assert get_carousel_item_image(carousel_item_tag, images) is None


def test_build_carousel_item(sample_soup):
    images = {"img1": "base64_encoded_image1"}
    item_tag = sample_soup.find("a")
    result = build_carousel_item(item_tag, images)
    assert asdict(result) == {
        "name": "Item 1",
        "extensions": ["2021"],
        "link": "https://www.google.com/test1",
        "image": "base64_encoded_image1",
    }

    images = {}
    item_tag = sample_soup.find_all("a")[1]
    result = build_carousel_item(item_tag, images)
    assert asdict(result) == {
        "name": "Item 2",
        "extensions": [],
        "link": "https://www.google.com/test2",
        "image": None,
    }


def test_custom_json_encoder():
    item = CarouselItem.create(
        name="Item 1",
        link="https://www.google.com/test1",
        image=None,
        year=None,
    )
    assert item.extensions == []
    json_str = json.dumps(item, cls=DropEmptyArrayEncoder)
    item_dict = json.loads(json_str)
    assert item_dict == {
        "name": "Item 1",
        "link": "https://www.google.com/test1",
        "image": None,
    }
