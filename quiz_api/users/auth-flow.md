# Authentication Flow

This document outlines the authentication flow used in our Django REST Framework backend with Next.js frontend, utilizing JWT (JSON Web Tokens) stored in HTTP-only cookies.

## Overview

Our authentication system uses JWT tokens stored in HTTP-only cookies for enhanced security. It supports both cookie-based and header-based token authentication.

## Key Components

### Backend (Django REST Framework)

1. **CustomJWTAuthentication**
   - Custom authentication class that checks for JWT in cookies or HTTP header.

2. **CookieTokenObtainPairView**
   - Handles user login and sets JWT cookies.

3. **CookieTokenRefreshView**
   - Refreshes the access token using the refresh token cookie.

4. **RegisterView**
   - Handles user registration and initial token generation.

5. **LogoutView**
   - Handles user logout by clearing JWT cookies.

6. **auth_check**
   - Endpoint to verify user authentication status.

### Frontend (Next.js)

1. **ProtectedRoute component**
   - Wraps protected pages and checks authentication status.

2. **API utilities**
   - Handles API requests, including credentials for cookie-based auth.

## Authentication Flow

1. **User Registration**
   - User submits registration data to `/register/`.
   - Backend creates user and generates tokens.
   - Tokens are set as HTTP-only cookies in the response.

2. **User Login**
   - User submits credentials to `/token/`.
   - Backend validates and generates tokens.
   - Tokens are set as HTTP-only cookies in the response.

3. **Authenticated Requests**
   - Requests to protected endpoints include HTTP-only cookies.
   - `CustomJWTAuthentication` validates the token.
   - If valid, the request is processed; if not, it's rejected.

4. **Token Refresh**
   - Frontend sends refresh request to `/token/refresh/` when access token expires.
   - Backend validates refresh token and issues new access token.
   - New access token is set as an HTTP-only cookie.

5. **Authentication Check**
   - Frontend can verify auth status via `/auth-check/`.
   - Endpoint returns success if a valid token is present.

6. **User Logout**
   - Frontend sends request to `/logout/`.
   - Backend clears the token cookies.

## Security Features

- **HTTP-only Cookies**: Prevents client-side JavaScript from accessing tokens, mitigating XSS attacks.
- **Short-lived Access Tokens**: Access tokens expire after 15 minutes.
- **Refresh Tokens**: Allows obtaining new access tokens without re-authentication.
- **CORS Configuration**: Ensures only the frontend can make authenticated requests.

## Configuration

Key settings in `settings.py`:

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    # ... other JWT settings ...
}

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    # Add your frontend URLs here
]