#!/usr/bin/env python
"""
"""

from xml.etree.ElementTree import Element
import xml.etree.ElementTree as etree
import xml.dom.minidom
import re
import sys
import getopt
import os
from time import gmtime, strftime
from nipype import config, logging
from nighres.lesion_tool.lesion_pipeline import Lesion_extractor
    

def main():
    try:
        o, a = getopt.getopt(sys.argv[1:], "n:d:s:a:")
    except getopt.GetoptError as err:
        print(err)
        print('waimea.py -n <subjects_dir> -d <directory> -s <subject> -a <atlas>')
        sys.exit(2)
    if len(o) < 4:
        print('waimea.py -f <subjects_dir> -d <directory> -s <subject> -a <atlas>')
        sys.exit(2)
    for opt, arg in o:
        if opt == '-n':
            wf_name = arg
        elif opt == '-d':
            base_dir = arg
        elif opt == '-s':
            sub = arg
        elif opt == '-a':
            atlas = arg
            
    wf = Lesion_extractor(wf_name=wf_name,
                          base_dir=base_dir,
                          subjects=[sub],
                          #main=main,
                          #acc=acc,
                          atlas=atlas)
         
    config.update_config({'logging': {'log_directory': wf.base_dir,'log_to_file': True}})
    logging.update_logging(config)
    config.set('execution','job_finished_timeout','20.0')
    wf.config['execution'] = {'job_finished_timeout': '10.0'}
    try:
        wf.run()
    except:
        print('Error! Pipeline exited ')
        raise

if __name__ == "__main__":
    main()
    