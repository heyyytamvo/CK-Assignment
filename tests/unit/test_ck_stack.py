import aws_cdk as core
import aws_cdk.assertions as assertions

from ck.ck_stack import CkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ck/ck_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CkStack(app, "ck")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
