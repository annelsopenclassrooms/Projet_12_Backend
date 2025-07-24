# Epic Events CRM

Epic Events CRM is a command-line application written in Python 3.  
It allows managing clients, contracts, and events for the company **Epic Events**.

## Features

- User management with roles (sales, management, support)
- Client, contract, and event management
- Secure password hashing with bcrypt
- Lightweight and portable SQLite database
- Follows the principle of least privilege

## Technologies

- Python 3.9+
- SQLite
- bcrypt

## Installation

### 1. Clone the project

```bash
git clone git@github.com:annelsopenclassrooms/Projet_12_Backend.git
```

### 2. Create and activate a virtual environment :

   ```sh
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```
### 3. Install dependencies :

   ```sh
   pip install -r requirements.txt
   ```

### 4. Create a user

   ```sh
   python create_user.py
   ```

### 5. Run the application

   ```sh
   python main.py
   ```

## Database Structure

#### Roles

* id (Integer, PK)
* name (String, unique, not null)

#### Users

* id (Integer, PK)
* username (String, unique, not null)
* first_name (String, not null)
* last_name (String, not null)
* email (String, unique, not null)
* hashed_password (String, not null)
* role_id (Integer, FK → Roles.id)

#### Clients

* id (Integer, PK)
* first_name (String, not null)
* last_name (String, not null)
* email (String, unique, not null)
* phone (String)
* company_name (String)
* date_created (DateTime, default = now)
* date_updated (DateTime, auto-updated)
* commercial_id (Integer, FK → Users.id)

#### Contracts

* id (Integer, PK)
* client_id (Integer, FK → Clients.id)
* commercial_id (Integer, FK → Users.id)
* total_amount (Float, not null)
* amount_due (Float, not null)
* date_created (DateTime, default = now)
* is_signed (Boolean, default = False)

#### Events

* id (Integer, PK)
* name (String, not null)
* contract_id (Integer, FK → Contracts.id)
* client_id (Integer, FK → Clients.id)
* support_contact_id (Integer, FK → Users.id, nullable)
* date_start (DateTime, not null)
* date_end (DateTime, not null)
* location (String)
* attendees (Integer)
* notes (String)