#!/usr/bin/env python3

import aws_cdk as cdk


from work.ck_stack import MyDemoStack
app = cdk.App()

MyDemoStack(app, "ck-stack")
app.synth()
