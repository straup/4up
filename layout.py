#!/usr/bin/env python

from glob import glob
from sys import argv, stdin
from csv import DictReader
from json import loads
from operator import itemgetter
from itertools import izip, count, chain, islice, groupby
from os.path import exists, dirname, join
from tempfile import mkstemp
from os import close, remove

from cairo import PDFSurface, ImageSurface, Context
from PIL import Image

import urllib
import urlparse
import os.path

import logging

from font import set_font_face_from_file
from placer import place_image_top, place_image_bottom, place_image_left
from placer import place_image_right, place_image_topleft, place_image_topright
from placer import place_image_bottomleft, place_image_bottomright, place_text
from placer import sheet_width, sheet_height

mmppt = 0.352777778
inppt = 0.013888889

ptpin = 1./inppt
ptpmm = 1./mmppt

LEFT, RIGHT = 1, 2
TALL, WIDE, EQUAL = 1, 2, 3

def load_image(image_row):
    '''
    '''

    image = Image.open(image_row['full_img'])

    width, height = image.size
    aspect = float(width) / float(height)

    handle, png_path = mkstemp(dir='.', suffix='.png')
    # image.thumbnail((64, 64), Image.ANTIALIAS)
    image.save(png_path)

    image = ImageSurface.create_from_png(png_path)

    remove(png_path)
    close(handle)
    
    shape = TALL if aspect < .5 else EQUAL
    shape = WIDE if aspect > 2. else shape
    
    return image, shape

def get_rows(input):
    '''
    '''
    basedir = dirname(input.name)
    rows = list(DictReader(input))
    rows.sort(key=lambda r: int(r['id']), reverse=False)
    
    ids = set()
    
    for row in rows:
        #
        # Row keys: alt, board_img, center_height, center_img, center_width,
        #           error, full_img, href, id, link, meta, text, thumb_img
        #
        # Meta keys: og:description, og:image, og:see_also, og:site_name,
        #            og:title, og:type, og:url, pinterestapp:actions,
        #            pinterestapp:comments, pinterestapp:likes, pinterestapp:pinboard,
        #            pinterestapp:pinner, pinterestapp:repins, pinterestapp:source,
        #            twitter:card, twitter:site, twitter:url
        #
    
        if not row['full_img']:
            continue

        if not exists(join(basedir, row['full_img'])) and row['full_img'].startswith('http'):

            url = row['full_img']
            parts = urlparse.urlparse(url)
            
            fname = os.path.basename(parts.path)
            path = join(basedir, fname)

            if not exists(path):
                logging.info("write %s to %s" % (url, path))

                try:
                    rsp = urllib.urlopen(url)

                    fh = open(path, 'wb')
                    fh.write(rsp.read())
                    fh.close()

                except Exception, e:
                    logging.error("failed to fetch/write %s because %s" % (url, e))

            row['full_img'] = fname

        #

        if not exists(join(basedir, row['full_img'])):
            continue

        if row['id'] in ids:
            continue
        
        ids.add(row['id'])
    
        # row['center_img'] = join(basedir, row['center_img'])
        # row['thumb_img'] = join(basedir, row['thumb_img'])
        # row['board_img'] = join(basedir, row['board_img'])

        row['full_img'] = join(basedir, row['full_img'])
        row['meta'] = loads(row['meta'])
    
        # row['original_img'] = glob(join(dirname(row['full_img']), 'original.*'))[0]
        
        yield row

def arrange_page(ctx, image_rows, page_number, index):
    '''
    '''
    ctx.save()
    
    side = RIGHT if (page_number % 2) else LEFT

    if side == RIGHT:
        # right-hand page
        ctx.translate(.5, 0)

    # load up the next four images
    rows = list(islice(image_rows, 0, 4))
    images = [(row, ) + load_image(row) for row in rows]
    
    # are we done? we might be done.
    if len(rows) == 0:
        raise StopIteration()
    
    print 'Arranging page', page_number

    # put the images into a predictable order, sorting by shape
    images.sort(key=itemgetter(2))
    rows, images, shapes = map(tuple, zip(*images))
    
    if shapes[0] == EQUAL:
        place_image_topleft(ctx, images[0])
        info = rows[:1]
        
        if len(shapes) > 1:
            place_image_topright(ctx, images[1])
            info = rows[:2]

        if len(shapes) > 2:
            place_image_bottomleft(ctx, images[2])
            info = rows[:3]

        if len(shapes) > 3:
            place_image_bottomright(ctx, images[3])
            info = rows[:4]

    elif shapes[:3] == (TALL, EQUAL, EQUAL):
        place_image_left(ctx, images[0])
        place_image_topright(ctx, images[1])
        place_image_bottomright(ctx, images[2])
        info = rows[:3]
        
        if len(rows) > 3:
            image_rows = chain(rows[3:], image_rows)
    
    elif shapes[:3] == (WIDE, EQUAL, EQUAL):
        place_image_top(ctx, images[0])
        place_image_bottomleft(ctx, images[1])
        place_image_bottomright(ctx, images[2])
        info = rows[:3]
        
        if len(rows) > 3:
            image_rows = chain(rows[3:], image_rows)
    
    elif shapes[:3] == (TALL, WIDE, EQUAL):
        place_image_top(ctx, images[1])
        place_image_bottomleft(ctx, images[2])
        info = rows[1:3]
        
        if len(images) > 3:
            place_image_bottomright(ctx, images[3])
            info = rows[1:]
        
        image_rows = chain([rows[0]], image_rows)
    
    elif shapes[:2] == (WIDE, WIDE):
        place_image_top(ctx, images[0])
        place_image_bottom(ctx, images[1])
        info = rows[:2]
        
        if len(rows) > 2:
            image_rows = chain(rows[2:], image_rows)
    
    elif shapes[:2] == (TALL, TALL):
        place_image_left(ctx, images[0])
        place_image_right(ctx, images[1])
        info = rows[:2]
        
        image_rows = chain(rows[2:], image_rows)
    
    elif shapes == (TALL, ):
        place_image_left(ctx, images[0])
        info = rows[:1]
    
    elif shapes == (WIDE, ):
        place_image_top(ctx, images[0])
        info = rows[:1]
    
    else:
        raise Exception(shapes)
    
    ctx.set_font_size(7 * inppt)

    for (row, num, y) in zip(info, count(1), (1.5, 1.25, 1.0, 0.75)):
        text = row['meta'].get('og:description', '')
        href = row['meta'].get('pinterestapp:source', '')

        place_text(ctx, text, href, .5, sheet_height - y)
        index.append(dict(page=page_number, text=text, href=href, row=row))
    
    ctx.set_font_size(10 * inppt)

    if side == LEFT:
        ctx.move_to(.35, sheet_height - .35)
    
    else:
        w = ctx.text_extents(str(page_number))[4]
        ctx.move_to(sheet_width - .35 - .5 - w, sheet_height - .35)

    ctx.show_text(str(page_number))
    ctx.restore()
    
    return image_rows

def setup_doc(name):
    '''
    '''
    doc = PDFSurface(name, sheet_width*ptpin, sheet_height*ptpin)
    ctx = Context(doc)
    ctx.scale(ptpin, ptpin)
    
    set_font_face_from_file(ctx, 'DejaVuSerifCondensed.ttf')
    
    return doc, ctx

if __name__ == '__main__':

    import optparse
    import ConfigParser
    
    parser = optparse.OptionParser()
    parser.add_option("-d", "--data", dest="data", help="The path to the CSV file containing your data")
    # TO DO: out dir
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="Be chatty while you work (default is false)")

    (opts, args) = parser.parse_args()

    if opts.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    path = opts.data

    input = open(path)
    books = count(1)
    
    image_rows = islice(get_rows(input), 0, 10000)
    index = []
    
    fname = os.path.basename(path)
    fname = fname.replace(".csv", "")

    doc, ctx = setup_doc('%s-book%d.pdf' % (fname, books.next()))
    page_numbers = count(1)
    
    while True:
        page_number = page_numbers.next()
    
        try:
            image_rows = arrange_page(ctx, image_rows, page_number, index)
        
        except StopIteration:
            break

        else:
            doc.show_page()
        
        if page_number == 240:
            doc.finish()
            doc, ctx = setup_doc('%s-book%d.pdf' % (fname, books.next()))
            page_numbers = count(1)
    
    doc.finish()
