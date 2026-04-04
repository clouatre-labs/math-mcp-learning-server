#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2024 Hugues Clouâtre
# SPDX-License-Identifier: Apache-2.0
"""Demo script for math-mcp-learning-server. Used by assets/demo.tape only."""
import sys
import asyncio

sys.path.insert(0, "src")

from math_mcp.tools.calculate import calc_expression, calc_statistics, calc_interest, calc_units
from math_mcp.tools.persistence import workspace_save, workspace_load

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
DIM = "\033[2m"


def hdr(label):
    print(f"\n{BOLD}{CYAN}>>> {label}{RESET}")


def ok(label, value):
    print(f"  {GREEN}{label}:{RESET} {BOLD}{value}{RESET}")


def dim(label, value):
    print(f"  {DIM}{label}: {value}{RESET}")


async def main():
    print(f"{BOLD}math-mcp-learning-server  --  demo{RESET}")
    print(f"{DIM}17 tools  |  cloud: https://math-mcp.fastmcp.app/mcp{RESET}")

    hdr("calc_expression('2 * math.pi * 6371')")
    r = await calc_expression(expression="2 * math.pi * 6371")
    ok("result ", f"{r.result:,.4f} km")
    dim("topic  ", r.topic)

    hdr("calc_statistics([4, 8, 15, 16, 23, 42], 'mean')")
    r = await calc_statistics(numbers=[4, 8, 15, 16, 23, 42], operation="mean")
    ok("mean   ", f"{r.result:.4f}")
    r2 = await calc_statistics(numbers=[4, 8, 15, 16, 23, 42], operation="std_dev")
    ok("std_dev", f"{r2.result:.4f}")
    dim("n      ", r.sample_size)

    hdr("calc_interest(10000, rate=0.07, time=10)")
    r = await calc_interest(principal=10000, rate=0.07, time=10, compounds_per_year=12)
    ok("final  ", f"${r.final_amount:,.2f}")
    ok("profit ", f"${r.total_interest:,.2f}")
    dim("formula", r.formula)

    hdr("calc_units(100, 'km', 'mi')")
    r = await calc_units(value=100, from_unit="km", to_unit="mi", unit_type="length")
    ok("result ", f"{r.converted_value:.4f} mi")

    hdr("workspace_save('circumference', '2*math.pi*6371', 40030.17)")
    r = await workspace_save(name="circumference", expression="2 * math.pi * 6371", result=40030.17)
    ok("saved  ", r.name)
    ok("total  ", f"{r.total_variables} variables in workspace")

    hdr("workspace_load('circumference')")
    r = await workspace_load(name="circumference")
    ok("result ", r.result)
    ok("expr   ", r.expression)

    print(f"\n{DIM}Done.{RESET}\n")


asyncio.run(main())
