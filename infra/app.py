#!/usr/bin/env python3
"""
CDK application entrypoint for the trading simulator infrastructure.

Usage (from the infra directory, after `uv sync`):

    uv run cdk synth
    uv run cdk deploy SimulatorStack
"""

import os

import aws_cdk as cdk

from simulator_stack import SimulatorStack


def main() -> None:
  app = cdk.App()

  # Allow overriding account/region via environment, but fall back to CDK defaults
  env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION"),
  )

  SimulatorStack(app, "SimulatorStack", env=env)

  app.synth()


if __name__ == "__main__":
  main()


