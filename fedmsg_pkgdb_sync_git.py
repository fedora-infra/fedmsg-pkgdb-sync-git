# -*- coding: utf-8 -*-
""" A fedmsg consumer that listens to FAS messages to run pkgdb2branch via
Ansible

Authors:    Janez Nemanič <janez.nemanic@gmail.com>
            Ralph Bean <rbean@redhat.com>
            Pierre-Yves Chibon <pingou@pingoured.fr>

"""

import pprint
import subprocess
import fedmsg.consumers
import fedmsg.meta
import moksha.hub.reactor


class FasClientConsumer(fedmsg.consumers.FedmsgConsumer):

    # Because we are interested in a variety of topics, we tell moksha that
    # we're interested in all of them (it doesn't know how to do complicated
    # distinctions).  But then we'll filter later in our consume() method.
    topic = '*'
    interesting_topics = [
        'org.fedoraproject.prod.pkgdb.package.new',
        'org.fedoraproject.prod.pkgdb.package.branch.new',
    ]

    config_key = 'pkgdb2branch.consumer.enabled'

    def __init__(self, hub):
        super(FasClientConsumer, self).__init__(hub)

        # This is required.  It is the number of seconds that we should wait
        # until we ultimately act on a pkgdb message.
        self.delay = self.hub.config['pkgdb2branch.consumer.delay']

        # We use this to manage our state
        self.queued_messages = []

    def consume(self, msg):
        if msg['topic'] not in self.interesting_topics:
            return

        # Strip off moksha's outer envelope, which should always be present
        msg = msg.get('body', {})

        # Check to see if it's not crazy-malformed
        if 'msg' not in msg:
            self.log.warning("msg %r, %r is crazy malformed" % (
                msg.get('msg_id'), msg.get('topic')))
            return

        self.log.info("Got a message %r" % msg['topic'])

        def delayed_consume():
            if self.queued_messages:
                try:
                    self.action(self.queued_messages)
                finally:
                    # Empty our list at the end of the day.
                    self.queued_messages = []
            else:
                self.log.debug("Woke up, but there were no messages.")

        self.queued_messages.append(msg)

        moksha.hub.reactor.reactor.callLater(self.delay, delayed_consume)

    def action(self, messages):
        self.log.debug("Acting on %s" % pprint.pformat(messages))

        pkgs = set()
        for msg in messages:
            pkgs.update(fedmsg.meta.msg2packages(msg))

        command = '/usr/bin/sudo -i /usr/bin/ansible-playbook ' \
            '/srv/web/infra/ansible/playbooks/run_pkgdb_sync_git.yml '
        command = command.split()

        self.log.info("Running %r" % command)
        process = subprocess.Popen(args=command)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            self.log.info("%r was successful" % command)
        else:
            self.log.error("%r exited with %r, stdout: %s, stderr: %s" % (
                command, process.returncode, stdout, stderr))
