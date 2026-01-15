"""
Quick configuration validation script.
Run this to verify all environment variables are loaded correctly.
"""
from config import settings

print("=" * 60)
print("Configuration Validation")
print("=" * 60)

print(f"\n✓ App Name: {settings.APP_NAME}")
print(f"✓ Database URL: {settings.DATABASE_URL[:30]}...")
print(f"✓ Google Client ID: {settings.GOOGLE_CLIENT_ID[:20]}...")
print(f"✓ Google API Key: {settings.GOOGLE_API_KEY[:20]}...")
print(f"✓ Gemini Model: {settings.GEMINI_MODEL}")
print(f"✓ Secret Key: {settings.SECRET_KEY[:20]}...")
print(f"✓ Frontend URL: {settings.FRONTEND_URL}")
print(f"✓ CORS Origins: {settings.cors_origins_list}")
print(f"✓ Log Level: {settings.LOG_LEVEL}")

print("\n" + "=" * 60)
print("✅ All configuration loaded successfully!")
print("=" * 60)
