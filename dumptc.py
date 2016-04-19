import stl
import timecode
import getopt
import sys
import re
import os

def usage():
    print "Usage: dump [OPTION] [FILE]..."
    print ""
    print "Options:"
    print "-h, --help  \tShow this help"
    print "-i, --input=\tInput STL file"
    print "\n"
    print "Report bugs to <ebilli@claxson.com>"


def main():
    try:
	opts, args = getopt.getopt(sys.argv[1:], "hi:", [ "help", "input="])
    except getopt.GetoptError as err:
	# print help information and exit:
        print str(err)
	usage()
        sys.exit(2)     
        
    file_in  = None
    for o,a in opts:
	if o == '-h':
	    usage()
	    sys.exit()
	elif o in ('-i', '--input'):
	    file_in = a
	else:
	    assert False, "unhandled option"


    if file_in is not None:
	subtitle = stl.STL()
	subtitle.load(file_in)
	i = 0
	tf_0 = subtitle.tti[0]
	tf_1 = subtitle.tti[1]

	print ("%s,%s,%s,%s,%s" % (file_in, tf_0.tci, tf_0.tco, tf_1.tci, tf_1.tco ))

    
if __name__ == "__main__":
    main()