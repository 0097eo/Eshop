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