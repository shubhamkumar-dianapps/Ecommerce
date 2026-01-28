# """
# Quick script to reset database and create fresh data.

# This will:
# 1. Delete the database
# 2. Run migrations
# 3. Create superuser
# 4. Create test users
# """

# import os
# import sys
# import django

# # Setup Django
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
# django.setup()

# from django.core.management import call_command
# from apps.accounts.models import User


# def reset_database():
#     """Reset database and create fresh data"""

#     print("\n[*] Starting database reset...")

#     # Delete database
#     db_path = "db.sqlite3"
#     if os.path.exists(db_path):
#         os.remove(db_path)
#         print("[+] Deleted old database")

#     # Run migrations
#     print("\n[*] Running migrations...")
#     call_command("migrate", "--noinput")
#     print("[+] Migrations complete")

#     # Create superuser
#     print("\n[*] Creating superuser...")
#     admin = User.objects.create_superuser(
#         email="admin@example.com",
#         phone="+919876543210",
#         role="ADMIN",
#         password="Admin@123",
#     )
#     admin.email_verified = True
#     admin.save()
#     print(f"[+] Superuser created: {admin.email}")

#     # Create test customer
#     print("\n[*] Creating test customer...")
#     customer = User.objects.create_user(
#         email="customer@example.com",
#         phone="+919876543211",
#         role="CUSTOMER",
#         password="Customer@123",
#     )
#     customer.customerprofile.full_name = "Test Customer"
#     customer.customerprofile.save()
#     customer.email_verified = True
#     customer.save()
#     print(f"[+] Customer created: {customer.email}")

#     # Create test shopkeeper
#     print("\n[*] Creating test shopkeeper...")
#     shopkeeper = User.objects.create_user(
#         email="shop@example.com",
#         phone="+919876543212",
#         role="SHOPKEEPER",
#         password="Shop@123",
#     )
#     shopkeeper.shopkeeperprofile.shop_name = "Test Shop"
#     shopkeeper.shopkeeperprofile.gst_number = "22AAAAA0000A1Z5"
#     shopkeeper.shopkeeperprofile.is_verified = True
#     shopkeeper.shopkeeperprofile.save()
#     shopkeeper.email_verified = True
#     shopkeeper.save()
#     print(f"[+] Shopkeeper created: {shopkeeper.email}")

#     print("\n" + "=" * 60)
#     print("[SUCCESS] Database reset complete!")
#     print("=" * 60)
#     print("\nTest Credentials:\n")
#     print("  Admin:")
#     print("     Email: admin@example.com")
#     print("     Password: Admin@123")
#     print("     URL: http://localhost:8000/admin/\n")
#     print("  Customer:")
#     print("     Email: customer@example.com")
#     print("     Password: Customer@123\n")
#     print("  Shopkeeper:")
#     print("     Email: shop@example.com")
#     print("     Password: Shop@123\n")
#     print("=" * 60)
#     print("\nYou can now run: python manage.py runserver")


# if __name__ == "__main__":
#     try:
#         reset_database()
#     except Exception as e:
#         print(f"\n[ERROR] {e}")
#         import traceback

#         traceback.print_exc()
#         sys.exit(1)
