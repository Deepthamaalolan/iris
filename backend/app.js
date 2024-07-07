require('dotenv').config();
const express = require('express');
const multer = require('multer');
const AWS = require('aws-sdk');
const fs = require('fs');
const path = require('path');

// Configure AWS with your access and secret key.
AWS.config.update({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: process.env.AWS_REGION
});

// Create S3 and SQS service objects
const s3 = new AWS.S3();
const sqs = new AWS.SQS();

const app = express();
const port = 3000;

// Configure multer for file upload
const upload = multer({ dest: 'uploads/' });

const uploadVideoToS3AndPushToSQS = async (filePath, fileName, additionalParams) => {
  try {
    const fileContent = fs.readFileSync(filePath);

    // Uploading files to the bucket
    const uploadParams = {
      Bucket: process.env.S3_BUCKET_NAME,
      Key: fileName, // File name you want to save as in S3
      Body: fileContent,
      ContentType: 'video/mp4' // Change accordingly based on your video type
    };

    const uploadResult = await s3.upload(uploadParams).promise();

    console.log("uploadResult", uploadResult)

    // Construct the message to send to SQS
    const messageBody = {
      s3Url: uploadResult.Location,
      ...additionalParams // Spread any additional parameters here
    };

    const sqsParams = {
      QueueUrl: process.env.SQS_QUEUE_URL,
      MessageBody: JSON.stringify(messageBody),
    };

    await sqs.sendMessage(sqsParams).promise();

    console.log(`Successfully uploaded ${fileName} to ${uploadResult.Location} and sent to SQS`);

  } catch (error) {
    console.error('Error uploading video or sending to SQS', error);
    throw error;
  }
};

// API endpoint to accept video upload
app.post('/upload', upload.single('video'), async (req, res) => {
  try {
    const filePath = req.file.path;
    const fileName = req.file.originalname;
    const additionalParams = {
      title: req.body.title || 'Default Title',
      description: req.body.description || 'Default Description'
    }; // Additional parameters to send to SQS

    await uploadVideoToS3AndPushToSQS(filePath, fileName, additionalParams);

    // Delete the file from local storage after upload
    fs.unlinkSync(filePath);

    res.status(200).send({ message: 'Video uploaded and message sent to SQS successfully.' });
  } catch (error) {
    res.status(500).send({ error: 'Error uploading video or sending to SQS' });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
