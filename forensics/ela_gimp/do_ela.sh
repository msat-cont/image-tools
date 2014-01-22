#!/bin/sh

INFILE="test.jpg"
TMPFILE="test_tmp.jpg"
OUTFILE="test_out.jpg"

date
gimp -c -d -f -i -n -s -b '(simple-ela "'$INFILE'" "'$TMPFILE'" "'$OUTFILE'" 0.95)' -b '(gimp-quit 0)'
date


