#!/usr/bin/env python

import sys
import datetime
import logging
import json
import csv
import os.path

import optparse
import ConfigParser
import flickrapi

if __name__ == '__main__' :

    parser = optparse.OptionParser()
    parser.add_option("-c", "--config", dest="config", help="path to an ini config file")
    parser.add_option("-u", "--user-id", dest="user_id", help="the user to fetch photos for")
    parser.add_option("-o", "--outdir", dest="outdir", help="where to write data files")

    (opts, args) = parser.parse_args()

    cfg = ConfigParser.ConfigParser()
    cfg.read(opts.config)

    api_key=cfg.get('flickr', 'api_key')
    api_secret=cfg.get('flickr', 'api_secret')

    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    (token, frob) = flickr.get_token_part_one(perms='read')
    if not token: raw_input("Press ENTER after you authorized this program")
    flickr.get_token_part_two((token, frob))

    # sudo put me in a library or something...
    # (20130930/straup)

    if opts.user_id == 'me':
        data = flickr.auth_checkToken()
        opts.user_id = data.find('auth').find('user').attrib['nsid']

    pages = None
    page = 1

    current_year = None
    writer = None

    while not pages or page <= int(pages):

        print "page %s (%s)" % (page, pages)

        data = flickr.favorites_getList(
            user_id=opts.user_id,
            extras='owner_name,geo,date_taken,url_m,url_n,url_c,url_l',
            page=page
            )

        if not pages:
            pages = data.find('photos').attrib['pages']

        for ph in data.find('photos'):#['photo']:
            
            df = float(ph.attrib['date_faved'])
            df = datetime.date.fromtimestamp(df)

            year_faved = df.year

            dt = ph.attrib['datetaken']
            dt = dt.split('-')
            year_taken = dt[0]

            title = ph.attrib['title']
            owner = ph.attrib['ownername']

            # http://farm{farm-id}.staticflickr.com/{server-id}/{id}_{secret}.jpg
            # full_img = 'http://farm%s.staticflickr.com/%s/%s_%s_b.jpg' % (ph['farm'], ph['server'], ph['id'], ph['secret'])

            # because _z.jpg?zz=1 WTF???

            for url in ('url_l', 'url_c', 'url_m'):

                if ph.get(url):
                    full_img = ph.attrib[url]
                    break

            logging.debug("fetch %s" % full_img)

            photo_page = "http://www.flickr.com/photos/%s/%s" % (ph.attrib['owner'], ph.attrib['id'])

            desc = ""
        
            if title != '':
                desc = "%s, by %s (%s)" % (title, owner, year_taken)
            else:
                desc = "Untitled, by %s (%s)" % (owner, year_taken)

            meta = json.dumps({
                'og:description': desc,
                'pinterestapp:source': photo_page,
            })

            row = {
                'full_img': full_img,
                'id': ph.attrib['id'],
                'meta': meta,
            }

            if not current_year or year_faved != current_year:

                current_year = year_faved
                fname = "flickr-faves-%s.csv" % current_year

                path = os.path.join(opts.outdir, fname)
                fh = open(path, 'w')

                writer = csv.DictWriter(fh, fieldnames=('full_img', 'id', 'meta'))
                writer.writeheader()

            writer.writerow(row)

        page += 1
