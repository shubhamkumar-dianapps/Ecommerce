# Ecommerce Backend - API Quick Reference

## Authentication

### Register User
```
POST /api/accounts/register/
{
  "email": "user@example.com",
  "phone": "9876543210",
  "role": "CUSTOMER",  // or "SHOPKEEPER", "ADMIN"
  "password": "password123",
  "full_name": "John Doe"  // for customer
}
```

### Login
```
POST /api/accounts/login/
{
  "email": "user@example.com",
  "password": "password123"
}
Response: { "access": "...", "refresh": "...", "user": {...} }
```

### Get/Update Profile
```
GET /api/accounts/profile/
PUT /api/accounts/profile/
```

## Addresses
```
GET    /api/addresses/          # List all user addresses
POST   /api/addresses/          # Create new address
GET    /api/addresses/{id}/     # Get specific address
PUT    /api/addresses/{id}/     # Update address
DELETE /api/addresses/{id}/     # Delete address
```

## Products
```
GET /api/categories/             # List categories
GET /api/categories/{slug}/      # Get category details
GET /api/brands/                 # List brands
GET /api/products/               # List products (with filters)
GET /api/products/{slug}/        # Get product details

# Filters:
?category=1&brand=2&is_featured=true
?search=laptop
?ordering=-created_at
```

## Cart
```
GET  /api/cart/                  # Get cart
POST /api/cart/add_item/         # Add to cart
     { "product_id": 1, "quantity": 2 }
POST /api/cart/update_item/      # Update quantity
     { "item_id": 1, "quantity": 3 }
POST /api/cart/remove_item/      # Remove from cart
     { "item_id": 1 }
POST /api/cart/clear/            # Clear cart
```

## Orders
```
GET  /api/orders/                # List user orders
GET  /api/orders/{id}/           # Get order details  
POST /api/orders/checkout/       # Create order from cart
     {
       "shipping_address_id": 1,
       "billing_address_id": 1,
       "customer_notes": "..."
     }
POST /api/orders/{id}/cancel/    # Cancel order
```

## Reviews
```
GET    /api/reviews/             # List all reviews
       ?product_id=1             # Filter by product
POST   /api/reviews/             # Create review
       {
         "product": 1,
         "rating": 5,
         "title": "Great!",
         "comment": "..."
       }
PUT    /api/reviews/{id}/        # Update own review
DELETE /api/reviews/{id}/        # Delete own review
```

## Admin Portal
Access at: `http://localhost:8000/admin/`
All models registered with appropriate inlines and filters.
