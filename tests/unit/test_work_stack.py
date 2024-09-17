import aws_cdk as core
import aws_cdk.assertions as assertions

from work.work_stack import WorkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in work/work_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = WorkStack(app, "work")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
