# Script to help verify phone and test OTP sending

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Twilio OTP Phone Verification & Test" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Get phone number from user
$phoneNumber = Read-Host "Enter your phone number (with country code, e.g., +919876543210)"

Write-Host ""
Write-Host "IMPORTANT: Twilio Trial Account Limitations" -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Yellow
Write-Host "Trial accounts can ONLY send SMS to verified phone numbers." -ForegroundColor Yellow
Write-Host ""
Write-Host "To verify your phone number:" -ForegroundColor White
Write-Host "1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified" -ForegroundColor White
Write-Host "2. Click 'Add a new number'" -ForegroundColor White
Write-Host "3. Enter your phone number: $phoneNumber" -ForegroundColor White
Write-Host "4. You'll receive a verification code via SMS" -ForegroundColor White
Write-Host "5. Enter the code to verify your number" -ForegroundColor White
Write-Host ""

$verified = Read-Host "Have you verified this number in Twilio Console? (yes/no)"

if ($verified -ne "yes") {
    Write-Host ""
    Write-Host "Please verify your number first, then run this script again." -ForegroundColor Red
    Write-Host ""
    Write-Host "Opening Twilio Console in your browser..." -ForegroundColor Cyan
    Start-Process "https://console.twilio.com/us1/develop/phone-numbers/manage/verified"
    exit
}

Write-Host ""
Write-Host "Testing OTP sending to $phoneNumber..." -ForegroundColor Cyan
Write-Host ""

# Test sending OTP
cd backend
python test_twilio_otp.py $phoneNumber

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Check your phone for the OTP SMS!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "If you didn't receive the SMS:" -ForegroundColor Yellow
Write-Host "1. Check Twilio logs: https://console.twilio.com/us1/monitor/logs/sms" -ForegroundColor White
Write-Host "2. Verify phone number format is correct (E.164 format)" -ForegroundColor White
Write-Host "3. Ensure the number is verified in Twilio Console" -ForegroundColor White
Write-Host "4. Check if your phone can receive SMS from international numbers" -ForegroundColor White
Write-Host ""
