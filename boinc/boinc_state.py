#!/usr/bin/env python3


from collections import defaultdict
from datetime import datetime
from pprint import pprint
import re
import subprocess


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

    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.url = data["master_url"]
        self.nomorework = data["don_t_request_more_work"] == "yes"
        self.tasks = self.get_tasks()

    def get_tasks(self):
        output = []
        tasks = BoincCmd(["--get_tasks"])
        for t, v in tasks.contents["tasks"].items():
            if v["project_url"] != self.url:
                continue
            output.append(v)
        return output

    def pending_tasks(self):
        """ This include all running and not started tasks """
        return [t for t in self.tasks if t["state"] == "downloaded"]

    def running_tasks(self):
        """ Tasks that are currently running """
        return [t for t in self.tasks if t["active_task_state"] == "EXECUTING"]

    def __repr__(self):
        output = "{name} | {remaining} tasks, {running} running".format(
            name=self.data["name"],
            remaining=len(self.pending_tasks()),
            running=len(self.running_tasks()),
        )
        if self.nomorework:
            output += ", no more new work"
        return output


def collect_projects():
    cmd = BoincCmd(["--get_project_status"])
    return [Project(p, v) for p, v in cmd.contents["projects"].items()]


def main():
    projects = collect_projects()
    print(datetime.now())
    print("\n".join([str(p) for p in projects]))


if __name__ == "__main__":
    main()
