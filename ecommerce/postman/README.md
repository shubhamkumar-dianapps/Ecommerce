# Ecommerce API Postman Collection

Comprehensive API collection for testing all endpoints with edge cases.

## 📁 Files

| File | Description |
|------|-------------|
| `Ecommerce_API_Part1.json` | Health, Authentication, Addresses |
| `Ecommerce_API_Part2.json` | Categories, Brands, Products, Cart |
| `Ecommerce_API_Part3.json` | Orders, Returns, Reviews, Edge Cases |

## 🚀 Quick Start

1. **Import Collections**: Import all 3 JSON files into Postman
2. **Set Environment Variables**: The collections use these variables:
   - `baseUrl`: `http://localhost:8000/api/v1`
   - `accessToken`: Auto-set after login
   - `refreshToken`: Auto-set after login

3. **Run in Order**:
   - Register a customer
   - Login to get tokens
   - Run other endpoints

## 📋 Endpoints Covered

### 🔐 Authentication (18 requests)
- Customer/Shopkeeper Registration
- Login/Token Refresh
- Profile CRUD
- Email Verification
- Session Management

### 📍 Addresses (13 requests)
- CRUD Operations
- Filtering by type/city
- Set Default Address

### 📦 Products (16 requests)
- List/Search/Filter Products
- Category/Brand browsing
- Shopkeeper product management

### 🛒 Cart (16 requests)
- Add/Update/Remove Items
- Stock validation
- Clear cart

### 📦 Orders (17 requests)
- Checkout flow
- Order cancellation
- Return requests

### ⭐ Reviews (18 requests)
- CRUD Operations
- Like/Reply
- Filtering/Search

### 🔒 Security Tests (6 requests)
- Rate limiting
- Authorization checks
- Token validation

## 🧪 Edge Cases Tested

Each section includes edge case tests marked with "EDGE CASE:" description:

- ❌ Invalid credentials
- ❌ Missing required fields
- ❌ Unauthorized access
- ❌ Resource not found (404)
- ❌ Rate limit exceeded (429)
- ❌ Stock validation failures
- ❌ Permission denied (403)
- ❌ Duplicate entries
- ❌ Invalid data formats

## 🔧 Collection Variables

| Variable | Description | Auto-Set |
|----------|-------------|----------|
| `baseUrl` | API base URL | No |
| `accessToken` | JWT access token | ✅ On login |
| `refreshToken` | JWT refresh token | ✅ On login |
| `customerId` | Customer user ID | ✅ On register |
| `shopkeeperId` | Shopkeeper user ID | ✅ On register |
| `productId` | Product ID | ✅ On list products |
| `productSlug` | Product slug | ✅ On list products |
| `addressId` | Address ID | ✅ On create address |
| `cartItemId` | Cart item ID | ✅ On add to cart |
| `orderId` | Order ID | ✅ On checkout |
| `reviewId` | Review ID | ✅ On create review |

## 📝 Test Scripts

Collections include automatic test scripts that:
- Extract and save tokens after login
- Save IDs for use in subsequent requests
- Validate response codes

## 🏃 Running Tests

### Manual Testing
1. Run requests individually in order
2. Check response codes and bodies

### Automated Testing (Newman)
```bash
npm install -g newman

# Run all collections
newman run Ecommerce_API_Part1.json
newman run Ecommerce_API_Part2.json
newman run Ecommerce_API_Part3.json
```

## ⚠️ Prerequisites

1. Django server running at `http://localhost:8000`
2. Database migrated with test data
3. At least one product in database for cart/order tests
