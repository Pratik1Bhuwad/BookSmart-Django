# BookSmart-Django

A robust, multi-role Django booking application. This project features a service marketplace where providers can manage their services, schedules, and appointments, while clients can easily book, pay, and track their requests.

## Features

* **Multi-Role Authentication**: Users can register as either a `Client` or a `Service Provider`.
* **Service Marketplace**: Providers can define their own service offerings, including custom pricing, duration, and locations.
* **Dynamic Booking Flow**: Clients can browse services by category, select a provider, and book an appointment with real-time availability checks.
* **Stripe Integration**: Secure payment processing is handled via Stripe's API (in sandbox mode).
* **Asynchronous Notifications**: Email confirmations are triggered using Django signals.
* **Responsive UI**: Built with Bootstrap 5 for a clean and mobile-friendly interface.
* **Provider Management Portal**: A dedicated dashboard for providers to manage their schedules, services, and appointment requests.

## Tech Stack

* **Backend**: Django (Python)
* **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
* **Database**: SQLite (Development)
* **Payment Gateway**: Stripe

## Getting Started

### Prerequisites

* Python 3.8+
* pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Pratik1Bhuwad/BookSmart-Django.git](https://github.com/Pratik1Bhuwad/BookSmart-Django.git)
    cd BookSmart-Django
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your database:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    ```

5.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

## 🎨 Database Schema

This ER diagram illustrates the structure of the application's models and their relationships.
