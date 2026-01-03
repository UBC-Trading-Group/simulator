"""
Main CDK stack for the trading simulator.

This provisions:
- VPC (public + private subnets)
- RDS Postgres for the main database
- ElastiCache Redis for caching / leaderboard
- ECS Fargate service running the FastAPI backend behind an ALB
- S3 bucket + CloudFront distribution for the Vite React frontend
"""

from pathlib import Path
from typing import Dict

import aws_cdk as cdk
from aws_cdk import Duration, RemovalPolicy, Stack
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_elasticache as elasticache
from aws_cdk import aws_logs as logs
from aws_cdk import aws_rds as rds
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3_deployment
from aws_cdk import aws_secretsmanager as secretsmanager


class SimulatorStack(Stack):
    def __init__(self, scope: cdk.App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = self._create_vpc()

        db_instance = self._create_rds(vpc)

        redis = self._create_redis(vpc)

        backend_service = self._create_backend_service(
            vpc=vpc,
            db_instance=db_instance,
            redis=redis,
        )

        frontend_distribution = self._create_frontend(backend_service)

        # Allow ECS tasks to reach DB and Redis
        db_instance.connections.allow_default_port_from(
            backend_service.service,
            "Allow backend to access Postgres",
        )

        if isinstance(redis, elasticache.CfnCacheCluster):
            # Security is handled via security groups configured in _create_redis
            pass

        # Outputs
        cdk.CfnOutput(
            self,
            "BackendUrl",
            value=f"http://{backend_service.load_balancer.load_balancer_dns_name}",
            description="Public URL for the FastAPI backend (via ALB).",
        )

        cdk.CfnOutput(
            self,
            "FrontendUrl",
            value=f"https://{frontend_distribution.domain_name}",
            description="Public URL for the CloudFront distribution serving the frontend.",
        )

    # --- VPC -----------------------------------------------------------------

    def _create_vpc(self) -> ec2.Vpc:
        return ec2.Vpc(
            self,
            "SimulatorVpc",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                ),
                ec2.SubnetConfiguration(
                    name="private-with-egress",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                ),
            ],
        )

    # --- RDS -----------------------------------------------------------------

    def _create_rds(self, vpc: ec2.IVpc) -> rds.DatabaseInstance:
        db_name = "simdb"

        db_instance = rds.DatabaseInstance(
            self,
            "SimulatorPostgres",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15,
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            credentials=rds.Credentials.from_generated_secret("simuser"),
            multi_az=False,
            allocated_storage=20,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO,
            ),
            publicly_accessible=False,
            deletion_protection=False,
            removal_policy=RemovalPolicy.DESTROY,
            database_name=db_name,
        )

        # Secret containing username/password for the DB
        db_credentials_secret = db_instance.secret
        if db_credentials_secret is None:
            raise ValueError("Expected RDS instance to have an attached secret")

        # Ensure the secret is deleted when stack is destroyed
        db_credentials_secret.apply_removal_policy(RemovalPolicy.DESTROY)

        # Attach for later use (ECS task environment)
        self._db_credentials_secret = db_credentials_secret
        self._db_name = db_name

        return db_instance

    # --- Redis / ElastiCache -------------------------------------------------

    def _create_redis(self, vpc: ec2.IVpc) -> elasticache.CfnCacheCluster:
        subnet_group = elasticache.CfnSubnetGroup(
            self,
            "RedisSubnetGroup",
            description="Subnet group for simulator Redis",
            subnet_ids=[
                subnet.subnet_id
                for subnet in vpc.select_subnets(
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                ).subnets
            ],
        )

        redis_sg = ec2.SecurityGroup(
            self,
            "RedisSecurityGroup",
            vpc=vpc,
            description="Security group for ElastiCache Redis",
            allow_all_outbound=True,
        )

        cache_cluster = elasticache.CfnCacheCluster(
            self,
            "RedisCluster",
            engine="redis",
            cache_node_type="cache.t3.micro",
            num_cache_nodes=1,
            cache_subnet_group_name=subnet_group.ref,
            vpc_security_group_ids=[redis_sg.security_group_id],
        )

        # Store primary node endpoint as a secret-formatted URL (single-node cluster has no configuration endpoint)
        redis_url_secret = secretsmanager.Secret(
            self,
            "RedisUrlSecret",
            description="Redis connection URL for the trading simulator backend.",
            secret_string_value=cdk.SecretValue.unsafe_plain_text(
                "redis://{host}:{port}".format(
                    host=cache_cluster.attr_redis_endpoint_address,
                    port=cache_cluster.attr_redis_endpoint_port,
                )
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )
        self._redis_url_secret = redis_url_secret
        self._redis_security_group = redis_sg

        return cache_cluster

    # --- ECS backend ---------------------------------------------------------

    def _create_backend_service(
        self,
        vpc: ec2.IVpc,
        db_instance: rds.DatabaseInstance,
        redis: elasticache.CfnCacheCluster,
    ) -> ecs_patterns.ApplicationLoadBalancedFargateService:
        cluster = ecs.Cluster(self, "SimulatorCluster", vpc=vpc)

        log_group = logs.LogGroup(
            self,
            "BackendLogGroup",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Security group for ECS tasks
        service_sg = ec2.SecurityGroup(
            self,
            "BackendServiceSecurityGroup",
            vpc=vpc,
            description="Security group for backend ECS tasks",
            allow_all_outbound=True,
        )

        # Allow backend to reach Redis
        self._redis_security_group.add_ingress_rule(
            peer=service_sg,
            connection=ec2.Port.tcp(6379),
            description="Allow backend tasks to connect to Redis",
        )

        environment: Dict[str, str] = {
            "LOG_LEVEL": "INFO",
            # Allow CORS from anywhere for now; you can tighten this later.
            "BACKEND_CORS_ORIGINS": '["*"]',
            "DB_HOST": db_instance.db_instance_endpoint_address,
            "DB_PORT": db_instance.db_instance_endpoint_port,
            "DB_NAME": self._db_name,
        }

        secrets_env: Dict[str, ecs.Secret] = {
            "DB_USERNAME": ecs.Secret.from_secrets_manager(
                self._db_credentials_secret,
                field="username",
            ),
            "DB_PASSWORD": ecs.Secret.from_secrets_manager(
                self._db_credentials_secret,
                field="password",
            ),
            "REDIS_URL": ecs.Secret.from_secrets_manager(self._redis_url_secret),
        }

        task_image_options = ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
            image=ecs.ContainerImage.from_asset("../backend"),
            container_port=8000,
            environment=environment,
            secrets=secrets_env,
            log_driver=ecs.LogDriver.aws_logs(
                stream_prefix="backend",
                log_group=log_group,
            ),
        )

        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "BackendService",
            cluster=cluster,
            cpu=512,
            memory_limit_mib=1024,
            desired_count=1,
            public_load_balancer=True,
            task_image_options=task_image_options,
            assign_public_ip=False,
            security_groups=[service_sg],
            listener_port=80,
        )

        # Health check tuning (optional)
        service.target_group.configure_health_check(
            path="/health",
            healthy_http_codes="200-399",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5),
            healthy_threshold_count=2,
            unhealthy_threshold_count=5,
        )

        return service

    # --- Frontend ------------------------------------------------------------

    def _create_frontend(
        self, backend_service: ecs_patterns.ApplicationLoadBalancedFargateService
    ) -> cloudfront.Distribution:
        bucket = s3.Bucket(
            self,
            "FrontendBucket",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # Create backend origin for API and WebSocket
        backend_origin = origins.HttpOrigin(
            backend_service.load_balancer.load_balancer_dns_name,
            protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
            http_port=80,
        )

        distribution = cloudfront.Distribution(
            self,
            "FrontendDistribution",
            default_root_object="index.html",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            additional_behaviors={
                "/api/*": cloudfront.BehaviorOptions(
                    origin=backend_origin,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                ),
                "/ws/*": cloudfront.BehaviorOptions(
                    origin=backend_origin,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                ),
            },
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(5),
                )
            ],
        )

        # Deploy built assets from the frontend dist directory
        frontend_dist_path = Path(__file__).parent.parent / "frontend" / "dist"
        if not frontend_dist_path.exists() or not frontend_dist_path.is_dir():
            raise FileNotFoundError(
                f"Frontend dist directory not found at {frontend_dist_path}. "
                "Please build the frontend first by running 'npm run build' in the frontend directory."
            )

        s3_deployment.BucketDeployment(
            self,
            "DeployFrontend",
            sources=[s3_deployment.Source.asset(str(frontend_dist_path))],
            destination_bucket=bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        return distribution
