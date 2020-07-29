import ROOT as r
from array import array

def set_color_palette(name, alpha=1., ncontours=256):
    if name == "gray" or name == "grayscale":
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [1.00, 0.84, 0.61, 0.34, 0.00]
        green = [1.00, 0.84, 0.61, 0.34, 0.00]
        blue  = [1.00, 0.84, 0.61, 0.34, 0.00]
    elif name == "frenchFlag":
        stops = [0.00, 0.5, 1.00]
        red   = [0.00, 1.00, 1.00]
        green = [0.00, 1.00, 0.00]
        blue  = [1.00, 1.00, 0.00]
    elif name == "kBird":
        stops = [0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000]
        red   = [0.2082, 0.0592, 0.0780, 0.0232, 0.1802, 0.5301, 0.8186, 0.9956, 0.9764]
        green = [0.1664, 0.3599, 0.5041, 0.6419, 0.7178, 0.7492, 0.7328, 0.7862, 0.9832]
        blue  = [0.5293, 0.8684, 0.8385, 0.7914, 0.6425, 0.4662, 0.3499, 0.1968, 0.0539]
    elif name == "watermelon":
        stops = [0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000]
        red   = [ 19./255., 42./255., 64./255.,  88./255., 118./255., 147./255., 175./255., 187./255., 205./255.]
        green = [ 19./255., 55./255., 89./255., 125./255., 154./255., 169./255., 161./255., 129./255.,  70./255.]
        blue  = [ 19./255., 32./255., 47./255.,  70./255., 100./255., 128./255., 145./255., 130./255.,  75./255.]
    elif name == "pulls" :
        nStop = 12
        nc = nStop*1.
        stops = [0./nc, 1./nc, 1./nc, 5./nc, 5./nc, 7./nc, 7./nc, 11./nc, 11./nc, 12./nc]
        red   = [ 0.00,  0.00,  0.50,  0.90,  0.95,  0.95,  1.00,   1.00,   1.00,   1.00]
        green = [ 0.00,  0.00,  0.50,  0.90,  0.95,  0.95,  0.90,   0.50,   0.00,   0.00]
        blue  = [ 1.00,  1.00,  1.00,  1.00,  0.95,  0.95,  0.90,   0.50,   0.00,   0.00]
    elif name == "positive_pulls" :
        nStop = 10
        nc = nStop*1.
        stops = [0.00, 1.00]
        red   = [1.00, 1.00]
        green = [1.00, 0.00]
        blue  = [1.00, 0.00]
    elif name == "ed_noice" :
        nStop = 10
        nc = nStop*1.
        stops = [0.00, 1.00]
        red   = [1.00, 49./256.]
        green = [1.00, 163./256.]
        blue  = [1.00, 84./256.]
    elif name == "boring" :
        nStop = 10
        nc = nStop*1.
        stops = [0.00, 1.00]
        red   = [1.00, 1.00]
        green = [1.00, 1.00]
        blue  = [1.00, 1.00]
    elif name == "jonno_flip" :
        nStop = 100
        nc = nStop*1.
        stops = [0.00, 1.00]
        red   = [0.00, 1.00]
        green = [0.00, 1.00]
        blue  = [200./256, 1.00]
        #red   = [1.0, 45./256]
        #green = [1.0, 0.00]
        #blue  = [1.0, 160./256]

    elif name == "ed_noice_mig" :
        nStop = 10
        nc = nStop*1.
        stops = [0.00, 1.00]
        red   = [1.00, 49./256.]
        green = [1.00, 80./256.]
        blue  = [1.00, 163./256.]
    elif name == "ed_noice_ggh" :
        nStop = 10
        nc = nStop*1.
        stops = [0.00, 1.00]
        red   = [1.00, 0./256.]
        green = [1.00, 180./256.]
        blue  = [1.00, 220./256.]
    elif name == "ed_noice_qqh" :
        nStop = 10
        nc = nStop*1.
        stops = [0.00, 1.00]
        red   = [1.00, 250./256.]
        green = [1.00, 170./256.]
        blue  = [1.00, 0./256.]
    elif name == "exclusion95" :
        stops = [0.00, 0.34, 0.61, 0.84, 0.95, 0.95, 1.00]
        red   = [0.00, 0.00, 0.87, 1.00, 0.51, 0.00, 0.00]
        green = [0.00, 0.81, 1.00, 0.20, 0.00, 0.00, 0.00]
        blue  = [0.51, 1.00, 0.12, 0.00, 0.00, 0.00, 0.00]
    elif name == "exclusion05" :
        stops = [0.00, 0.05, 0.05, 0.34, 0.61, 0.84, 1.00]
        red   = [0.00, 0.00, 0.00, 0.00, 0.87, 1.00, 0.51]
        green = [0.00, 0.00, 0.00, 0.81, 1.00, 0.20, 0.00]
        blue  = [0.00, 0.00, 0.51, 1.00, 0.12, 0.00, 0.00]
    elif name == "":
        # default palette, looks cool
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red   = [0.00, 0.00, 0.87, 1.00, 0.51]
        green = [0.00, 0.81, 1.00, 0.20, 0.00]
        blue  = [0.51, 1.00, 0.12, 0.00, 0.00]
    else:
        raise AttributeError, "Palette '{0}' undefined".format(str(name))

    stops = array('d', stops)
    red   = array('d', red)
    green = array('d', green)
    blue  = array('d', blue)

    npoints = len(stops)
    r.TColor.CreateGradientColorTable(npoints, stops, red, green, blue, ncontours, alpha)
