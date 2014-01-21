#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Base lib of VauxooTools
'''
from configglue import glue, schema, app, parser
from optparse import OptionParser
import logging


class VxConfig(schema.Schema):
    '''
    This class is to instanciate the `configglue`_ options to manage the
    configuration file and optparsers toghether. You will be able to load the
    configuration option from the command line and some of this 3 paths.::

        /etc/xdg/vauxootools/vauxootools.cfg
        /home/<user>/.config/vauxootools/vauxootools.cfg
        ./local.cfg

    The objective of this class is give a generic way to create all the config
    options you need almost always to interact openerp with.

    So as this is a normal python class you can always inherit it from your own
    script/tool and extend what you need.

    See vauxootools --help to read the configuration options available, you can
    create this files as any normal text file with the ini syntax.

    You can see below some options.

    .. _configglue: http://pythonhosted.org/configglue/
    '''

    hostname = schema.StringOption(short_name='H', default='localhost',
            help='Hostname of your OpenERP server.')
    dbname = schema.StringOption(short_name='D', default='development',
            help='Data base name where OpenERP has the information you need.')
    username = schema.StringOption(short_name='u', default='demo',
            help='User name to connect to the database')
    password = schema.StringOption(short_name='p', default='demo',
            help='Password of the username provided.')
    sadminpwd = schema.StringOption(short_name='S', default='demo',
            help='Super Admin Password to create data base.')
    port = schema.IntOption(short_name='P', default=8069,
            help='Port where your openerp is serving the web-service.')
    logfile = schema.StringOption(short_name='l', default='vauxootools.log',
            help='Where do you want the log of this configuration.')
    loglevel = schema.StringOption(short_name='L', default='DEBUG',
            help='Where do you want the log of this configuration.')

class VauxooTools(object):
    '''
    Vauxoo tools is the base class to manage the common features necesary to
    work with this library.
    '''
    def __init__(self, app_name='Vauxoo Tools',
                 usage_message='Generated by VauxooTools', options=None,
                 log=False, vx_instance=VxConfig):
        vxparser = OptionParser(usage=usage_message)
        self.config = vx_instance
        self.app_name = app_name
        self.logger = logging.getLogger(self.app_name)
        self.appconfig = app.App(self.config, parser=vxparser, name=app_name)
        self.scp = parser.SchemaConfigParser(self.config())
        self.options = options
        self.log = log
        self.params = self.get_options()
        self.logfile = self.params.get('logfile', 'default.log')
        self.loglevel = self.params.get('loglevel', 'DEBUG')
        self.set_logging()

    def set_logging(self):
        ch = logging.StreamHandler()
        logging.basicConfig(filename=self.logfile)
        self.logger.setLevel(self.loglevel.upper())
        formatter = logging.Formatter('%(levelname)s:[%(asctime)s] - '
                                      '%(name)s - %(message)s')
        ch.setFormatter(formatter)
        if self.log:
            self.logger.addHandler(ch)

    def get_options(self):
        '''With this method we will be pre-parsing options for our program,
        basically it is a parser to re-use configglue in the vauxoo's way, with
        the minimal configuration for our scripts, une time you instance the
        VauxooTools class in your script you will have available the minimal
        config parameter to be used against any openerp instance avoiding the
        need to re-implement the wheel any time you write a xml-rpc script with
        any of the tools availables.

        Instanciate the config in your application.

        >>> configuration = VauxooTools(app_name='TestApi',
        ...                             options=['hostname', 'port'])

        Ask for options.

        >>> result = configuration.get_options()
        >>> print result
        {'hostname': 'localhost', 'port': 8069, 'args': []}

        Where args will be the parameter passed to your script use it to
        receive parameters from the console.

        If you don't pass options you will receive an empty dict, with only the
        args key, you will need to valid both in your code to ensure it is
        empty if you need it.

        >>> configuration = VauxooTools(app_name='TestApi')
        >>> result = configuration.get_options()
        >>> print result
        {'args': []}
        '''
        result = {}
        options = self.options
        self.scp.read(self.appconfig.config.get_config_files(self.appconfig))
        opt, opts, args = glue.schemaconfigglue(self.scp)
        self.logger.info(opts)
        is_valid, reasons = self.scp.is_valid(report=True)
        if not is_valid:
            opt.error(reasons[0])
        values = self.scp.values('__main__')
        if options is not None:
            if self.log:
                options.append('logfile')
                options.append('loglevel')
            for option in options:
                value = values.get(option)
                result[option] = value
        else:
            pass
        result['args'] = args
        return result

    def get_hostname(self):
        '''Helper to get the normal parameters with less code, in this case
        openerp hostname.

        >>> configuration = VauxooTools(app_name='TestApi',
        ...                             options=['hostname', 'port'])
        >>> result = configuration.get_hostname()
        >>> print result
        localhost
        '''
        return self.params.get('hostname')

    def get_port(self):
        '''openerp hostname what we will connect to.

        >>> configuration = VauxooTools(app_name='TestApi',
        ...                             options=['hostname', 'port'])
        >>> result = configuration.get_port()
        >>> print result
        8069
        '''
        return self.params.get('port')

    def get_db(self):
        '''openerp data base what we will conect to.

        >>> configuration = VauxooTools(app_name='TestApi',
        ...                             options=['hostname', 'dbname'])
        >>> result = configuration.get_db()
        >>> print result
        development
        '''
        return self.params.get('dbname')

    def get_user(self):
        '''openerp data base what we will conect to.

        >>> configuration = VauxooTools(app_name='TestApi',
        ...                             options=['username', 'password'])
        >>> result = configuration.get_user()
        >>> print result
        demo
        '''
        return self.params.get('username')

    def get_pwd(self):
        '''openerp data base what we will conect to.

        >>> configuration = VauxooTools(app_name='TestApi',
        ...                             options=['username', 'password'])
        >>> result = configuration.get_pwd()
        >>> print result
        demo
        '''
        return self.params.get('password')

    def get_sadminpwd(self):
        '''openerp data base what we will conect to.

        >>> configuration = VauxooTools(app_name='TestApi',
        ...                             options=['sadminpwd', 'password'])
        >>> result = configuration.get_sadminpwd()
        >>> print result
        demo
        '''
        return self.params.get('sadminpwd')

class VxConfigServers(VxConfig):
    '''
    This class is to instanciate the `configglue`_ options to manage the
    configuration file and optparsers toghether. You will be able to load the
    configuration option from the command line and some of this 3 paths.::

        /etc/xdg/vauxootools/vauxootools.cfg
        /home/<user>/.config/vauxootools/vauxootools.cfg
        ./local.cfg

    The objective of this class is give a generic way to create all the config
    options you need almost always to interact openerp with.

    So as this is a normal python class you can always inherit it from your own
    script/tool and extend what you need.

    See vauxootools --help to read the configuration options available, you can
    create this files as any normal text file with the ini syntax.

    You can see below some options.

    .. _configglue: http://pythonhosted.org/configglue/
    '''

    sh = schema.StringOption(short_name='-sh', default='localhost',
            help='Hostname of your secondary OpenERP server.')
    sd = schema.StringOption(short_name='-sd', default='development',
            help='Secondary data base name where your secondary OpenERP '
            'has the information you need.')
    su = schema.StringOption(short_name='-su', default='demo',
            help='Secondary user name to connect to the database')
    sp = schema.StringOption(short_name='-sp', default='demo',
            help='Password of the secondary username provided.')
    spo = schema.IntOption(short_name='-spo', default=8069,
            help='Secondary port where your secondary openerp is serving '
            'the web-service.')
    il = schema.ListOption(short_name='-il', default=[0],
                           remove_duplicates=True,
            help='List of id or ids separate by comma without spaces of the '
            'leads that generated the task of create the instance to extract '
            'data of it')


class VauxooToolsServers(VauxooTools):
    '''
    Vauxoo tools is the base class to manage the common features necesary to
    work with this library.
    '''
    def __init__(self, app_name='Vauxoo Tools',
                 usage_message='Generated by VauxooTools',
                 options=None, log=False, vx_instance=VxConfigServers):
        super(VauxooToolsServers, self).__init__(app_name=app_name,
                                                 usage_message=usage_message,
                                                 options=options, log=log,
                                                 vx_instance=vx_instance)

    def get_shostname(self):
        '''openerp hostname what we will connect to.

        >>> configuration = VauxooTools(app_name='TestApi',
                                        options=['sh', 'sp'])
        >>> result = configuration.get_shostname()
        >>> print result
        localhost
        '''
        return self.params.get('sh')

    def get_sport(self):
        '''openerp port what we will connect to.

        >>> configuration = VauxooTools(app_name='TestApi',
                                        options=['sh', 'sp'])
        >>> result = configuration.get_sport()
        >>> print result
        8069
        '''
        return self.params.get('spo')

    def get_sdb(self):
        '''openerp data base what we will conect to.

        >>> configuration = VauxooTools(app_name='TestApi',
        ...                             options=['hostname', 'sd'])
        >>> result = configuration.get_sdb()
        >>> print result
        development
        '''
        return self.params.get('sd')

    def get_suser(self):
        '''openerp user what we will conect to.

        >>> configuration = VauxooTools(app_name='TestApi',
        ...                             options=['su', 'sp'])
        >>> result = configuration.get_suser()
        >>> print result
        demo
        '''
        return self.params.get('su')

    def get_spwd(self):
        '''User password what we will conect to.

        >>> configuration = VauxooTools(app_name='TestApi',
        ...                             options=['su', 'sp'])
        >>> result = configuration.get_spwd()
        >>> print result
        demo
        '''
        return self.params.get('sp')

    def get_records(self):
        '''Record ids to works.

        >>> configuration = VauxooTools(app_name='TestApi',
        ...                             options=['il'])
        >>> result = configuration.get_records()
        >>> print result
        [0]
        '''
        return self.params.get('il')

if __name__ == "__main__":
    import doctest
    doctest.testmod()
