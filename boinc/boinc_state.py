#!/usr/bin/env python3


from collections import defaultdict
from datetime import datetime
import logging
from pprint import pprint
import psutil
import re
import subprocess
import sys


logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger()


class BoincCmd:

    CLI = "boinccmd"

    def __init__(self, cmd, key_by_name=True):
        result = subprocess.run([self.CLI] + cmd, stdout=subprocess.PIPE)
        contents = self.parse(result.stdout.decode("utf-8").split("\n"))
        if key_by_name:
            self.contents = self.key_by_name(contents)
        else:
            self.contents = contents

    @classmethod
    def sanitize(self, value):
        replace = re.compile("\W")
        return replace.sub("_", value.strip().lower())

    @classmethod
    def parse(self, lines):
        output = defaultdict(lambda: defaultdict(dict))
        header_re = re.compile("======== (.*) ========")
        section_re = re.compile("(\d+)\) -----------")
        field_re = re.compile("\s+([^:]+): (.*)")
        for line in lines:
            m = header_re.match(line)
            if m:
                header = self.sanitize(m.group(1))
            m = section_re.match(line)
            if m:
                section = int(self.sanitize(m.group(1)))
            m = field_re.match(line)
            if m:
                name = self.sanitize(m.group(1))
                value = m.group(2)
                # all interesting stuff is on top. Ignore later garbage
                output[header][section].setdefault(name, value)
        return output

    def key_by_name(self, input_val):
        if not isinstance(input_val, dict):
            return input_val

        output = {}
        for key, val in input_val.items():
            if isinstance(key, int):
                if val["name"] in output:
                    raise ValueError(
                        "Duplicated names {} at {}".format(val["name"], key)
                    )
                output[self.sanitize(val["name"])] = self.key_by_name(val)
            else:
                output[key] = self.key_by_name(val)
        return output


class Project:

    FORMAT_STRING = "{name} | {remaining} tasks, {running} running"

    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.url = data["master_url"]
        self.nomorework = data["don_t_request_more_work"] == "yes"
        self.suspended = data["suspended_via_gui"] == "yes"
        self.tasks = self.get_tasks()

    @classmethod
    def get_all_tasks(self):
        output = []
        tasks = BoincCmd(["--get_tasks"])
        if not tasks:
            return []
        return list(tasks.contents["tasks"].values())

    def get_tasks(self):
        output = []
        tasks = self.get_all_tasks()
        for t in tasks:
            if t["project_url"] != self.url:
                continue
            output.append(t)
        return output

    @classmethod
    def pending_tasks(self, tasks):
        """ This include all running and not started tasks """
        return [t for t in tasks if t["state"] == "downloaded"]

    @classmethod
    def running_tasks(self, tasks):
        """ Tasks that are currently running """
        return [t for t in tasks if t["active_task_state"] == "EXECUTING"]

    def __repr__(self):
        output = self.FORMAT_STRING.format(
            name=self.data["name"],
            remaining=len(self.pending_tasks(self.tasks)),
            running=len(self.running_tasks(self.tasks)),
        )
        if self.nomorework:
            output += ", no more new work"
        if self.suspended:
            output += ", suspended"
        return output


def collect_projects():
    cmd = BoincCmd(["--get_project_status"])
    return [Project(p, v) for p, v in cmd.contents["projects"].items()]


def main():
    psutil.cpu_percent()
    projects = collect_projects()
    all_tasks = Project.get_all_tasks()
    logger.info(
        Project.FORMAT_STRING.format(
            name="Overview",
            remaining=len(Project.pending_tasks(all_tasks)),
            running=len(Project.running_tasks(all_tasks)),
        ) + ", util {0:.2f}%".format(psutil.cpu_percent())
    )
    for p in projects:
        logger.info(str(p))


if __name__ == "__main__":
    main()
