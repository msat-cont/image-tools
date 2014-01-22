#!/bin/sh

date
gimp -c -d -f -i -n -s -b '(simple-copy-move "warning_clone.jpg" "warning_clone_out.jpg" 1 10)' -b '(gimp-quit 0)'
date

