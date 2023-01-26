import os
import sys
# if w3lib is not found, run 
# python3 -m pip install w3lib
from w3lib.html import replace_entities 

# The name of the compiler we're testing
jcc = "./jeffc"

# Oracle base url, oracle number
o_url = "https://compilers.cool/oracles/o"
o_no = str(open("verify.cfg").read()) # Reads the config file output by `make testSuite`
oracle = o_url + o_no + '/'

# Oracle Response Boundaries
# These are used to seek to the start and end of each response section
# If either is not found, then the jeffc program should not emit any text for that file
o_out_start = 'OUTPUT FILE<br /><pre style="background:white;overflow:visible;padding-bottom:0px">'
o_err_start = 'STDERR<br /><pre style="background:white;overflow:visible">'
o_rsp_end = '<br /></pre>' # This is the same for both input and output

# Input prefix -- Must be followed by test number passed as argv[1]
test_dir = "./tests/"
pfx_in = test_dir + "test";

# File-type suffixes 
suf_in  = ".jeff"; 
suf_out = ".out";
suf_err = ".err";
suf_vfy = ".expected" # appended to out, err types
suf_dif = ".diff"

# Take in the test number
# File in must be pfx_in + tno + suf_in
# Files out will be pfx_in + tno + suf_out|suf_err
# Will be compared to pfx_in + tno + (suf_out+suf_vfy)|(suf_err+suf_vfy)
if __name__ == '__main__':
    tno = str(sys.argv[1])

    # Input file and output destinations
    infile = pfx_in + tno + suf_in;
    out = pfx_in + tno + suf_out;
    err = pfx_in + tno + suf_err;

    # Comparison files for out, err
    # N.B.: Right now these must be manually created before the test 
    #  using the oracle. Once the oracle is exposed by the API, can be
    #  created on demand
    v_out = out + suf_vfy;
    v_err = err + suf_vfy;

    # Curl the oracle to get verified outputs
    # cmd = "curl -v -X POST -d @" + infile + " -H \"Content-Disposition: form-data; name=\\\"input\\\"; filename=\\\"" + infile + "\\\" Content-Type: application/octet-stream\" " + oracle
    o_rsp = "./o_rsp.tmp"
    cmd = "curl -s -F \"input=@" + infile + "\" " + oracle + " >> " + o_rsp
    os.system(cmd)
    f = open(o_rsp); # Read the query response file
    v = replace_entities(f.read()); # 'v' is verified output from the oracle
    os.system("rm " + o_rsp) # Remove the query response file since we have the text

    v_out_txt = ""
    ts = v.find(o_out_start) # Where expected output starts
    te = v.find(o_rsp_end, ts) # where expected output ends
    if (ts != -1) :
        ts += len(o_out_start)
        v_out_txt = v[ts:te]
    
    v_err_txt = ""
    ts = v.find(o_err_start) # Where expected output starts
    te = v.find(o_rsp_end, ts) # where expected output ends
    if (ts != -1) :
        ts += len(o_err_start)
        v_err_txt = v[ts:te]
    
    f = open(v_out, "w")
    f.write(v_out_txt)
    f.close()
    f = open(v_err, "w")
    f.write(v_err_txt)
    f.close()


    # Run the test and generate / overwrite the out, err files
    cmd = jcc + " " + infile + " -t " + out + " 2> " + err
    os.system(cmd)

    # Compare the output
    res_file = pfx_in + tno + suf_out + suf_dif;
    cmd = "diff --strip-trailing-cr " + str(out) + " " + str(v_out) + " 2>" + res_file + " >>" + res_file
    os.system(cmd)
    if os.stat(res_file).st_size == 0:
        print('Test ' + tno + ' - PASS: Outputs.')
    else:
        print('Test ' + tno + ' - ERROR: Outputs do not match. See ' + res_file + '.')

    # Compare the errors
    res_file = pfx_in + tno + suf_err + suf_dif;
    cmd = "diff --strip-trailing-cr " + str(err) + " " + str(v_err) + " 2>" + res_file + " >>" + res_file
    os.system(cmd)
    if os.stat(res_file).st_size == 0:
        print('Test ' + tno + ' - PASS: Errors.\n')
    else:
        print('Test ' + tno + ' - ERROR: Errors do not match. See ' + res_file + '.\n')
