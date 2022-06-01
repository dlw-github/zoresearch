'''
!/usr/bin/env python
coding: utf-8

DESCRIPTION:
Creates/updates a dictionary a PDF's annotations for use in Notes app.

INPUTS:
PDF file location, meta data

OUTPUTS:
Dictionary with PDF metadata and annotations
'''

# IMPORTS
import sys
import os
import fitz


def _check_contain(rect_annot, rect_reference, threshold=0.75):
    '''Check if word rectangle overlaps with annotation rectangle'''
    x_a1, y_a1, x_a2, y_a2 = rect_annot
    x_b1, y_b1, x_b2, y_b2 = rect_reference

    if x_a1 >= x_b2 or x_b1 >= x_a2:
        return False
    elif y_a1 >= y_b2 or y_b1 >= y_a2:
        return False
    else:
        b_area = (y_b2 - y_b1) * (x_b2 - x_b1)
        overlap_area = (
                        (min(y_a2, y_b2) - max(y_a1, y_b1))
                        * (min(x_a2, x_b2) - max(x_a1, x_b1))
                       )
        return (overlap_area / b_area) > threshold


def _iterate_words(page):
    '''Iterate through all words in a page and return word'''
    for wb in sorted(page.get_text('words'), key=lambda w: (w[1], w[0])):
        yield(wb)


def _get_highlight_text(annot):
    '''Get highlighted text'''
    annot_text_raw = ''
    rect_counts = len(annot.vertices) // 4
    for i in range(rect_counts):
        for word in _iterate_words(annot.parent):
            if _check_contain(
                              annot.vertices[i * 4]
                              + annot.vertices[(i * 4) + 3],
                              word[:4],
                             ):
                annot_text_raw = annot_text_raw + ' ' + word[4]
    return annot_text_raw


def _create_annot(annot, source):
    '''Create annot entry in source_entry dict
       for sticky comments and highlights
    '''
    # Get text from sticky comment
    if(annot.type[0] == 0):
        annot_text_raw = annot.info['content']

    # Get text from highlight
    elif(annot.type[0] == 8):
        annot_text_raw = _get_highlight_text(annot)

    # Create annot entry
    annot_text = ('PAGE '
                  + str(annot.parent.number + 1)
                  + ' ('
                  + annot.type[1]
                  + '): '
                  + annot_text_raw
                  )
    annot_entry = {
                       'page': annot.parent.number + 1,
                       'type': annot.type[1],
                       'text': annot_text
                       }

    # Append annot entry if not already present
    if annot_entry not in source['annots']:
        source['annots'].append(annot_entry)
        source['all_notes'] += '\n\n' + annot_text 
        print('\t\tAnnot added to dictionary')
    else:
        print('\t\tAnnot already in dictionary')


def _main(source):
    '''Main function'''
    try:
        file_path = os.path.normpath(source['file_loc'])
        doc = fitz.open(file_path)
        print('\tExtracting annotations')

        for page in doc.pages():
            for annot in page.annots():
                _create_annot(annot, source)
        return source
   
    except RuntimeError:
        print('\tNo PDF available')
        source['file_loc'] = None 
        return source

if __name__ == '__main__':
    _main(sys.argv[1])
