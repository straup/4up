#!/usr/bin/env python

import sys
import datetime
import json
import csv
import os.path

import optparse
import ConfigParser
import Flickr.API
    
parser = optparse.OptionParser()
parser.add_option("-c", "--config", dest="config", help="path to an ini config file")
parser.add_option("-u", "--user-id", dest="user_id", help="the user to fetch photos for")
parser.add_option("-o", "--outdir", dest="outdir", help="where to write data files")

(opts, args) = parser.parse_args()

cfg = ConfigParser.ConfigParser()
cfg.read(opts.config)

api_key=cfg.get('flickr', 'api_key')
api_secret=cfg.get('flickr', 'api_secret')
auth_token=cfg.get('flickr', 'auth_token')

api = Flickr.API.API(api_key, api_secret)

pages = None
page = 1

current_year = None
writer = None

while not pages or page <= pages:

    print "page %s (%s)" % (page, pages)

    args = {
        'method':'flickr.photos.search',
        'user_id':opts.user_id,
        'format':'json',
        'nojsoncallback':1,
        'extras':'date_taken,owner_name,geo,date_taken,url_m, url_n, url_z, url_c, url_l',
        'auth_token':auth_token,
        'page':page,
        'sort':'date-taken-asc'
        }

    req = Flickr.API.Request(**args)
    res = api.execute_request(req)

    data = json.loads(res.read())

    if not pages:
        pages = data['photos']['pages']

    for ph in data['photos']['photo']:

        # print ph

        dt = ph['datetaken']
        dt = dt.split('-')
        year_taken = dt[0]

        title = ph['title']
        owner = ph['ownername']

        # http://farm{farm-id}.staticflickr.com/{server-id}/{id}_{secret}.jpg
        full_img = 'http://farm%s.staticflickr.com/%s/%s_%s_b.jpg' % (ph['farm'], ph['server'], ph['id'], ph['secret'])

        for url in ('url_l', 'url_c', 'url_z', 'url_m'):

            if ph.get(url):
                full_img = ph[url]
                break

        # print full_img

        """
        sz_args = {
            'method':'flickr.photos.getSizes',
            'photo_id':ph['id'],
            'format': 'json',
            'nojsoncallback': 1,
            'auth_token': auth_token,
        }

        sz_req = Flickr.API.Request(**sz_args)
        sz_res = api.execute_request(sz_req)

        sz_data = json.load(sz_res)

        possible = sz_data['sizes']['size']
        possible_h = {}

        for p in possible:
            possible_h[ p['label'] ] = p

        for label in ('Large', 'Medium 800', 'Medium 640', 'Medium'):
            if possible_h.get(label, False):
                full_img = possible_h[label]['source']
                print full_img
                break
        """
        
        photo_page = "http://www.flickr.com/photos/%s/%s" % (ph['owner'], ph['id'])

        desc = ""
        
        if title != '':
            desc = "%s" % (title,)
        else:
            desc = "Untitled"

        meta = json.dumps({
            'og:description': desc,
            'pinterestapp:source': photo_page,
        })

        row = {
            'full_img': full_img,
            'id': ph['id'],
            'meta': meta,
        }

        if not current_year or year_taken != current_year:

            current_year = year_taken
            fname = "flickr-photos-%s.csv" % current_year

            path = os.path.join(opts.outdir, fname)
            print path

            fh = open(path, 'w')

            writer = csv.DictWriter(fh, fieldnames=('full_img', 'id', 'meta'))
            writer.writeheader()

        writer.writerow(row)

    page += 1

