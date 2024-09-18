from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_bedrock as bedrock,
    aws_opensearchserverless as opensearchserverless,
    aws_iam as iam
)
from constructs import Construct

import hashlib

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
        
        
        # Create Opensearch Serverless Collection
        self.cfn_collection = opensearchserverless.CfnCollection(
            self,
            "ChatBotAgentCollection",
            name="ck-demo-collection",
            description="ChatBot Collection",
            type="VECTORSEARCH",
        )
        
        opensearch_serverless_encryption_policy = opensearchserverless.CfnSecurityPolicy(self, "OpenSearchServerlessEncryptionPolicy",
            name="encryption-policy",
            policy="{\"Rules\":[{\"ResourceType\":\"collection\",\"Resource\":[\"collection/*\"]}],\"AWSOwnedKey\":true}",
            type="encryption",
            description="the encryption policy for the opensearch serverless collection"
        )
        
        opensearch_serverless_network_policy = opensearchserverless.CfnSecurityPolicy(self, "OpenSearchServerlessNetworkPolicy",
            name="network-policy",
            policy="[{\"Description\":\"Public access for collection\",\"Rules\":[{\"ResourceType\":\"dashboard\",\"Resource\":[\"collection/*\"]},{\"ResourceType\":\"collection\",\"Resource\":[\"collection/*\"]}],\"AllowFromPublic\":true}]",
            type="network",
            description="the network policy for the opensearch serverless collection"
        )
        
        self.cfn_collection.add_dependency(opensearch_serverless_encryption_policy)
        self.cfn_collection.add_dependency(opensearch_serverless_network_policy)
        
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
                type="OPENSEARCH_SERVERLESS",
                
                opensearch_serverless_configuration = bedrock.CfnKnowledgeBase.OpenSearchServerlessConfigurationProperty(
                    collection_arn=self.cfn_collection.attr_arn,
                    field_mapping=bedrock.CfnKnowledgeBase.OpenSearchServerlessFieldMappingProperty(
                        metadata_field="AMAZON_BEDROCK_METADATA",
                        text_field="AMAZON_BEDROCK_TEXT_CHUNK",
                        # To Do !!
                        vector_field="bedrock-knowledge-base-default-vector"
                    ),
                    # To Do !!
                    vector_index_name="bedrock-knowledgebase-index"
                )
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