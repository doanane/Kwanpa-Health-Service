# clean_secrets.ps1 - Remove all secrets from Git history

Write-Host "🚨 CRITICAL SECURITY ALERT!" -ForegroundColor Red
Write-Host "You have exposed multiple API keys in your repository." -ForegroundColor Yellow
Write-Host "`nStep 1: BACKUP YOUR .env FILE" -ForegroundColor Cyan
Copy-Item .env .env.backup -Force

Write-Host "`nStep 2: Creating clean template..." -ForegroundColor Cyan
@"
# Database
DATABASE_URL=postgresql://user:password@server.postgres.database.azure.com:5432/dbname?sslmode=require

# Azure Custom Vision
AZURE_CUSTOM_VISION_PREDICTION_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/customvision/v3.0/Prediction/...
AZURE_CUSTOM_VISION_PREDICTION_KEY=your_prediction_key_here

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your_openai_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-5-chat
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# JWT Secret - generate with: openssl rand -hex 32
SECRET_KEY=generate_a_random_secret_key_here

# Add other variables WITHOUT real values
"@ | Out-File -FilePath example.env -Encoding UTF8

Write-Host "✅ Created example.env template" -ForegroundColor Green

Write-Host "`nStep 3: Removing .env from Git..." -ForegroundColor Cyan
git rm --cached .env
Add-Content .gitignore "`n.env`n.env.local`n*.env.*`n"

Write-Host "`nStep 4: Fixing ai_food_analysis.py..." -ForegroundColor Cyan
$content = Get-Content "app\utils\ai_food_analysis.py" -Raw
$content = $content -replace 'PREDICTION_KEY =os\.getenv\("AZURE_CUSTOM_VISION_PREDICTION_KEY"\)', 'PREDICTION_KEY = os.getenv("AZURE_CUSTOM_VISION_PREDICTION_KEY", "")'
$content = $content -replace 'PREDICTION_ENDPOINT = os\.getenv\("AZURE_CUSTOM_VISION_PREDICTION_ENDPOINT"\)', 'PREDICTION_ENDPOINT = os.getenv("AZURE_CUSTOM_VISION_PREDICTION_ENDPOINT", "")'
Set-Content "app\utils\ai_food_analysis.py" $content

Write-Host "`nStep 5: Committing changes..." -ForegroundColor Cyan
git add .gitignore example.env app/utils/ai_food_analysis.py
git commit -m "security: Remove all secrets from repository

- Remove .env file from git tracking
- Add .env to .gitignore
- Create example.env template
- Fix environment variable loading in ai_food_analysis.py
- All API keys must now be set as environment variables"

Write-Host "`n🚨 IMPORTANT NEXT STEPS:" -ForegroundColor Red
Write-Host "1. ROTATE ALL EXPOSED KEYS IMMEDIATELY:" -ForegroundColor Yellow
Write-Host "   - Azure Custom Vision" -ForegroundColor White
Write-Host "   - Azure OpenAI" -ForegroundColor White
Write-Host "   - SendGrid" -ForegroundColor White
Write-Host "   - Gemini" -ForegroundColor White
Write-Host "   - Azure Storage" -ForegroundColor White
Write-Host "   - Database passwords" -ForegroundColor White
Write-Host "`n2. Update Azure App Service with new environment variables" -ForegroundColor Yellow
Write-Host "`n3. Push with force (after key rotation):" -ForegroundColor Cyan
Write-Host "   git push origin dev --force" -ForegroundColor White