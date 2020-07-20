import os
import sys
import zipfile
import optparse
import tempfile

import cobra
import cobra.remoteapp as c_remoteapp

def release():

    parser = optparse.OptionParser()

    parser.add_option('--cacert', dest='cacert', default=None )
    parser.add_option('--sslkey', dest='sslkey', default=None )
    parser.add_option('--sslcert', dest='sslcert', default=None )

    opts, argv = parser.parse_args()
    pyzfile, appuri = argv

    with open(__file__, 'rb') as f:
        mainsrc = f.read()
    mainlines = mainsrc.split('\n')[:-2]

    castr = 'None'
    keystr = 'None'
    certstr = 'None'

    if opts.cacert:
        with open(opts.cacert, 'rb') as f:
            castr = '"%s"' % f.read().encode('hex')

    if opts.sslkey:
        with open(opts.sslkey, 'rb') as f:
            keystr = '"%s"' % f.read().encode('hex')

    if opts.sslcert:
        with open(opts.sslcert, 'rb') as f:
            certstr = '"%s"' % f.read().encode('hex')

    mainlines.append('    appuri="%s"' % appuri)
    mainlines.append('    cacrt=%s' % castr)
    mainlines.append('    sslkey=%s' % keystr)
    mainlines.append('    sslcert=%s' % certstr)
    mainlines.append('    main(appuri, cacrt=cacrt, sslcert=sslcert, sslkey=sslkey)')

    mainsrc = '\n'.join(mainlines)

    pyz = zipfile.PyZipFile(pyzfile,'w')
    pyz.writepy('cobra')
    pyz.writestr('__main__.py',mainsrc)
    pyz.close()


def dumpfile(hexbytes,filepath):
    with open(filepath, 'wb') as f:
        f.write(hexbytes.decode('hex'))
    return filepath


def main(uri,cacrt=None,sslcert=None,sslkey=None):
    if any([cacrt,sslcert,sslkey]):
        scheme, host, port, name, urlparams = cobra.chopCobraUri( uri )
        builder = cobra.initSocketBuilder(host,port)

        tempdir = tempfile.mkdtemp()
        if cacrt:
            cafile = dumpfile(cacrt, os.path.join(tempdir,'ca.crt'))
            builder.setSslCa(cafile)

        if sslkey:
            keyfile = dumpfile(sslkey, os.path.join(tempdir,'client.key'))
            certfile = dumpfile(sslcert, os.path.join(tempdir,'client.crt'))
            builder.setSslClientCert(certfile,keyfile)

    try:
        c_remoteapp.getAndRunApp(uri)
    except Exception as e:
        print('error: %s' % e)

if __name__ == '__main__':
    sys.exit(release()) # this *must* be the *last* line...
