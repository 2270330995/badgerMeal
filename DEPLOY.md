# Deploying Badger Meal to Google Cloud Run

This guide will walk you through deploying your Badger Meal application to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account**: You already have this set up with project ID `praxis-practice-477200-s7`
2. **gcloud CLI**: Install the Google Cloud SDK
   - Download from: https://cloud.google.com/sdk/docs/install
   - Or use Cloud Shell directly in the Google Cloud Console

3. **Google Gemini API Key**: You'll need this for the application to work

## Step-by-Step Deployment

### 1. Install and Configure gcloud CLI

```bash
# Install gcloud (if not already installed)
# Follow instructions at: https://cloud.google.com/sdk/docs/install

# Login to Google Cloud
gcloud auth login

# Set your project ID
gcloud config set project praxis-practice-477200-s7

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Set Your Region

Choose a region close to your users. For Wisconsin, `us-central1` is recommended:

```bash
gcloud config set run/region us-central1
```

### 3. Build and Deploy to Cloud Run

From your project directory, run:

```bash
# Build the container and deploy in one command
gcloud run deploy badger-meal \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_actual_api_key_here
```

**Important**: Replace `your_actual_api_key_here` with your actual Google Gemini API key.

### 4. Set Environment Variables Securely (Recommended)

Instead of putting your API key in the command line, you can set it after deployment:

```bash
# First deploy without the API key
gcloud run deploy badger-meal \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Then update with your API key
gcloud run services update badger-meal \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=your_actual_api_key_here
```

### 5. Access Your Application

After deployment completes, you'll see output like:

```
Service [badger-meal] revision [badger-meal-00001] has been deployed and is serving 100 percent of traffic.
Service URL: https://badger-meal-xxxxx-uc.a.run.app
```

Visit that URL to see your deployed application!

## Using Cloud Shell (No Local Installation Required)

If you don't want to install gcloud locally, you can use Google Cloud Shell:

1. Go to your Google Cloud Console: https://console.cloud.google.com
2. Click the "Activate Cloud Shell" button (terminal icon in top right)
3. Clone your repository or upload your code
4. Run the deployment commands from there

## Configuration Options

### Adjusting Resources

If your app needs more memory or CPU:

```bash
gcloud run deploy badger-meal \
  --source . \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --region us-central1
```

### Setting Minimum Instances

To avoid cold starts, keep at least one instance running:

```bash
gcloud run deploy badger-meal \
  --source . \
  --min-instances 1 \
  --region us-central1
```

**Note**: This will increase costs as the instance runs continuously.

## Updating Your Deployment

To deploy updates after making changes to your code:

```bash
gcloud run deploy badger-meal \
  --source . \
  --region us-central1
```

## Viewing Logs

To view application logs:

```bash
gcloud run services logs read badger-meal --region us-central1
```

Or view logs in the Cloud Console:
1. Go to Cloud Run in the Console
2. Click on your service
3. Click the "LOGS" tab

## Cost Estimation

Cloud Run pricing is based on:
- **Requests**: $0.40 per million requests
- **Compute time**: ~$0.00002400 per vCPU-second
- **Memory**: ~$0.00000250 per GiB-second
- **Free tier**: 2 million requests per month, 360,000 GiB-seconds

For a student project with moderate usage, costs should be minimal (often within free tier).

## Troubleshooting

### Build Fails

If the build fails, check the error messages. Common issues:
- Missing dependencies in `requirements.txt`
- Dockerfile syntax errors
- Permission issues

### Application Won't Start

Check logs:
```bash
gcloud run services logs read badger-meal --region us-central1 --limit 50
```

Common issues:
- Missing `GEMINI_API_KEY` environment variable
- Port binding issues (Cloud Run sets PORT automatically)

### 403 Errors

If you get permission errors:
```bash
# Make sure you're authenticated
gcloud auth login

# Ensure you have the right permissions on the project
gcloud projects get-iam-policy praxis-practice-477200-s7
```

## Security Best Practices

1. **API Keys**: Use Secret Manager for production:
   ```bash
   # Create secret
   echo -n "your-api-key" | gcloud secrets create gemini-api-key --data-file=-

   # Deploy with secret
   gcloud run deploy badger-meal \
     --source . \
     --set-secrets=GEMINI_API_KEY=gemini-api-key:latest
   ```

2. **Authentication**: For a production app, consider adding authentication:
   ```bash
   gcloud run deploy badger-meal --source . --no-allow-unauthenticated
   ```

## Custom Domain (Optional)

To use a custom domain:

1. Go to Cloud Run in Console
2. Select your service
3. Click "MANAGE CUSTOM DOMAINS"
4. Follow the instructions to map your domain

## Alternative: Using Docker Locally First

To test the Docker container locally before deploying:

```bash
# Build the image
docker build -t badger-meal .

# Run locally
docker run -p 8080:8080 -e PORT=8080 -e GEMINI_API_KEY=your_key badger-meal

# Visit http://localhost:8080
```

## Next Steps

After deployment:
- Monitor your app's performance in Cloud Console
- Set up alerting for errors
- Consider adding Cloud CDN for faster global access
- Implement Cloud Armor for DDoS protection if needed

## Support

For issues:
- Cloud Run Documentation: https://cloud.google.com/run/docs
- Stack Overflow: Tag with `google-cloud-run`
- Google Cloud Support: https://cloud.google.com/support
