# Flask test app
This is a test flask app ready to be deployed as an Azure web app (via an docker image).
After log-in an image of a digit is displayed to the user. The user may submit a label for the image and the label is stored in an Azure SQL database. The images are stored in Azure blob storage. To allow monitoring consistency/reproducibility of labeling, there is a 20% chance that the user will be served with an image which he has already labeled previously.

Furthermore, a user statistic is presented to the user that contains information on how many labels he has already provided, how many distinct images he has labeled, and how many images are still awaiting labeling. Inactive users of the app will be signed out after 120 seconds.

# Deploy to Azure

- Create blob storage:
    - In Azure, go to the "Storage account" service. Create your storage account and ensure that the "Enable blob public access" option is unchecked, so that your data remains private.
    - Create a folder "credentials" in this repository and create a file "blob_storage.py" that holds the string variable "storage_account_name" with the name of the storage account you just created. This is ommited in this repository for obvious reasons.
    - Within your storage account, create a container ("Data Storage -> Containers -> Create") and add a string variable "container_name" to your "./credentials/blob_storage.py" file that holds your container name.
    - Under "Security + networking -> Shared access signature" choose appropiate option and click "Generate SAS and connection string". Copy the SAS token and store it in string variable "sas_tocken" to your "./credentials/blob_storage.py" file.
    - Under "Security + networking -> Access keys" get your connection string and store it in string variable "connection_string_blob" to your "./credentials/blob_storage.py" file.

- Create database in Azure:
    - In Azure, go to the "SQL databases" service and create a SQL database- In your "credentials" folder, create a "database.py" file that holds corresponding string variables for "server", "database", "username", and "password". 
    - Run the file "manage_azure_database_and_blob_storage.py" to:
        - Initialize the users, images and labels table. To the user, table an user "guest"1 with password "123456" is initialized, the other two tables remain empy for now.
        - Download digit images, save them as jpg file in the folder "./images" and push them to the blob storage.
        - Add entries in the "images" table that hold the urls for the images in the blob storage.
    - In the "Overview" view, select "Set server firewall" and under "Exceptions" select option "Allow Azure services and resources to access this server".

- Secret key:
    - In your "credentials" folder, create a "application.py" file that holds a string variable "secret_key" with your secret key.

- Create docker image and push in to the Azure container registry:
    - In Azure, go to the "Container registries" and create one.
    - Start Docker Desktop.
    - Install the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli).
    - In Azure, go to the "Container registries" service and create a registry.
    - In your Azure container registry, make sure to enable "Admin user" in the "Update" tab.
    - In a command terminal, go to your repository folder and run following commands:

```
        docker run -dit alpine sh
        docker image build -t docker-app .
        az login
        az acr login --name YOURLOGINSERVER.azurecr.io
        docker tag docker-app YOURLOGINSERVER.azurecr.io/testapp         
        docker push YOURLOGINSERVER.azurecr.io/testapp
```  


- Deploy app:
    - In Azure, go to the "App Services" service and create the app service by selecting your docker image from the Azure container registry.
