from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_lambda_event_sources as lambda_events,
    aws_events as events,
    aws_events_targets as targets,
    aws_s3_notifications as s3n,
)
from constructs import Construct
import os

class RearcAsnStack(Stack): 

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket.from_bucket_name(self, "BlsStagingBucket", "bucket-staging-s3")

        # Common access dep layer for requirements
        layer = _lambda.LayerVersion(
            self, "CommonDependenciesLayer",
            code=_lambda.Code.from_asset("rearc_asn/lambda_layer",
                bundling=_lambda.BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_11.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -r /asset-input/requirements.txt -t /asset-output/python && cp -r /asset-input/* /asset-output/"
                    ],
                    volumes=[],
                    working_directory="/asset-input",
                    user="root"
                )
            ),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="Layer containing dependencies from requirements.txt",
        )

        # BLS + USA POP ingestion Lambda
        ingest_lambda = _lambda.Function(
            self, "IngestLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("rearc_asn/lambdas/bls_and_population_ingest"),
            layers=[layer],
            environment={
                "BUCKET_NAME": "bucket-staging-s3"
            },
            timeout=Duration.minutes(5)
        )
        bucket.grant_read_write(ingest_lambda)

        # EventBridge rule for daily ingest
        rule = events.Rule(
            self, "DailyTrigger",
            schedule=events.Schedule.rate(Duration.days(1))
        )
        rule.add_target(targets.LambdaFunction(ingest_lambda))

        # SQS queue for EDA trigger
        queue = sqs.Queue(self, "PopulationSQS", visibility_timeout=Duration.seconds(600))

        # EDA Lambda
        eda_lambda = _lambda.Function(
            self, "EdaReportLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("rearc_asn/lambdas/eda_report"),
            layers=[layer],
            environment={
                "BUCKET_NAME": "bucket-staging-s3"
            },
            timeout=Duration.minutes(5)
        )
        bucket.grant_read_write(eda_lambda)
        eda_lambda.add_event_source(lambda_events.SqsEventSource(queue))

        # S3 → SQS Notification
        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.SqsDestination(queue),
            s3.NotificationKeyFilter(prefix="datausa/", suffix=".json")
        )
