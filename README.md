# 4up

[Mike's](https://github.com/migurski/) "4up" Pinterest PDF-book code abstracted just
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

Scripts for generating 4up "compliant" CSV files for a user's photos or
favourited photos on Flickr. These scripts will dump all the photos in to CSV
files grouped by year uploaded or year faved.

One limitation of the this code is that it assumes old-skool Flickr Auth API
credentials (which you can't create anymore). Updating it to work with the newer
OAuth stuff is on the list.

Note the use of the `-u me` shortcut. By default you pass a Flickr `NSID` to
identify a user but if that value is set to "me" the code will look up the NSID
for the user identified by the Flickr auth token.

### Flickr photos for a user

	$> python ./flickr/4up-photos.py -c flickr.cfg -u me -o ../data

### Flickr faves for a user

	$> python ./flickr/4up-faves.py -c flickr.cfg -u me -o ../data

### flickr.cfg

A sample config file is included but it looks like this. As noted above this
assumes old Flickr Auth API style credentials.

	[flickr]
	api_key=YOUR_FLICKR_API_KEY
	api_secret=YOUR_FLICKR_API_SECRET
	auth_token=YOUR_FLICKR_AUTH_TOKEN

## Why "4up"

Because it's sort of catchy and more often that not its the layout that the code
chooses for arranging photos on a page.

## Caveats

* You will need to have both Cairo and its corresponding Python bindings
installed. This is sometimes harder than it sounds. See below inre: a setup.py
script.

## To do

* A proper `setup.py` script

* Update the Flickr stuff to work with new-skool OAuth API token nonsense.

* Identify and document that minimum properties required to generate a book and
  update everything else accordingly

* Add the ability to pass multiple CSV files at once. Yak shaving ?
