from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_bedrock as bedrock,
    aws_opensearchserverless as opensearchserverless,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    SecretValue
)
from constructs import Construct

import hashlib
import os

class MyDemoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        EMBEDDING_MODEL_ARN="arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
        # Create an S3 bucket
        self.bucket = s3.Bucket(self, 
            "ck-demo-s3",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )
        
        self.secret = secretsmanager.Secret(self, "Secret",
            secret_object_value={
                "apiKey": SecretValue.unsafe_plain_text(os.getenv('apikey'))
            }
        )

        
        # Create a bedrock knowledgebase role.
        bedrock_kb_role = iam.Role(self, 'bedrock-kb-role',
            role_name = f"bedrock-kb-role-{hashlib.sha256('CloudKinetics'.encode()).hexdigest()[:15]}".lower(),
            assumed_by=iam.ServicePrincipal('bedrock.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonBedrockFullAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonOpenSearchServiceFullAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'),
                iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsFullAccess'),
            ],
        )
        
        # Add inline permissions to the bedrock knowledgebase execution role      
        bedrock_kb_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "aoss:APIAccessAll",
                    "es:ESHttpPut", 
                    "iam:CreateServiceLinkedRole", 
                    "iam:PassRole", 
                    "iam:ListUsers",
                    "iam:ListRoles", 
                    "secretsmanager:GetSecretValue"
                    ],
                resources=["*"],
            )
        )
        
        # create knowledge base
        self.kb = bedrock.CfnKnowledgeBase(
            self, 
            id="ck-demo-kb",
            ## name required
            name="ck-demo-kb",
            ## role_arn required
            role_arn=bedrock_kb_role.role_arn,
            ## KnowledgeBaseConfiguration required
            knowledge_base_configuration=bedrock.CfnKnowledgeBase.KnowledgeBaseConfigurationProperty(
                type="VECTOR",
                vector_knowledge_base_configuration=bedrock.CfnKnowledgeBase.VectorKnowledgeBaseConfigurationProperty(
                    embedding_model_arn=EMBEDDING_MODEL_ARN,

                    ## the properties below are optional
                    embedding_model_configuration=bedrock.CfnKnowledgeBase.EmbeddingModelConfigurationProperty(
                        bedrock_embedding_model_configuration=bedrock.CfnKnowledgeBase.BedrockEmbeddingModelConfigurationProperty(
                            dimensions=512
                        )
                    )
                )
            ),
            ## StorageConfiguration required
            storage_configuration=bedrock.CfnKnowledgeBase.StorageConfigurationProperty(
                type="PINECONE",
                
                pinecone_configuration=bedrock.CfnKnowledgeBase.PineconeConfigurationProperty(
                    connection_string="https://test-pn0ffam.svc.aped-4627-b74a.pinecone.io",
                    credentials_secret_arn=self.secret.secret_arn,
                    field_mapping=bedrock.CfnKnowledgeBase.PineconeFieldMappingProperty(
                        metadata_field="metadataField",
                        text_field="textField"
                    ),

                    # the properties below are optional
                    namespace="CK"
                    ),
                )
        )
        
        # create KB datasource
        self.dataSource = bedrock.CfnDataSource(
            self,
            "CKDemoDataSource",
            data_source_configuration=bedrock.CfnDataSource.DataSourceConfigurationProperty(
                s3_configuration=bedrock.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_arn=self.bucket.bucket_arn,
                ),
                type="S3"
            ),
            
            knowledge_base_id=self.kb.attr_knowledge_base_id,
            name="ck-demo-datasource",
            data_deletion_policy="RETAIN"
            )