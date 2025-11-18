# E-Shop API

A robust Django REST Framework backend for a modern e-commerce platform with comprehensive product management, user authentication, order processing, payment integration, and sales analytics.

![E-Shop API](https://img.shields.io/badge/E--Shop-API-brightgreen)
![Django](https://img.shields.io/badge/Django-4.2-green)
![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.14-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![Python](https://img.shields.io/badge/Python-3.12-yellow)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [API Structure](#api-structure)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Overview

This Django-powered RESTful API serves as the backend for a feature-rich e-commerce platform. It provides secure endpoints for user management, product catalog operations, order processing, payment handling, and sales analytics.

## Features

- **User Authentication & Authorization** - JWT-based secure authentication
- **Product Management** - Comprehensive catalog with categories, reviews, and images
- **Order Processing** - Cart management, checkout, and order history
- **Payment Integration** - Secure Stripe payment processing
- **Sales Analytics** - Advanced reporting and data visualization
- **Cloud Storage** - Cloudinary integration for media files
- **CORS Support** - Configured for cross-origin requests

## Tech Stack

- **[Django](https://www.djangoproject.com/)** - High-level Python web framework
- **[Django REST Framework](https://www.django-rest-framework.org/)** - Toolkit for building Web APIs
- **[PostgreSQL](https://www.postgresql.org/)** - Advanced open-source database
- **[JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)** - Token-based authentication
- **[Stripe](https://stripe.com/)** - Payment processing platform
- **[Cloudinary](https://cloudinary.com/)** - Cloud-based image and video management
- **[Gunicorn](https://gunicorn.org/)** - WSGI HTTP Server for UNIX

## API Structure

The API is organized into the following Django apps:

### Accounts
- User registration, authentication, and profile management
- Permission-based access control
- Password reset functionality
- Social authentication options

### Products
- Product catalog with categories and subcategories
- Product images, details, and specifications
- Inventory management
- Review and rating system
- Search, filter, and sorting capabilities

### Orders
- Shopping cart functionality
- Order creation and management
- Order status tracking
- Shipping and delivery options

### Payments
- Secure payment processing via Stripe
- Multiple payment methods
- Invoice generation
- Refund processing

### Sales Analysis
- Sales reports and statistics
- Revenue tracking
- Product performance metrics
- Customer behavior analysis

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/0097eo/eshop.git
   cd eshop
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies using Pipenv**
   ```bash
   pip install pipenv
   pipenv install
   ```

4. **Set up the PostgreSQL database**
   - Install PostgreSQL if not already installed
   - Create a database for the project

5. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Django Settings
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgres://user:password@localhost:5432/dbname

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Stripe Configuration
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

## Running the Project

1. **Start the development server**
   ```bash
   python manage.py runserver
   ```

2. **Access the API**
   - Main API: http://127.0.0.1:8000/api/
   - Admin interface: http://127.0.0.1:8000/admin/

## API Documentation

### Authentication Endpoints

```
POST /api/accounts/register/         # Register a new user
POST /api/accounts/login/            # Log in and get token
POST /api/accounts/token/refresh/    # Refresh token
GET  /api/accounts/profile/          # Get user profile
PUT  /api/accounts/profile/          # Update user profile
```

### Product Endpoints

```
GET    /api/products/                # List all products
GET    /api/products/{id}/           # Get product details
GET    /api/products/categories/     # List all categories
GET    /api/products/{id}/reviews/   # Get product reviews
POST   /api/products/{id}/reviews/   # Create a product review
```

### Order Endpoints

```
GET    /api/orders/                  # List user's orders
POST   /api/orders/                  # Create a new order
GET    /api/orders/{id}/             # Get order details
PUT    /api/orders/{id}/             # Update an order
GET    /api/orders/cart/             # Get current cart
POST   /api/orders/cart/items/       # Add item to cart
```

### Payment Endpoints

```
POST   /api/payments/process/        # Process payment
GET    /api/payments/history/        # Payment history
POST   /api/payments/webhook/        # Stripe webhook
```

### Sales Analysis Endpoints

```
GET    /api/analytics/sales/         # Get sales statistics
GET    /api/analytics/products/      # Product performance
GET    /api/analytics/customers/     # Customer analytics
```

For detailed API documentation with request/response examples, navigate to the docs directory:

## Deployment

### Preparing for Production

1. Set `DEBUG=False` in the `.env` file
2. Update `ALLOWED_HOSTS` with your production domain
3. Configure proper CORS settings in `settings.py`

### Deploying to a Server

1. **Set up the production server**
   - Install required packages: Python, PostgreSQL, etc.
   - Configure Nginx or Apache as a reverse proxy

2. **Clone the repository and install dependencies**
   ```bash
   git clone https://github.com/your-username/eshop-api.git
   cd eshop-api
   pipenv install
   ```

3. **Set up environment variables**
   - Create `.env` file with production settings

4. **Run migrations and collect static files**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

5. **Start the Gunicorn server**
   ```bash
   gunicorn eshop.wsgi:application
   ```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

---

Built using Django and DRF
