# Django Service Layer
A clean, structured approach to organizing business logic in Django applications using a dedicated service layer with built-in error handling and logging.

## Overview
This repository demonstrates an implementation of the Service Layer pattern for Django REST Framework applications. The pattern separates business logic from views and models, promoting cleaner code organization, better testability, and consistent error handling.

## Key Features
- Protocol-based service design - All services follow a consistent interface
- Self-documenting errors - Error messages use docstrings by default
- Structured logging - Comprehensive error logging with full context
- Clean separation - Business logic isolated from views and serializers
- Type safety - Full type hints and dataclass support

## Architecture
1. Service Protocol
```python
class IService(Protocol):
    def __call__(self, **kwargs) -> Any:
        """Business logic here. Use only keyword arguments."""
```
2. Base Service Error
```python
class BaseServiceError(Exception):
    def __init__(self, message: str = None, **context) -> None:
        self.message = message or self.__doc__  # Uses docstring as default message
        self.context = context  # Additional error context for logging/response
```
3. Error logging decorator
```python
@log_service_error
def __call__(self, *, product_id: int, customer: Customer) -> None:
    # Business logic with automatic error logging
```
4. Service Exception Handler - Transforms service errors into consistent API responses with proper HTTP status codes.
```python
from rest_framework.views import exception_handler

def service_exception_handler(exc, context):
    if isinstance(exc, BaseServiceError):
        return Response(
            data={
                "error_message": exc.message,
                "error_context": dict(**exc.context),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    return exception_handler(exc, context)
```
## Usage example
1. Create a service
```python
@dataclass(kw_only=True, slots=True, frozen=True)
class BuyProductService:
    @log_service_error
    def __call__(self, *, product_id: int, customer: Customer) -> None:
        product = Product.objects.filter(pk=product_id).first()
        if product is None:
            raise ProductDoesNotExist(
                customer=dict(id=customer.pk),
                product=dict(id=product_id),
            )
        
        # Business logic here
```
2. Define custom exceptions
```python
class ProductDoesNotExist(BaseServiceError):
    """Product does not exist."""

class NotEnoughBalance(BaseServiceError):
    """Customer does not have enough balance."""
```
3. Use in Django View
```python
class BuyProductView(APIView):
    def post(self, request: Request) -> Response:
        # Validation
        serializer = BuyProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Business logic
        BuyProductService()(
            customer=request.user.customer,
            product_id=data.get("product_id"),
        )

        return Response(
            data={"message": "Thank you for buying!"},
            status=status.HTTP_200_OK,
        )
```
## Error handling
Automatic Logging
Service errors are automatically logged with:

- Error location (class name)
- Error type
- Error message
- Full context data

## API Response Format
Service errors return structured responses:
```json
{
    "error_message": "Customer does not have enough balance.",
    "error_context": {
        "customer": {"id": 1, "balance": 50.00},
        "product": {"id": 5, "price": 99.99, "name": "Premium Product"}
    }
}
```
## Benefits
### ✅ Clean Code Organization
- Business logic separated from HTTP layer
- Services are testable in isolation
- Consistent interface across all services

### ✅ Better Error Handling
- Self-documenting error messages
- Structured error context
- Automatic logging

### ✅ Type Safety
- Full type hints support
- Dataclass-based service containers
- Protocol enforcement

### ✅ Performance
- slots=True for memory efficiency
- frozen=True for immutability
- kw_only=True for explicit keyword arguments

## Project Structure
```text
django-service-layer/
├── src/                          
│   ├── apps/                    
│   │   ├── customer/             
│   │   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   └── models.py        
│   │   └── product/              
│   │       ├── migrations/
│   │       ├── serializers/
│   │       ├── services/
│   │       ├── __init__.py
│   │       ├── admin.py
│   │       ├── apps.py
│   │       ├── exceptions.py
│   │       ├── models.py         
│   │       ├── urls.py
│   │       └── views.py 
│   ├── config/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── core/
│   │   └── service
│   └── manage.py
├── .gitignore
├── example.py
├── pyproject.toml        
├── README.md
└── uv.lock
```
## Support
For issues and questions, please open an issue in the GitHub repository.
