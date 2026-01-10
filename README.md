# (Django) Service Layer — (D)SL
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-9C2B2B?style=for-the-badge&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![ElasticSearch](https://img.shields.io/badge/Elasticsearch-005571?style=for-the-badge&logo=elasticsearch&logoColor=white)
![Logstash](https://img.shields.io/badge/Logstash-005571?style=for-the-badge&logo=logstash&logoColor=white)
![Kibana](https://img.shields.io/badge/Kibana-005571?style=for-the-badge&logo=kibana&logoColor=white)

This repository provides a structured and clean architectural pattern for implementing a service layer in Django applications. It focuses on separating business logic from the view layer, promoting testability, and ensuring consistent, structured error handling and logging.

The project demonstrates a sample e-commerce feature (`BuyProduct`) built with this pattern, complete with an integrated ELK stack (Elasticsearch, Logstash, Kibana) for log monitoring.

## Key Features

*   **Clean Separation of Concerns**: Isolates complex business logic into dedicated service classes, away from views and serializers.
*   **Protocol-Based Design**: Services adhere to a simple, consistent `IService` protocol, making the architecture predictable.
*   **Structured, Automatic Logging**: A decorator (`@log_service_error`) automatically catches and logs exceptions from services in a structured JSON format, ready for log aggregators.
*   **Descriptive, Contextual Errors**: Custom exceptions carry both a human-readable message (using the class `__doc__` string by default) and a rich context dictionary for logging and debugging.
*   **Consistent API Responses**: A custom DRF exception handler translates service errors into uniform `400 Bad Request` responses.
*   **Type Safety**: Fully typed with modern Python features like `dataclasses` and `Protocol` for better maintainability and editor support.
*   **Integrated Log Management**: Includes a `docker-compose.yml` configuration to run an ELK stack for collecting and visualizing structured logs in Kibana.
*   **Dependency Injection**: Uses [**punq**](https://github.com/bobthemighty/punq) for simple and clean dependency injection, managed through a central container.

## Architecture

The pattern is built upon a few core components found in `src/apps/core/service/`.

### 1. The Service Protocol (`IService`)

All services implement a simple, callable protocol. This ensures a consistent interface for executing business logic.

```python
# src/apps/core/service/base.py
class IService(Protocol):
    def __call__(self, **kwargs) -> Any:
        """Business logic here. Use only keyword arguments."""
```

### 2. The Base Exception (`BaseServiceError`)

Custom service exceptions inherit from this base class. It automatically uses the exception's docstring as the error message and captures contextual data.

```python
# src/apps/core/service/base.py
class BaseServiceError(Exception):
    def __init__(self, message: str = None, **context) -> None:
        self.message = message or self.__doc__
        self.context = context
```

### 3. The Logging Decorator (`@log_service_error`)

This decorator wraps the service's `__call__` method, providing a `try...except` block that logs any `BaseServiceError` in a structured format before re-raising it.

```python
# src/apps/core/service/base.py
def log_service_error(__call__: Callable) -> Callable:
    @wraps(__call__)
    def wrapper(self, **kwargs) -> Any:
        try:
            return __call__(self, **kwargs)
        except BaseServiceError as error:
            logger.error(
                {
                    "error_in": self.__class__.__name__,
                    "error_name": error.__class__.__name__,
                    "error_message": error.message,
                    "error_context": dict(**error.context),
                },
            )
            raise error

    return wrapper
```

### 4. The DRF Exception Handler

This handler, configured in `settings.py`, intercepts any `BaseServiceError` that bubbles up to the view layer and formats it into a consistent JSON response.

```python
# src/apps/core/service/handle_error.py
def service_exception_handler(exc, context):
    if isinstance(exc, BaseServiceError):
        return Response(
            data={
                "error": exc.message,
                "detail": dict(**exc.context),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    return exception_handler(exc, context)
```

## How It Works: A Practical Example

Let's follow the flow of a user buying a product.

### 1. Define DTOs and Custom Exceptions

Data Transfer Objects (DTOs) define the data structures for service inputs. We also define specific exceptions for our business domain.

```python
# src/apps/product/services/dtos/buy_product_dto.py
@dataclass(kw_only=True, frozen=True, slots=True)
class BuyProductIn(BaseServiceDTO):
    id: int
    count: int

# src/apps/product/exceptions.py
class NotEnoughBalance(BaseServiceError):
    """Not enough balance"""

class ProductNotFound(BaseServiceError):
    """Product not found"""
```

### 2. Create the Service

The service is a `dataclass` that contains the business logic. It performs checks and raises exceptions with context if something goes wrong. Dependencies like `SendCRMService` are injected upon instantiation.

```python
# src/apps/product/services/buy_product_service.py
@final
@dataclass(kw_only=True, slots=True, frozen=True)
class BuyProductService:
    product: BuyProductIn
    crm_sender: SendCRMService

    @log_service_error
    def __call__(self, *, customer: Customer) -> BuyProductOut:
        # ... business logic ...
        if customer.can_buy_max_count_of(product) < self.product.count:
            raise NotEnoughBalance(
                product=dict(id=product.pk, count=product.count, price=product.price),
                customer=dict(id=customer.pk, balance=customer.balance),
            )
        # ...
        return self._buy(product=product, customer=customer)
```

Dependencies are registered with the `punq` container using factory functions.

```python
# src/apps/product/services/buy_product_service.py
def buy_product_service_factory(product: dict) -> BuyProductService:
    return BuyProductService(
        product=BuyProductIn(**product),
        crm_sender=container.resolve("SendCRMService"),
    )

container.register("BuyProductService", factory=buy_product_service_factory)
```

### 3. Use in the View

The Django view becomes very simple. Its only responsibilities are validating the request, resolving and calling the service via the `punq` container, and returning the result.

```python
# src/apps/product/views.py
class BuyProductView(APIView):
    permission_classes = (CustomerRequired,)

    def post(self, request: Request) -> Response:
        serializer = BuyProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = container.resolve(
            "BuyProductService",
            product=serializer.validated_data,
        )(customer=request.user.customer)

        return Response(
            data=result.asdict(),
            status=status.HTTP_200_OK,
        )
```

### 4. Error Handling in Action

If the `BuyProductService` raises `NotEnoughBalance`, two things happen automatically:

1.  **Structured Log:** The `@log_service_error` decorator sends a JSON log to Logstash:
    ```json
    {
      "@timestamp": "...",
      "message": {
        "error_in": "BuyProductService",
        "error_name": "NotEnoughBalance",
        "error_message": "Not enough balance",
        "error_context": {
          "product": { "id": 1, "count": 1, "price": 500 },
          "customer": { "id": 2, "balance": 100 }
        }
      },
      "source": "django-app"
    }
    ```
2.  **API Response:** The `service_exception_handler` returns a clean error response to the client:
    ```json
    {
        "error": "Not enough balance",
        "detail": {
            "product": {
                "id": 1,
                "count": 1,
                "price": 500
            },
            "customer": {
                "id": 2,
                "balance": 100
            }
        }
    }
    ```

## Getting Started

### Prerequisites

*   Python 3.12+
*   [Docker](https://www.docker.com/get-started) and Docker Compose
*   [uv](https://github.com/astral-sh/uv) (for package management)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/youngwishes/django-service-layer.git
    cd django-service-layer
    ```
2.  **Start the logging stack (ELK):**
    ```bash
    docker-compose up -d
    ```
    This will start Elasticsearch, Logstash, and Kibana.
    *   Kibana will be available at `http://localhost:5601`.
    *   Elasticsearch will be available at `http://localhost:9200`.

3.  **Install Python dependencies:**
    ```bash
    uv sync
    ```
4.  **Set up the database:**
    ```bash
    python src/manage.py migrate
    ```
5.  **Create a superuser to access the admin panel:**
    ```bash
    python src/manage.py createsuperuser
    ```
6.  **Run the Django development server:**
    ```bash
    python src/manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000`.

### Populating Data and Logs

1.  Log into the Django admin at `http://127.0.0.1:8000/admin/` and create:
    *   A few `Product` instances with varying prices and counts.
    *   Two `User` instances.
    *   Two `Customer` instances linked to the users, with different balances.
    *   Authentication tokens for the users (in the `authtoken` section).
2.  Copy `utils/.env.example` to `utils/.env` and fill in the API tokens for your test users.
3.  Run the log population script to simulate API calls and generate error logs:
    ```bash
    python utils/populate_kibana_logs.py
    ```
4.  **View logs in Kibana:**
    *   Navigate to `http://localhost:5601`.
    *   Go to **Management > Stack Management > Index Management**. You should see the `django-logs-clean` index.
    *   Go to **Analytics > Discover** to view and search the structured logs. Logstash may take a moment to process the initial logs.

## Project Structure

```text
django-service-layer/
├── src/
│   ├── apps/
│   │   ├── core/
│   │   │   └── service/            # Core service layer components
│   │   │       ├── base.py         # IService, BaseServiceError, decorator
│   │   │       ├── handle_error.py # DRF exception handler
│   │   │       └── dtos.py         # Base DTO
│   │   ├── customer/
│   │   └── product/
│   │       ├── exceptions.py       # Custom domain exceptions
│   │       ├── services/           # Business logic services
│   │       │   ├── dtos/
│   │       │   └── buy_product_service.py
│   │       ├── serializers/
│   │       └── views.py
│   ├── config/                     # Django project settings
│   │   └── container.py            # Dependency Injection container
│   └── manage.py
├── docker-compose.yml              # ELK stack configuration
├── logstash.conf                   # Logstash pipeline configuration
├── pyproject.toml
└── README.md
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.