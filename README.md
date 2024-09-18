# Clone Repository
```sh
git clone https://github.com/heyyytamvo/CK-Assignment.git
```
# Set up the Indexes in PineCone 

Set up the Storage for the Model, I will use service from PineCone to avoid charging.

![image](/images/10.png)

# Export Environment Variables
```sh
export AWS_ACCESS_KEY_ID=<your-access-key> \
export AWS_SECRET_ACCESS_KEY=<your-secret> \
export AWS_DEFAULT_REGION=<your-region> \
export apikey=<your-api-key>
```

# Activate Python Environment
```sh
cd CK-Assignment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Provision the Infrastructure
```sh
cdk bootstrap
```

## Provision S3 Bucket and Bedrock Role

In file `work/ck_stack.py`, comment lines **63-117**, then:

```sh
cdk deploy
```

Then, we will get the deployment of **S3** and **BedRockRole** as below:

![image](/images/01.png)

## Provision Knowledge Base and Data Source
Next, uncomment lines **63-117** `work/ck_stack.py`, then executing the command below:

```sh
cdk diff
```
We will find out 2 resources are ready to be deployed.

![image](/images/02.png)

Deploy the infrastructure, we will see the successful result.

![image](/images/03.png)

Now, move to the Console Management to check the **Knowledge Base** as the picture below:

![image](/images/04.png)

and the **Data Source** as Figure below:

![image](/images/05.png)

We are going to upload the CSV file to the S3 Bucket. The file `knownledgebase.csv` will be used for testing purposes.

![image](/images/06.png)

Next, sync the **Data Source**

![image](/images/07.png)

# Test the Model by Q&A
## Question 1
![image](/images/08.png)
## Question 2
![image](/images/09.png)