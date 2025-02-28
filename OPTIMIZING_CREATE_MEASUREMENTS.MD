# Optimizing the create_measurements.py tool  
I thought optimizing the create measurements tool could also be a interesting project, it has a slightly different set of needs, and, well its another challenge and good for practice. All versions of this will be found in the commit history. :) Also I realize that there is an implementation of this exact tool also located in the official 1BRC challenge, remember this is a learning experience for me.

Here you will find my notes and process I took for this optimization.

# The Basic Build
First things first, I need a basic functioning tool. This will be a pretty inefficient tool. 

Some requirements:
 - Key distribution should be fairly even
 - Able to specify the number of Rows
 - User friendly
   - It should have a progress bar
 - Should only use native python libraries


Now the full code of this can be found in the `unoptimized/create_measurements_unoptimized.py' file. from now on il use simple code snippets to show the changes I make.