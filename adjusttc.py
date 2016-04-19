import stl
import timecode
import getopt
import sys
import re
import os

def usage():
    print "Usage: adjusttc.py [OPTION] [FILE]..."
    print "Modify the initial and final timecode of a STL subtitle"
    print ""
    print "Options:"
    print "-i, --input=\tInput STL file"
    print "-o, --output=\tOutput STL file"
    print "-a, --add=\tTimecode that need to be added for each TCI/TCO"
    print "-s, --sub=\tTimecode that need to be substracted for each TCI/TCO"
    print "\t\tTimecode Format:\tHH:MM:SS:FF | HH:MM:SS;FF\n"
    print "-n, --number\tOptional Argument: From that subtitle makes changes"
    print "-h, --help\tDisplay this help"
    print "-d, --dump\tOnly dumps Subtitle Number, TCI, TCO"
    print "-f, --force\tForce Story and Lang correction based in STORY_LANG*.stl filename"
    print "-p, --prefix\tAdd Story Prefix if not exist"
    print "-2, --two\tShow the first 2 TCI and TCO and only the first Text"
    print "-8, --eight\tForce SOM in 00:00:00;00 to 00:00:00;08 in the first subtitle"
    print "-c, --clean\tClean second line"
    print "-e, --export\tExport a .sub subtitle"
    print "\n"
    print "Report bugs to <ebilli@claxson.com>"


def split_filename(file_in=''):
    if file_in is not '' and (file_in.endswith('.stl') or file_in.endswith('.STL')):

	if os.name == 'nt':
	    separator = '\\'
	elif os.name == 'posix':
	    separator = '/'
    	
	path = file_in.split(separator)
	file = path[len(path)-1]    
	result = re.match('(.+)_(ESP|PRT)(\.|_)', file)
	if result:
	    return result.group(1), result.group(2)
	else:
	    raise
    else:
	raise	


def main():
    try:
	opts, args = getopt.getopt(sys.argv[1:], "hdi:o:a:s:n:p:f28ce:", [ "help", "dump", "input=","output=","add=", "sub=", "number=", "prefix=", "force", "two", "eight", "clean", "export="])
    except getopt.GetoptError as err:
	# print help information and exit:
	print "xxx"    
        print str(err)
	usage()
        sys.exit(2)     
        
    file_in  = None
    file_out = None
    tc     = None 
    add    = None
    num    = 0
    dump   = False
    force  = False
    prefix = ''
    two    = False
    eight  = False
    clean_second_line = False
    export = False
    export_file = None
    
    for o,a in opts:
	if o == '-h':
	    usage()
	    sys.exit()
	elif o in ('-d', '--dump'):
	    dump = True
	elif o in ('-i', '--input'):
	    file_in = a
	elif o in ('-o', '--output'):
	    file_out = a
	    if os.path.isfile(file_out):
		print "[Warning] Overwrite dst"
	elif o in ('-a', '--add'):
	    tc = timecode.fromString(a)
	    add = True
	elif o in ('-s', '--sub'):
	    tc = timecode.fromString(a)
	    add = False
	elif o in ('-n', '--number'):
	    num = int(a)
	elif o in ('-f', '--force'):
	    force = True
	elif o in ('-p', '--prefix'):
	    prefix = a    
	elif o in ('-2', '--two'):
	    two    = True
	elif o in ('-8', '--eight'):
	    eight  = True
	elif o in ('-c', '--clean'):
	    clean_second_line = True    
	elif o in ('-e', '--export'):
	    export = True
	    export_file = a    
	else:
	    assert False, "unhandled option"

    if export == True and file_in is not None and export_file is not None:
	subtitle = stl.STL()
	subtitle.load(file_in)
	subtitle.export(export_file, 'srt', '00:00:00;00')
	return 

    if dump == True and file_in is not None:
	subtitle = stl.STL()
	subtitle.load(file_in)
	i = 0
	print '-------------------------------------------------------'
	print file_in
	for tf in subtitle.tti:
	    if two and (i == 0 or i == 1):
		print ("SGN: %d, SN: %d, EBN: %d, CS:%d: - %s -> %s - VP: %d, JC: %d, CF: %d, TF: %s") % (tf.sgn,tf.sn,tf.ebn, tf.cs, tf.tci, tf.tco, tf.vp, tf.jc, tf.cf, tf.tf.encode_utf8())
	    else:
		print ("SGN: %d, SN: %d, EBN: %d, CS:%d: - %s -> %s - VP: %d, JC: %d, CF: %d") % (tf.sgn,tf.sn,tf.ebn, tf.cs, tf.tci, tf.tco, tf.vp, tf.jc, tf.cf)
	    if two:
		if i >= 1:
		    break;
	    i = i + 1
	print '-------------------------------------------------------'

    else:
	if file_in is not None and file_out is not None and (tc is not None or eight == True or clean_second_line == True):
	    print file_in
	    subtitle = stl.STL()
	    subtitle.load(file_in)
	    i = 0
	    for tf in subtitle.tti:
		if i == 0 and force == True:
		    try:
			story_tmp, lang = split_filename(file_in)
	
		        if prefix != '':
		    	    if story_tmp.startswith(prefix):
		    		story = story_tmp
		    	    else:
		    		story = prefix +  story_tmp
		    	else:
		    	    story = story_tmp
		    	
		    	if eight == True:
		    	    tf.tci = timecode.fromString('00:00:00;00')
		    	    tf.tco = timecode.fromString('00:00:00;08')
		    	
		        line_zero = bytearray(b'STORY: %s\x8aLANG: %s' % (story, lang))			
		        j = 0
			while j < 112:
		    	    tf.tf.tf[j] = b'\x8f'
		    	    j = j + 1
			j = 0
		        while j < len(line_zero):
			    tf.tf.tf[j] = line_zero[j]
		    	    j = j + 1    
		    except:
			print "Error in filename: %s, expected: STORY_LANG*.stl" % file_in
		        sys.exit(2)

		if i == 1 and clean_second_line == True:
		    tsl = timecode.fromString('00:00:00;08')
		    if tf.tco == tsl:
			j = 0
			while j < 112:
		    	    tf.tf.tf[j] = b'\x8f'
		    	    j = j + 1
		
		if i >= num and tc is not None:
		    if add:
			tf.tci = tf.tci + tc
	    	        tf.tco = tf.tco + tc
		    else:
			tf.tci = tf.tci - tc
		        tf.tco = tf.tco - tc
		i = i + 1
	    subtitle.save(file_out)
	else:
	    usage()
	    sys.exit()	    
    
if __name__ == "__main__":
    main()