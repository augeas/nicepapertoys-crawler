# nicepapertoys-crawler

A crawler for archiving [www.nicepapertoys.com](https://www.nicepapertoys.com) while you still can.

## Installation

* [Download](https://github.com/augeas/nicepapertoys-crawler/archive/refs/heads/main.zip) and extract this repository.
* On a Mac, make sure you have [pip3](https://pip.pypa.io/en/stable/installation/) installed:

```bash
python3 -m ensurepip --upgrade
```

* Still in the terminal, go to the directory where you extracted the repository:

```bash
cd /path/to/nicepapertoys-crawler
``` 

* Install the dependencies with:
```
pip3 install -r requirements.txt
```

## Running crawls:

### photos

From the terminal, in the repository directory:

```
scrapy crawl photos -o photos.json
```

will dump the details of *all* the photos in JSON format in `photos.json`.

### blogs

```
scrapy crawl blogs -o blogs.json
```

### members

```
scrapy crawl members -o members.json
```

## Images

By default, images will end up in:

```
/your/home/directory/nicepapertoys/images
```

The correspondence between the downloaded files and the original filenames is held in the JSON files.
 
