#!/bin/env python2
from __future__ import division
from path import Path
import re
from argparse import ArgumentParser

parser = ArgumentParser(description='A script to generate SFZ Mappings for drum samples by Analogue Drums.')
parser.add_argument('samplepath')
parser.add_argument('sfzfile')

volume = -6

instruments = {}
midi_layout = {
    'China-EG': (31,),
    'Stack-EG': (32,),
    'Splash-EG': (33,),
    'KickR-CN': (36,),
    'KickL-CN': (35,),
    'Snare3-XS': (37, 40),
    'Snare3-CN': (38,),
    'Tom6-CN': (41,),
    'Hihat-EC': (42, 68),
    'Tom5-CN': (43,),
    'Hihat-PD': (44,),
    'Tom4-CN': (45,),
    'Hihat-EO': (46, 72),
    'Tom3-CN': (47,),
    'Tom2-CN': (48,),
    'Crash1-BL': (49,),
    'Tom1-CN': (50,),
    'Ride-BW': (51,),
    'Crash2-EG': (52,),
    'Ride-BL': (53,),
    'Crash1-CH': (54,),
    'Crash1-EG': (55,),
    'Crash2-BL': (57,),
    'FXCrash-BL': (58,),
    'FXCrash-EG': (59,),
    'Crash2-CH': (56,),
    'Hihat-TT': (60,),
    'Hihat-TC': (61,),
    'Hihat-TL': (62,),
    'Hihat-TS': (63,),
    'Hihat-TO': (64,),
    'Hihat-FS': (66,),
    'Hihat-ET': (68,),
    'Hihat-EL': (70,),
    'Hihat-ES': (71,),
}

mic_layout = {
    'CM': 1,
    'KS': 2,
    'OH': 3,
    'RM': 4,
    'SB': 5,
    'SM': 6
}

filename_regex =\
    re.compile('^(?P<productname>[A-Z0-9]*)_(?P<instrument>[A-Za-z0-9]*)'
               '(?P<miclayer>CM|KS|OH|RM|SB|SM)[a-z]*RR(?P<roundrobin>[0-9])_'
               '(?P<lowvelocity>[0-9]{1,3})_(?P<highvelocity>[0-9]{1,3})_'
               '(?P<articulation>CN|XS|BW|BL|EG|TT|TC|TL|TS|TO|ET|EC|EL|ES|EO|FS|PD|CH)')

def main(samplepath, sfzfile):
    path = Path(samplepath)
    sfzfile = open(sfzfile, 'w')

    for dir in (path / 'Samples').dirs():
        if dir.basename() not in midi_layout:
            continue
        instruments_name = dir.basename()
        instruments[instruments_name] = {}
        for file in dir.files():
            result = filename_regex.match(str(file.basename()))
            if result.group('roundrobin') not in instruments[instruments_name]:
                instruments[instruments_name][result.group('roundrobin')] = []
            instruments[instruments_name][result.group('roundrobin')].append({
                'instrument': result.group('instrument'),
                'name': dir.basename() / file.basename(),
                'miclayer': result.group('miclayer'),
                'roundrobin': result.group('roundrobin'),
                'lowvelocity': result.group('lowvelocity'),
                'highvelocity': result.group('highvelocity'),
                'articulation': result.group('articulation'),
            })

    for name, instrument in instruments.iteritems():
        for key in midi_layout[name]:
            sfzfile.write('<group> volume={0} loop_mode=one_shot key={1}\n'.format(volume, key))

            for roundrobin, samplegroup in instrument.iteritems():
                for sample in samplegroup:
                    out = '<region> lovel={0} hivel={1} lorand={2} hirand={3} output={4} sample={5}\n'\
                        .format(sample['lowvelocity'], sample['highvelocity'],
                                float(int(sample['roundrobin'])-1)*(1.0/len(instrument)),
                                float(sample['roundrobin'])*(1.0/len(instrument)),
                                mic_layout[sample['miclayer']],
                                sample['name'])
                    sfzfile.write(out)

if __name__ == '__main__':
    args = parser.parse_args()
    main(args.samplepath, args.sfzfile)
