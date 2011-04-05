'''
The ftp module is used to execute the logic used by the salt-ftp command
line application, salt-ftp is NOT intended to broadcast large files, it is
intened to handle text files.
Salt-ftp can be used to distribute configuration files
'''
# Import python modules
import os
import stat
import sys
# Import salt modules
import salt.client

class SaltFTP(object):
    '''
    Create a salt ftp object, used to distribute simple files with salt
    '''
    def __init__(self, opts):
        self.opts = opts

    def _file_dict(self, fn_):
        '''
        Take a path and return the contents of the file as a string
        '''
        if not os.path.isfile(fn_):
            err = 'The referenced file, ' + fn_ + ' is not available.'
            sys.stderr.write(err + '\n')
            sys.exit(42)
        return {fn_: open(fn_, 'r').read()}

    def _recurse_dir(self, fn_, files={}):
        '''
        Recursively pull files from a directory
        '''
        for base in os.listdir(fn_):
            path = os.path.join(fn_, base)
            if os.path.isdir(path):
                files.update(self._recurse_dir(path))
            else:
                files.update(self._file_dict(path))
        return files

    def _load_files(self):
        '''
        Parse the files indicated in opts['src'] and load them into a python
        object for transport
        '''
        files = {}
        for fn_ in self.opts['src']:
            if os.path.isfile(fn_):
                files.update(self._file_dict(fn_))
            elif os.path.isdir(fn_):
                files.update(self._recurse_dir(fn_))
        return files


    def run(self):
        '''
        Make the salt client call
        '''
        arg = [self._load_files(), self.opts['dest']]
        local = salt.client.LocalClient(self.opts['conf_file'])
        args = [self.opts['tgt'],
                'ftp.recv',
                arg,
                self.opts['timeout'],
                ]
        if self.opts['pcre']:
            args.append('pcre')
        elif self.opts['list']:
            args.append('list')
        elif self.opts['facter']:
            args.append('facter')
        
        ret = local.cmd(*args)

        print yaml.dump(ret)