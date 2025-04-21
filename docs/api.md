# Shop API Documentation

## Authentication

Most endpoints require authentication using JWT (JSON Web Tokens). Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Account Management

### Sign Up
- **URL**: `/signup/`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:

  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```

- **Success Response**: `201 CREATED`

  ```json
  {
    "message": "Registration successful. Please check your email for verification.",
    "user": {
      "email": "user@example.com"
    }
  }
  ```

### Email Verification

- **URL**: `/verify-email/`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:

  ```json
  {
    "email": "user@example.com",
    "verification_code": "abc123"
  }
  ```

- **Success Response**: `200 OK`

  ```json
  {
    "message": "Email verified successfully."
  }
  ```

### Resend Verification Email

- **URL**: `/resend-verification/`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:

  ```json
  {
    "email": "user@example.com"
  }
  ```

- **Success Response**: `200 OK`
  ```json
  {
    "message": "Verification code resent successfully"
  }
  ```

### Login

- **URL**: `/login/`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:

  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```

- **Success Response**: `200 OK`

  ```json
  {
    "refresh": "refresh_token",
    "access": "access_token",
    "user": {
      "email": "user@example.com",
      "other_fields": "values"
    }
  }
  ```

### Request Password Reset

- **URL**: `/request-password-reset/`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:

  ```json
  {
    "email": "user@example.com"
  }
  ```

- **Success Response**: `200 OK`

  ```json
  {
    "message": "Password reset instructions sent to your email"
  }
  ```

### Reset Password

- **URL**: `/reset-password/`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:

  ```json
  {
    "email": "user@example.com",
    "token": "reset_token",
    "new_password": "newpassword"
  }
  ```

- **Success Response**: `200 OK`

  ```json
  {
    "message": "Password reset successful"
  }
  ```

### Profile Management

- **URL**: `/profile/`
- **Method**: `GET`, `PUT`
- **Auth Required**: Yes
- **PUT Request Body**:

  ```json
  {
    "field_to_update": "new_value"
  }
  ```

- **Success Response**: `200 OK`

  ```json
  {
    "user_data": {
      "email": "user@example.com",
      "other_fields": "values"
    }
  }
  ```

## Categories
### List Categories

- **URL**: /categories/
- **Method**: GET
- **Auth Required**: No
- **Success Response**: 200 OK

  ```json
  [
    {
      "id": 1,
      "name": "Electronics",
      "description": "Electronic devices and accessories"
    }
  ]
  ```


### Create Category

- **URL**: /categories/
- **Method**: POST
- **Auth Required**: Yes (Admin only)
- **Request Body**:
  ```json
  {
    "name": "Electronics",
    "description": "Electronic devices and accessories"
  }
  ```

- **Success Response**: 201 CREATED
  ```json
  {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic devices and accessories"
  }
  ```


### Get Category Details

- **URL**: /categories/{category_id}/
- **Method**: GET
- **Auth Required**: No
- **Success Response**: 200 OK
  ```json
  {
    "id": 1,
    "name": "Electronics",
    "description": "Electronic devices and accessories"
  }
  ```


### Update Category

- **URL**: /categories/{category_id}/
- **Method**: PUT
- **Auth Required**: Yes (Admin only)
- **Request Body**:
  ```json
  {
    "name": "Electronics",
    "description": "Updated description for electronics category"
  }
  ```

- **Success Response**: 200 OK
  ```json
  {
    "id": 1,
    "name": "Electronics",
    "description": "Updated description for electronics category"
  }
  ```


### Delete Category

- **URL**: /categories/{category_id}/
- **Method**: DELETE
- **Auth Required**: Yes (Admin only)
- **Success Response**: 204 NO CONTENT

## Products

### List Products

- **URL**: `/products/`
- **Method**: `GET`
- **Auth Required**: No
- **Query Parameters**:
  - `search`: Search term for name/description
  - `category`: Filter by category ID
  - `material`: Filter by material
  - `condition`: Filter by condition
  - `min_price`: Minimum price
  - `max_price`: Maximum price
  - `available`: Filter by availability (true/false)
  - `ordering`: Sort by (-price, price, -created_at, created_at, name, -name)
- **Success Response**: `200 OK`

  ```json
  {
    "count": 100,
    "next": "URL",
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Product Name",
        "price": 99.99
      }
    ]
  }
  ```

### Product Details

- **URL**: `/products/{product_id}/`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: `200 OK`

  ```json
  {
    "id": 1,
    "name": "Product Name",
    "description": "Description",
    "price": 99.99,
    "category": 1,
    "reviews": []
  }
  ```

### Create Product

- **URL**: `/products/`
- **Method**: `POST`
- **Auth Required**: Yes (Admin only)
- **Request Body**:

  ```json
  {
    "category": 1,
    "name": "Modern Dining Chair",
    "description": "Comfortable dining chair with ergonomic design",
    "price": 199.99,
    "stock": 10,
    "primary_material": "WOOD",
    "condition": "NEW",
    "image": "base64_encoded_image_string",
    "additional_images": "base64_encoded_image_string",
    "is_available": true
  }
  ```

- **Notes**:
  - `category` must be a valid category ID
  - `primary_material` must be one of: WOOD, METAL, FABRIC, LEATHER, GLASS, PLASTIC
  - `condition` must be one of: NEW, USED, REFURBISHED
  - `image` and `additional_images` should be base64 encoded strings of the image files
  - `price` must be a positive number with up to 2 decimal places
  - `stock` must be a positive integer

- **Success Response**: `201 CREATED`

  ```json
  {
    "id": 1,
    "category": {
      "id": 1,
      "name": "Chairs"
    },
    "name": "Modern Dining Chair",
    "description": "Comfortable dining chair with ergonomic design",
    "price": "199.99",
    "stock": 10,
    "primary_material": "WOOD",
    "condition": "NEW",
    "image": "cloudinary_url",
    "additional_images": "cloudinary_url",
    "is_available": true,
    "created_at": "2025-02-18T10:00:00Z",
    "updated_at": "2025-02-18T10:00:00Z"
  }
  ```

### Update Product

- **URL**: `/products/{product_id}/`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin only)
- **Request Body**:

  ```json
  {
    "category": 1,
    "name": "Modern Dining Chair",
    "description": "Updated description for the dining chair",
    "price": 179.99,
    "stock": 15,
    "primary_material": "WOOD",
    "condition": "NEW",
    "image": "base64_encoded_image_string",
    "additional_images": "base64_encoded_image_string",
    "is_available": true
  }
  ```

- **Notes**:
  - All fields are optional in the update request
  - Only provided fields will be updated
  - Image fields can be updated by providing new base64 encoded strings
  - Existing images will remain if no new images are provided

- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "category": {
      "id": 1,
      "name": "Chairs"
    },
    "name": "Modern Dining Chair",
    "description": "Updated description for the dining chair",
    "price": "179.99",
    "stock": 15,
    "primary_material": "WOOD",
    "condition": "NEW",
    "image": "cloudinary_url",
    "additional_images": "cloudinary_url",
    "is_available": true,
    "created_at": "2025-02-18T10:00:00Z",
    "updated_at": "2025-02-18T10:30:00Z"
  }
  ```

### Delete Product

- **URL**: `/products/{product_id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin only)
- **Notes**:
  - Deleting a product will also remove associated reviews
  - Product will be removed from all wishlists
  - Associated images will be deleted from Cloudinary
  - Cannot delete products that are part of existing orders

- **Success Response**: `204 NO CONTENT`


### Product Reviews

- **URL**: `/products/{product_id}/reviews/`
- **Method**: `GET`, `POST`
- **Auth Required**: Yes (for POST)
- **POST Request Body**:

  ```json
  {
    "rating": 5,
    "comment": "Great product!"
  }
  ```

- **Success Response**: `201 CREATED`

### Wishlist Management

- **URL**: `/wishlist/`
- **Methods**: `GET`, `POST`
- **Auth Required**: Yes
- **POST Request Body**:

  ```json
  {
    "product_id": 1
  }
  ```

- **Success Response**: `200 OK`

  ```json
  {
    "products": [
      {
        "id": 1,
        "name": "Product Name"
      }
    ]
  }
  ```

### Remove from Wishlist

- **URL**: `/wishlist/{product_id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Success Response**: `204 NO CONTENT`

## Shopping Cart

### View Cart

- **URL**: `/cart/`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**: `200 OK`

  ```json
  {
    "id": 1,
    "items": [
      {
        "id": 1,
        "product": {
          "id": 1,
          "name": "Product Name",
          "price": 99.99
        },
        "quantity": 2
      }
    ],
    "total": 199.98
  }
  ```

### Add to Cart

- **URL**: `/cart/`
- **Method**: `POST`
- **Auth Required**: Yes
- **Request Body**:

  ```json
  {
    "product_id": 1,
    "quantity": 2
  }
  ```

- **Success Response**: `200 OK`

  ```json
  {
    "cart_data": {
      "items": [],
      "total": 0
    }
  }
  ```

### Update Cart Item

- **URL**: `/cart/item/{item_id}/`
- **Method**: `PUT`
- **Auth Required**: Yes
- **Request Body**:

  ```json
  {
    "quantity": 3
  }
  ```

- **Success Response**: `200 OK`

  ```json
  {
    "cart_data": {
      "items": [],
      "total": 0
    }
  }
  ```

### Remove Cart Item

- **URL**: `/cart/item/{item_id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Success Response**: `200 OK`

  ```json
  {
    "cart_data": {
      "items": [],
      "total": 0
    }
  }
  ```

### Clear Cart

- **URL**: `/cart/`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Success Response**: `200 OK`

  ```json
  {
    "cart_data": {
      "items": [],
      "total": 0
    }
  }
  ```

## Orders

### List Orders

- **URL**: `/orders/`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**: `200 OK`

  ```json
  [
    {
      "id": 1,
      "status": "PENDING",
      "items": [],
      "total": 0
    }
  ]
  ```

### Create Order from Cart
- **URL**: `/orders/create/`
- **Method**: `POST`
- **Auth Required**: Yes
- **Success Response**: `201 CREATED`

  ```json
  {
    "id": 1,
    "status": "PENDING",
    "items": [],
    "total": 0
  }
  ```

### View Order Details
- **URL**: `/orders/{order_id}/`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**: `200 OK`

  ```json
  {
    "id": 1,
    "status": "PENDING",
    "items": [],
    "total": 0
  }
  ```

### Update Order Address

- **URL**: `/orders/{order_id}/address/`
- **Method**: `PUT`
- **Auth Required**: Yes
- **Request Body**:

  ```json
  {
    "shipping_address": "123 Main St",
    "billing_address": "123 Main St"
  }
  ```

- **Success Response**: `200 OK`

### Update Order Status

- **URL**: `/orders/{order_id}/status/`
- **Method**: `PUT`
- **Auth Required**: Yes
- **Request Body**:

  ```json
  {
    "status": "SHIPPED",
    "tracking_number": "1234567890"
  }
  ```
- **Success Response**: `200 OK`

### Delete Order

- **URL**: `/orders/{order_id}/delete/`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Constraints**: Only PENDING orders can be deleted
- **Success Response**: `204 NO CONTENT`

## Sales Analysis
## Daily Sales

### List Daily Sales
- **URL**: `/analytics/daily-sales/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "date": "2025-04-20",
      "total_sales": 2500.00,
      "order_count": 15,
      "average_order_value": 166.67,
      "unique_customers": 12,
      "new_customers": 3
    }
  ]
  ```

### Create Daily Sales Record
- **URL**: `/analytics/daily-sales/`
- **Method**: `POST`
- **Auth Required**: Yes (Admin only)
- **Request Body**:
  ```json
  {
    "date": "2025-04-20",
    "total_sales": 2500.00,
    "order_count": 15,
    "average_order_value": 166.67,
    "unique_customers": 12,
    "new_customers": 3
  }
  ```
- **Success Response**: `201 CREATED`

### View Daily Sales Details
- **URL**: `/analytics/daily-sales/{id}/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "date": "2025-04-20",
    "total_sales": 2500.00,
    "order_count": 15,
    "average_order_value": 166.67,
    "unique_customers": 12,
    "new_customers": 3
  }
  ```

### Update Daily Sales Record
- **URL**: `/analytics/daily-sales/{id}/`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin only)
- **Request Body**: Same as POST
- **Success Response**: `200 OK`

### Delete Daily Sales Record
- **URL**: `/analytics/daily-sales/{id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `204 NO CONTENT`

### Generate Daily Sales Report
- **URL**: `/analytics/daily-sales/report/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Query Parameters**:
  - `start_date`: Start date (YYYY-MM-DD)
  - `end_date`: End date (YYYY-MM-DD)
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "date": "2025-04-20",
      "total_sales": 2500.00,
      "order_count": 15,
      "average_order_value": 166.67,
      "unique_customers": 12,
      "new_customers": 3
    }
  ]
  ```

## Product Performance

### List Product Performance
- **URL**: `/analytics/product-performance/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "date": "2025-04-20",
      "product": 5,
      "units_sold": 42,
      "revenue": 1260.00,
      "average_rating": 4.7
    }
  ]
  ```

### Create Product Performance Record
- **URL**: `/analytics/product-performance/`
- **Method**: `POST`
- **Auth Required**: Yes (Admin only)
- **Request Body**:
  ```json
  {
    "date": "2025-04-20",
    "product": 5,
    "units_sold": 42,
    "revenue": 1260.00,
    "average_rating": 4.7
  }
  ```
- **Success Response**: `201 CREATED`

### View Product Performance Details
- **URL**: `/analytics/product-performance/{id}/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "date": "2025-04-20",
    "product": 5,
    "units_sold": 42,
    "revenue": 1260.00,
    "average_rating": 4.7
  }
  ```

### Update Product Performance Record
- **URL**: `/analytics/product-performance/{id}/`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin only)
- **Request Body**: Same as POST
- **Success Response**: `200 OK`

### Delete Product Performance Record
- **URL**: `/analytics/product-performance/{id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `204 NO CONTENT`

### Generate Product Performance Report
- **URL**: `/analytics/product-performance/report/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Query Parameters**:
  - `start_date`: Start date (YYYY-MM-DD)
  - `end_date`: End date (YYYY-MM-DD)
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "date": "2025-04-20",
      "product": 5,
      "units_sold": 42,
      "revenue": 1260.00,
      "average_rating": 4.7
    }
  ]
  ```

## Category Performance

### List Category Performance
- **URL**: `/analytics/category-performance/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "date": "2025-04-20",
      "category": 2,
      "products_sold": 67,
      "revenue": 3350.00
    }
  ]
  ```

### Create Category Performance Record
- **URL**: `/analytics/category-performance/`
- **Method**: `POST`
- **Auth Required**: Yes (Admin only)
- **Request Body**:
  ```json
  {
    "date": "2025-04-20",
    "category": 2,
    "products_sold": 67,
    "revenue": 3350.00
  }
  ```
- **Success Response**: `201 CREATED`

### View Category Performance Details
- **URL**: `/analytics/category-performance/{id}/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "date": "2025-04-20",
    "category": 2,
    "products_sold": 67,
    "revenue": 3350.00
  }
  ```

### Update Category Performance Record
- **URL**: `/analytics/category-performance/{id}/`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin only)
- **Request Body**: Same as POST
- **Success Response**: `200 OK`

### Delete Category Performance Record
- **URL**: `/analytics/category-performance/{id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `204 NO CONTENT`

### Generate Category Performance Report
- **URL**: `/analytics/category-performance/report/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Query Parameters**:
  - `start_date`: Start date (YYYY-MM-DD)
  - `end_date`: End date (YYYY-MM-DD)
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "date": "2025-04-20",
      "category": 2,
      "products_sold": 67,
      "revenue": 3350.00
    }
  ]
  ```

## Customer Insights

### List Customer Insights
- **URL**: `/analytics/customer-insights/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "user": 8,
      "total_spent": 4750.00,
      "orders_count": 12,
      "average_order_value": 395.83,
      "first_purchase_date": "2024-11-15",
      "last_purchase_date": "2025-04-18",
      "preferred_category": 3
    }
  ]
  ```

### Create Customer Insight Record
- **URL**: `/analytics/customer-insights/`
- **Method**: `POST`
- **Auth Required**: Yes (Admin only)
- **Request Body**:
  ```json
  {
    "user": 8,
    "total_spent": 4750.00,
    "orders_count": 12,
    "average_order_value": 395.83,
    "first_purchase_date": "2024-11-15",
    "last_purchase_date": "2025-04-18",
    "preferred_category": 3
  }
  ```
- **Success Response**: `201 CREATED`

### View Customer Insight Details
- **URL**: `/analytics/customer-insights/{id}/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "user": 8,
    "total_spent": 4750.00,
    "orders_count": 12,
    "average_order_value": 395.83,
    "first_purchase_date": "2024-11-15",
    "last_purchase_date": "2025-04-18",
    "preferred_category": 3
  }
  ```

### Update Customer Insight Record
- **URL**: `/analytics/customer-insights/{id}/`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin only)
- **Request Body**: Same as POST
- **Success Response**: `200 OK`

### Delete Customer Insight Record
- **URL**: `/analytics/customer-insights/{id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `204 NO CONTENT`

### Generate Customer Insights
- **URL**: `/analytics/customer-insights/generate/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "user": 8,
      "total_spent": 4750.00,
      "orders_count": 12,
      "average_order_value": 395.83,
      "first_purchase_date": "2024-11-15",
      "last_purchase_date": "2025-04-18",
      "preferred_category": 3
    }
  ]
  ```

## Sales Reports

### List Sales Reports
- **URL**: `/analytics/sales-reports/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "report_type": "MONTHLY",
      "start_date": "2025-03-01",
      "end_date": "2025-03-31",
      "generated_at": "2025-04-01T10:30:45Z",
      "total_sales": 78500.00,
      "total_orders": 427,
      "average_order_value": 183.84,
      "top_products": [1, 5, 8],
      "top_categories": [2, 4]
    }
  ]
  ```

### Create Sales Report
- **URL**: `/analytics/sales-reports/`
- **Method**: `POST`
- **Auth Required**: Yes (Admin only)
- **Request Body**:
  ```json
  {
    "report_type": "MONTHLY",
    "start_date": "2025-03-01",
    "end_date": "2025-03-31",
    "total_sales": 78500.00,
    "total_orders": 427,
    "average_order_value": 183.84,
    "top_products": [1, 5, 8],
    "top_categories": [2, 4]
  }
  ```
- **Success Response**: `201 CREATED`

### View Sales Report Details
- **URL**: `/analytics/sales-reports/{id}/`
- **Method**: `GET`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "report_type": "MONTHLY",
    "start_date": "2025-03-01",
    "end_date": "2025-03-31",
    "generated_at": "2025-04-01T10:30:45Z",
    "total_sales": 78500.00,
    "total_orders": 427,
    "average_order_value": 183.84,
    "top_products": [1, 5, 8],
    "top_categories": [2, 4]
  }
  ```

### Update Sales Report
- **URL**: `/analytics/sales-reports/{id}/`
- **Method**: `PUT`
- **Auth Required**: Yes (Admin only)
- **Request Body**: Same as POST
- **Success Response**: `200 OK`

### Delete Sales Report
- **URL**: `/analytics/sales-reports/{id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `204 NO CONTENT`

### Generate Sales Report
- **URL**: `/analytics/sales-reports/generate/`
- **Method**: `POST`
- **Auth Required**: Yes (Admin only)
- **Request Body**:
  ```json
  {
    "report_type": "MONTHLY",
    "start_date": "2025-03-01",
    "end_date": "2025-03-31"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "report_type": "MONTHLY",
    "start_date": "2025-03-01",
    "end_date": "2025-03-31",
    "generated_at": "2025-04-21T14:52:20Z",
    "total_sales": 78500.00,
    "total_orders": 427,
    "average_order_value": 183.84,
    "top_products": [1, 5, 8],
    "top_categories": [2, 4]
  }
  ```

## Update Sales Metrics

### Trigger Sales Metrics Update
- **URL**: `/analytics/update-metrics/`
- **Method**: `POST`
- **Auth Required**: Yes (Admin only)
- **Success Response**: `200 OK`
  ```json
  {
    "message": "Sales metrics update triggered successfully"
  }
  ```


## Error Responses

All endpoints may return the following error responses:

- `400 BAD REQUEST`: Invalid input data
- `401 UNAUTHORIZED`: Missing or invalid authentication
- `403 FORBIDDEN`: Insufficient permissions
- `404 NOT FOUND`: Resource not found
- `500 INTERNAL SERVER ERROR`: Server error

Error responses include a message explaining the error:

```json
{
  "error": "Error message description"
}
```