What Is Noode?
===============

Noodle is a simple graphing application. It's developed for displaying graphs of
service response times, but you should be able to graph other kinds of
time-scale data using it.

Noodle is currently pre-alpha; you can't do much other than look at some really
basic, incomplete graphs.

Noodle is implemented using Python, GTK, and Cairo. Currently you need GTK
installed to do anything interesting with it, but the graphing portion of the
code doesn't refer to GTK directly, so it should be possible to generate static
graphs (a la rrdtool) in the future.

Noodle is free software, licensed under the GPL version 3. Consult the LICENSE
file for the copyright and licensing details.
