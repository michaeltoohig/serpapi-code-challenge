# Extract Van Gogh Paintings Code Challenge

Goal is to extract a list of Van Gogh paintings from the attached Google search results page.

![Van Gogh paintings](https://github.com/serpapi/code-challenge/blob/master/files/van-gogh-paintings.png?raw=true "Van Gogh paintings")

My soluton also handles for new Google search result's carousel and multiple carousel items sharing the same thumbnail.

![US Presidents](https://github.com/michaeltoohig/serpapi-code-challenge/blob/master/files/us-presidents.jpg?raw=true "US Presidents")

> Notice Sato Kilman is repeated multiple times.

![VU Prime Ministers](https://github.com/michaeltoohig/serpapi-code-challenge/blob/master/files/vu-prime-ministers.jpg?raw=true "VU Prime Ministers")

## Running

First install dependencies from `pyproject.toml` with [Poetry](https://python-poetry.org).

```sh
poetry env use 3.11
poetry install
```

The code can be run via the `google-carousel-scraper` command which expects a path to an HTML file and a path for the JSON output.

```sh
poetry run google-carousel-scraper ./files/van-gogh-paintings.html ./van-gogh-paintings.json
poetry run google-carousel-scraper ./files/us-presidents.html ./us-presidents.json
poetry run google-carousel-scraper ./files/vu-prime-ministers.html ./vu-prime-ministers.json
```

Of course if you first `poetry shell` to activate the local virtual environment then you can drop the `poetry run` at the beginning of each command.

### JSON Output Note

The provided `expected-array.json` file begins with a naked key `artworks` which is not valid JSON for the Python `json` library so I could not write my JSON output in the exact same way as demonstrated without some hacky file manipulation.
So I did not include the envelope key in my JSON output.
Instead I return just an array of carousel item objects.

I was advised via email this was okay and the expected path I should follow by Emirhan Akdeniz.

## Testing

Testing the code is done with [Pytest](https://pytest.org).

```sh
poetry run pytest
```

## Original Instructions

This is already fully supported on SerpApi. ([relevant test], [html file], [sample json], and [expected array].)
Try to come up with your own solution and your own test.
Extract the painting `name`, `extensions` array (date), and Google `link` in an array.

Fork this repository and make a PR when ready.

Programming language wise, Ruby (with RSpec tests) is strongly suggested but feel free to use whatever you feel like.

Parse directly the HTML result page ([html file]) in this repository. No extra HTTP requests should be needed for anything.

[relevant test]: https://github.com/serpapi/test-knowledge-graph-desktop/blob/master/spec/knowledge_graph_claude_monet_paintings_spec.rb
[sample json]: https://raw.githubusercontent.com/serpapi/code-challenge/master/files/van-gogh-paintings.json
[html file]: https://raw.githubusercontent.com/serpapi/code-challenge/master/files/van-gogh-paintings.html
[expected array]: https://raw.githubusercontent.com/serpapi/code-challenge/master/files/expected-array.json

Add also to your array the painting thumbnails present in the result page file (not the ones where extra requests are needed). 

Test against 2 other similar result pages to make sure it works against different layouts. (Pages that contain the same kind of carrousel. Don't necessarily have to be paintings.)

The suggested time for this challenge is 4 hours. But, you can take your time and work more on it if you want.
