# 4up

[Mike's](https://github.com/migurski/) "4up" Pinterest-book code abstracted just
enough to work with non-Pinterest sources. Which really means any CSV file
containing the following columns:

	full_img,id,meta

For example, Flickr:

	http://farm1.staticflickr.com/1/132429_cb520f81ce.jpg,132429,"{""og:description"": ""Untitled-1, by mickey1 (2004)"", ""pinterestapp:source"": ""http://www.flickr.com/photos/44124351339@N01/132429""}"

If you're looking carefully at the example above and wondering why the various
properties are named the way they are it's only because this is still an early
branch and I've been more concerned with the bits that can be removed rather
than what things should or should not be named. So `og:description` it is, for
now.

Once you have a CSV file you can create a book like this:

	$> python ./layout.py -d data/flickr-photos-2005.csv

By default books are split at the 240-page limit. You can override this by
passing a `--pages` argument:

	$> python ./layout.py -d data/flickr-photos-2005.csv --pages 150

## Flickr

### Flickr photos for a user

	$> python ./flickr/4up-photos.py -c flickr.cfg. -u me -o ../data

### Flickr faves for a user

	$> python ./flickr/4up-photos.py -c flickr.cfg. -u me -o ../data
