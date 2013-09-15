from httplib import HTTPConnection
from urllib import urlencode

sheet_width, sheet_height = 8.25, 10.75 # 8.5, 11.0

wide_size = sheet_width - 1.5, (sheet_height - 3) / 2
wide_aspect = wide_size[0] / wide_size[1]

tall_size = (sheet_width - 2) / 2, sheet_height - 2.5
tall_aspect = tall_size[0] / tall_size[1]

quarter_size = (sheet_width - 2) / 2, (sheet_height - 3) / 2
quarter_aspect = quarter_size[0] / quarter_size[1]

#

def draw_box(ctx, x, y, width, height):
    """ Draw a box.
    """
    ctx.save()
    
    ctx.translate(x, y)
    
    ctx.move_to(0, 0)
    ctx.rel_line_to(width, 0)
    ctx.rel_line_to(0, height)
    ctx.rel_line_to(-width, 0)
    ctx.rel_line_to(0, -height)
    
    ctx.set_source_rgb(.9, .9, .9)
    ctx.fill()
    
    ctx.restore()

def place_image(ctx, img, x, y, width, height):
    """ Add an image to a given context, at a position and size given in millimeters.
    
        Assume that the scale matrix of the context is already in mm.
    """
    ctx.save()
    ctx.translate(x, y)
    
    # determine the scale needed to make the image the requested size
    xscale = width / img.get_width()
    yscale = height / img.get_height()
    ctx.scale(xscale, yscale)

    # paint the image
    ctx.set_source_surface(img, 0, 0)
    ctx.paint()

    ctx.restore()

def place_boxed_image(ctx, img, x, y, width, height):
    '''
    '''
    draw_box(ctx, x-.125, y-.125, width+.25, height+.25)
    place_image(ctx, img, x, y, width, height)

def adjust_size(img_aspect, space_aspect, width, height):
    '''
    '''
    if img_aspect < space_aspect:
        # narrower than the space
        width = img_aspect * height
    
    else:
        # shorter than the space
        height = width / img_aspect
    
    return width, height

def place_image_top(ctx, img):
    '''
    '''
    aspect = float(img.get_width()) / img.get_height()
    width, height = adjust_size(aspect, wide_aspect, *wide_size)
    
    center, bottom = (sheet_width - .5) / 2, wide_size[1] + .5
    left, top = center - width/2, bottom - height

    place_boxed_image(ctx, img, left, top, width, height)

def place_image_bottom(ctx, img):
    '''
    '''
    aspect = float(img.get_width()) / img.get_height()
    width, height = adjust_size(aspect, wide_aspect, *wide_size)
    
    center, top = (sheet_width - .5) / 2, wide_size[1] + 1
    left = center - width/2

    place_boxed_image(ctx, img, left, top, width, height)

def place_image_left(ctx, img):
    '''
    '''
    aspect = float(img.get_width()) / img.get_height()
    width, height = adjust_size(aspect, tall_aspect, *tall_size)
    
    right, middle = .5 + tall_size[0], .5 + tall_size[1]/2
    left, top = right - width, middle - height/2

    place_boxed_image(ctx, img, left, top, width, height)

def place_image_right(ctx, img):
    '''
    '''
    aspect = float(img.get_width()) / img.get_height()
    width, height = adjust_size(aspect, tall_aspect, *tall_size)
    
    left, middle = 1 + tall_size[0], .5 + tall_size[1]/2
    top = middle - height/2

    place_boxed_image(ctx, img, left, top, width, height)

def place_image_topleft(ctx, img):
    '''
    '''
    aspect = float(img.get_width()) / img.get_height()
    width, height = adjust_size(aspect, quarter_aspect, *quarter_size)
    
    right, bottom = .5 + quarter_size[0], .5 + quarter_size[1]
    left, top = right - width, bottom - height

    place_boxed_image(ctx, img, left, top, width, height)

def place_image_topright(ctx, img):
    '''
    '''
    aspect = float(img.get_width()) / img.get_height()
    width, height = adjust_size(aspect, quarter_aspect, *quarter_size)
    
    left, bottom = 1 + quarter_size[0], .5 + quarter_size[1]
    top = bottom - height

    place_boxed_image(ctx, img, left, top, width, height)

def place_image_bottomleft(ctx, img):
    '''
    '''
    aspect = float(img.get_width()) / img.get_height()
    width, height = adjust_size(aspect, quarter_aspect, *quarter_size)
    
    right, top = .5 + quarter_size[0], 1 + quarter_size[1]
    left = right - width

    place_boxed_image(ctx, img, left, top, width, height)

def place_image_bottomright(ctx, img):
    '''
    '''
    aspect = float(img.get_width()) / img.get_height()
    width, height = adjust_size(aspect, quarter_aspect, *quarter_size)
    
    left, top = 1 + quarter_size[0], 1 + quarter_size[1]

    place_boxed_image(ctx, img, left, top, width, height)

def short_url(href):
    '''
    '''
    conn = HTTPConnection('teczno.com', 80)
    conn.request('POST', '/s/', urlencode({'url': href}), {'Content-Type': 'application/x-www-form-urlencoded'})
    resp = conn.getresponse()
    body = resp.read()
    
    assert resp.status in range(200, 299), (resp.status, body)
    
    return body.strip()

def place_text(ctx, text, href, x, y):
    '''
    '''
    width = sheet_width - 1.5
    right = x + width
    
    ctx.move_to(x, y)
    
    for word in text.split():
        w = ctx.text_extents(word + ' ')[4]
        
        if x + w > right:
            ctx.show_text('…')
            break
        
        ctx.move_to(x, y)
        ctx.show_text(word)
        
        x += w
    
    if not href:
        return
    
    ctx.move_to(0.5, y + .1)
    
    href = href
    
    while True:
        w = ctx.text_extents(href)[4]
        
        if w < width:
            ctx.show_text(href)
            break
        
        href = href[:-2] + u'…'
