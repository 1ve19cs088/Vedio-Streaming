Sure! Here’s a **complete guide** to get started with your **Mini YouTube** project, covering the frontend, backend (Lambda functions), and deployment instructions. This will help you set up everything from scratch, including the **AWS Lambda functions**, **API Gateway**, **S3 bucket**, and the **frontend**.

### **Step-by-Step Guide**

---

### **1. AWS Setup (Backend)**

#### **A. Create S3 Bucket for Video Storage**

1. **Go to the S3 Console**:
   - Navigate to **Amazon S3** in the AWS Console.
   - Click on **Create bucket**.
   - Set the **Bucket name** (e.g., `my-mini-youtube-bucket`).
   - Choose a **region** and **leave the default settings**.
   - Click on **Create bucket**.

2. **Set Permissions**:
   - Ensure your Lambda functions have the appropriate permissions to interact with S3.
   - Create an IAM role with `s3:PutObject` and `s3:GetObject` permissions for your Lambda functions.

---

#### **B. Create the Lambda Functions**

1. **First Lambda Function: Upload Video**
   - Go to **AWS Lambda**.
   - Click on **Create function**.
   - Choose **Author from scratch**.
   - Name it `uploadVideoFunction`.
   - Select **Node.js 14.x** as the runtime.
   - Set the IAM role permissions as `Lambda Execution Role` with access to S3 (`s3:PutObject`).

2. **Lambda Code for Upload (uploadVideoFunction)**

   Copy and paste the following code into your Lambda function:

```python
import boto3
import re

s3 = boto3.client('s3')

# Lambda function to validate and upload .mp4 file
def lambda_handler(event, context):
    # Assuming the event contains the file details in a JSON format
    file_name = event['file_name']
    file_content = event['file_content']
    bucket_name = 'your-s3-bucket-name'  # Replace with your bucket name
    
    # Validate the file extension
    if not re.match(r'.*\.mp4$', file_name):
        return {
            'statusCode': 400,
            'body': 'Invalid file type. Only .mp4 files are allowed.'
        }
    
    # Upload the file to S3
    try:
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)
        return {
            'statusCode': 200,
            'body': f'File {file_name} uploaded successfully.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error uploading file: {str(e)}'
        }
```

3. **Second Lambda Function: Retrieve Video List**

   This function will list all uploaded videos.

```python
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = 'your-s3-bucket-name'  # Replace with your bucket name
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        video_files = []
        for obj in response.get('Contents', []):
            video_files.append({"fileName": obj['Key']})

        return {
            'statusCode': 200,
            'body': video_files
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error fetching video list: {str(e)}'
        }
```

4. **Third Lambda Function: Retrieve Video by Name**

   This function retrieves a specific video based on the file name.

```python
import boto3

s3 = boto3.client('s3')

def lambda_handler(event, context):
    file_name = event['file_name']
    bucket_name = 'your-s3-bucket-name'  # Replace with your bucket name
    
    try:
        # Retrieve the .mp4 file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        
        # Return the file content as a response
        file_content = response['Body'].read()
        return {
            'statusCode': 200,
            'body': file_content,
            'headers': {
                'Content-Type': 'video/mp4',
                'Content-Disposition': f'attachment; filename={file_name}'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error retrieving file: {str(e)}'
        }
```

---

### **2. Set Up API Gateway**

1. **Create a REST API** in **API Gateway**.
2. **Create Endpoints**:
   - **POST `/upload`**: Trigger `uploadVideoFunction` Lambda function.
   - **GET `/videos`**: Trigger `retrieveVideosListFunction` Lambda function.
   - **GET `/video/{fileName}`**: Trigger `retrieveVideoFunction` Lambda function.

3. **Enable CORS** for each endpoint to allow frontend communication.

4. **Deploy API** to a stage (e.g., `prod`) and get the **API Gateway URL**.

---

### **3. Frontend Code (HTML, CSS, JS)**

1. **Create the `index.html` File**:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mini YouTube</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; font-family: 'Arial', sans-serif; }
        .container { margin-top: 50px; }
        .video-card { margin-bottom: 20px; }
        .video-card img { width: 100%; height: 300px; object-fit: cover; }
        .video-card .card-body { background-color: #fff; padding: 15px; border-radius: 5px; }
        .video-title { font-size: 18px; font-weight: 600; color: #333; }
        .video-player { max-width: 100%; height: auto; border-radius: 10px; }
        .alert-custom { border-radius: 5px; margin-bottom: 20px; }
        .upload-btn { background-color: #007bff; color: white; border: none; }
        .upload-btn:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <div class="text-center mb-5">
            <h1>Welcome to Mini YouTube</h1>
            <p class="lead text-muted">Upload and watch your favorite videos</p>
        </div>

        <div id="alertPlaceholder"></div>

        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow-lg">
                    <div class="card-body">
                        <h3 class="card-title text-center">Upload Your Video</h3>
                        <form id="uploadForm">
                            <div class="mb-3">
                                <input type="file" class="form-control" id="fileInput" accept=".mp4" />
                            </div>
                            <button type="submit" class="btn upload-btn btn-block w-100">Upload Video</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <hr class="my-5">
        
        <h2 class="text-center mb-4">Uploaded Videos</h2>

        <div id="videoList" class="row row-cols-1 row-cols-md-3 g-4">
            <!-- Dynamic video cards will be inserted here -->
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <script>
        const apiUrl = "YOUR_API_GATEWAY_URL"; // Replace with your API Gateway URL

        function showAlert(message, isSuccess) {
            const alertPlaceholder = document.getElementById('alertPlaceholder');
            const alertDiv = document.createElement('div');
            alertDiv.classList.add('alert', isSuccess ? 'alert-success' : 'alert-danger', 'alert-custom');
            alertDiv.textContent = message;
            alertPlaceholder.appendChild(alertDiv);
            setTimeout(() => alertDiv.remove(), 3000);
        }

        document.getElementById("uploadForm").addEventListener("submit", async (event) => {
            event.preventDefault();
            const fileInput = document.getElementById("fileInput");
            const file = fileInput.files[0];

            if (!file || file.type !== "video/mp4") {
                showAlert("Please upload a valid .mp4 file.", false);
                return;
            }

            const formData = new FormData();
            formData.append("file", file);

            try {
                const response = await axios.post(`${apiUrl}/upload`, formData, {
                    headers: {
                        "Content-Type": "multipart/form-data"
                    }
                });
                showAlert(response.data.body, true);
                loadVideos();
            } catch (error) {
                showAlert("Error uploading file.", false);
            }
        });



        async function loadVideos() {
            try {
                const response = await axios.get(`${apiUrl}/videos`);
                const videoListDiv = document.getElementById("videoList");
                videoListDiv.innerHTML = "";

                if (response.data.length > 0) {
                    response.data.forEach((video) => {
                        const videoCard = document.createElement("div");
                        videoCard.classList.add("col");
                        videoCard.innerHTML = `
                            <div class="card video-card shadow-lg">
                                <video class="video-player" controls>
                                    <source src="${apiUrl}/video/${video.fileName}" type="video/mp4">
                                    Your browser does not support the video tag.
                                </video>
                                <div class="card-body">
                                    <h5 class="video-title">${video.fileName}</h5>
                                </div>
                            </div>
                        `;
                        videoListDiv.appendChild(videoCard);
                    });
                } else {
                    videoListDiv.innerHTML = "<p class='text-center w-100'>No videos uploaded yet.</p>";
                }
            } catch (error) {
                console.error("Error loading videos:", error);
            }
        }

        loadVideos();
    </script>
</body>
</html>
```

---

### **4. Deploy the Application**

1. **Deploy Lambda Functions**: In the Lambda console, deploy your functions after setting the necessary permissions.
2. **Configure API Gateway**: Use the **API Gateway** to deploy your REST API. Use the **GET** and **POST** methods to connect your Lambda functions.
3. **Connect Frontend to API**: Replace `YOUR_API_GATEWAY_URL` in the frontend code with the API Gateway URL you get after deploying the API.

---

### **Final Steps**:
- Test your application by uploading a video and viewing it through the frontend interface.
- Make any adjustments to the design, video formats, or backend as necessary.

Now you have a working mini YouTube application!