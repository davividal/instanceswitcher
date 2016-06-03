from termcolor import colored
import boto3
import os
import yaml


class Configer(object):
    def setup(self):
        raise NotImplementedError

    def pre_test(self, *args, **kwargs):
        raise NotImplementedError


class PuppetConf(Configer):
    puppet_common = 'puppet/common.yaml'

    def setup(self):
        f = open(self.puppet_common)
        self.puppet_yml = yaml.safe_load(f)
        f.close()

    def pre_test(self, ip, hosts):
        print('{:<25}'.format('Changing IP locally... '), end='', flush=True)

        self.puppet_yml['setuphosts::ip'] = ip
        self.puppet_yml['setuphosts::hostname'] = hosts[0]
        self.puppet_yml['setuphosts::host_aliases'] = hosts[1:]

        f = open(self.puppet_common, 'w')
        yaml.dump(self.puppet_yml, f, explicit_start=True)
        f.close()

        os.system('sudo puppet/puppet_wrapper.sh')

        print("{:>8}".format(colored('[ OK ]', 'green')))

    def shutdown(self):
        os.system('sudo puppet/puppet_wrapper.sh shutdown')


class Application(object):
    instances = []

    def __init__(self, name, elb, hosts):
        self.name = name
        self.elb = elb
        self.hosts = sorted(list(set(hosts)))

    def __str__(self):
        return self.name

    def get_instances(self):
        client = boto3.client('elb')

        app = client.describe_load_balancers(LoadBalancerNames=[self.elb])

        self.instances = []
        for i in app['LoadBalancerDescriptions'][0]['Instances']:
            self.instances.append(Instance(i['InstanceId']))

        self.instances = iter(self.instances)


class Instance(object):
    instance_id = None
    instance_ip = None

    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.instance_ip = self.get_instance_ip(instance_id)

    def get_instance_ip(self, instance_id):
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(instance_id)

        return instance.private_ip_address


class Settings(object):
    apps = []
    configer = None

    @classmethod
    def init(cls):
        cls.configer = PuppetConf()

        cls.apps = []

        f = open('settings.yaml')
        settings = yaml.safe_load(f)
        f.close

        for app in settings['applications']:
            cls.apps.append(Application(**app))


def menu(apps):
    while True:
        print("Chose an application:")

        for k, app in enumerate(apps):
            print(
                "[{0}] {1}".format(
                    colored(k, 'blue'),
                    app
                )
            )

        print("[{0}] Quit".format(colored('Q', 'blue')))
        ans = input('>>> ')

        if ans.lower() == 'q':
            break

        try:
            choosen = apps[int(ans)]
        except (IndexError, ValueError):
            continue

        choosen.get_instances()
        while True:
            try:
                instance = next(choosen.instances)
            except StopIteration:
                print('No more instances to test!')
                break

            Settings.configer.pre_test(instance.instance_ip, choosen.hosts)
            print("Ready to test another instance? [Yn]")
            continue_test = input('>>> ')

            if continue_test.lower() == 'n':
                break
            else:
                continue
        Settings.configer.shutdown()


if __name__ == '__main__':
    Settings.init()
    Settings.configer.setup()

    menu(Settings.apps)
