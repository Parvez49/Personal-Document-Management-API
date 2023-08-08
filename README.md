## Project Report: Personal Document Management API
1. Introduction:
The "Personal Document Management API" project aims to create a RESTful API that allows users to manage their documents by uploading, downloading, sharing, and searching for documents in various formats. The project utilizes the Django framework, Django REST Framework (DRF), and incorporates features such as authentication, document upload/download, sharing, metadata management, and search functionality.

2. Project Structure:
The project is organized into the following components:
- authentication: This app handles user authentication, including user registration, login, and token-based authentication.
- documents: This app manages the core functionality of document upload, download, sharing, and management.

3. Design Choices:

- User Authentication:
Django's built-in authentication system was chosen for user management. Token-based authentication was implemented for API endpoints to ensure secure user access. Role-based access control was integrated to distinguish regular users from admin users.
- Document Model:
The Document model stores metadata about uploaded documents, including title, description, upload date, format, owner, and the document file itself. The file is stored using the FileField and is uploaded to a designated directory.
- Sharing Model:
The ShareDocument model manages document sharing. It establishes a Many-to-One relationship with the Document model and a Many-to-One relationship with the User model, allowing for document sharing with multiple users.
- API Documentation:
API documentation is generated using the drf-yasg library. It provides an interactive and user-friendly Swagger interface, showcasing all API endpoints, their request methods, required parameters, and response formats. 
