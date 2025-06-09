import aws_cdk as core
import aws_cdk.assertions as assertions

from rearc_asn.rearc_asn_stack import RearcAsnStack

# example tests. To run these tests, uncomment this file along with the example
# resource in rearc_asn/rearc_asn_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RearcAsnStack(app, "rearc-asn")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
