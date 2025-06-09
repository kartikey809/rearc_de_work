#!/usr/bin/env python3
import aws_cdk as cdk
from rearc_asn.rearc_asn_stack import RearcAsnStack  # Use your folder and class name

app = cdk.App()
RearcAsnStack(app, "RearcAsnStack")
app.synth()
