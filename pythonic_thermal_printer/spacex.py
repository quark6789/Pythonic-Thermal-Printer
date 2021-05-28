#!/usr/bin/env python3

import textwrap
import time
from datetime import datetime
from tempfile import TemporaryFile

import pytz
import requests

import Adafruit_Thermal


LOCAL_TIMEZONE = pytz.timezone("US/Pacific")


def get_launch(id: str):
    response = requests.get(f"https://api.spacexdata.com/v4/launches/{id}")
    response.raise_for_status()
    return response.json()


def get_next_launch():
    response = requests.get("https://api.spacexdata.com/v4/launches/next")
    response.raise_for_status()
    return response.json()


def print_launch(printer: Adafruit_Thermal, launch: dict):
    # TODO: Rearrange code to make error catching more robust
    if launch["links"]["patch"]["small"]:
        with TemporaryFile() as launch_patch_file:
            launch_patch_response = requests.get(launch["links"]["patch"]["small"])
            if launch_patch_response.ok:
                launch_patch_file.write(launch_patch_response.content)
                printer.printImage(launch_patch_file)
    else:
        printer.printImage("gfx/spacex.png")

    with printer.format(doubleHeight=True, doubleWidth=True):
        printer.println(launch["name"])

    launch_time = datetime.fromtimestamp(launch["date_unix"])
    launch_time = launch_time.astimezone(LOCAL_TIMEZONE)
    printer.println(launch_time.strftime(r"%b %d, %Y"))
    with printer.format(bold=True):
        printer.println(launch_time.strftime(r"%a %I:%M %p"))

    printer.println(textwrap.fill(launch["details"],
                                  width=Adafruit_Thermal.MAX_CHARS_PER_LINE))


def main():
    printer = Adafruit_Thermal.Adafruit_Thermal("/dev/serial0", 19200, timeout=5)
    printer.println()  # TODO: Find out why it always prints a J at the start
    print_launch(printer, get_next_launch())
    printer.feed(2)
    time.sleep(7)
    print_launch(printer, get_launch("5eb87d42ffd86e000604b384"))
    printer.feed(3)


if __name__ == "__main__":
    main()
