# pypatch3
## application architecture
![architecture](images/pypatch3_architecture.png)
## Design decisions
- User authentication (authN) and authorization (authZ) is performed in web frontend. API services are auth-free.
- Due to the decision above, API should not be exposed outside container network
- Maria DB with MyISAM engine is to be used as datasource, as it's an open source product. Previous version (pypatch2) utilized SQLite as datasource, but with introduction of microservices, we need a server to serve concurrent connections.
- Every module in API has its own directory to contain its own `Dockerfile`
- `venv` dir resides in `pypatch3` dir, launch `vscode` there.
## Directory structure
```
pypatch3
  +- api
     +- deployment
        -- Dockerfile
     +- user
        -- Dockerfile
  +- web
        -- Dockerfile
  +- venv
  -- docker-compose.yml
  -- requirements.txt
```
## API modules
### ad

### user
Manages users and logins, provides both authN and authZ. The following endpoints are available:
- `/user/authn/<login>` GET gets {password} in JSON parameter and returns True if the user exists 
- `/user/authz/<login>/<group>` GET returns True if the user with `login` is a member of the `group` 
- `/user/<login>` GET returns a JSON representation of a user 
- `/user/<login>` POST updates a user info in DB. 
- `/user/<login>` DELETE deletes a user
- `/user/<login>` PUT creates a new user getting user info from JSON submitted as a parameter. Returns an error if such user exists already
- `/user/register` POST gets {login, email, password} parameters, checks if such "login-email" pair exists in `user` table, on success it creates a correspondent login record (unauthorized yet) and stores a hash of the password.
- `/user/approve` POST gets {login, authz_login} parameters, checks if authz_login is a member of "login_approvers" group and records "approved_by" field
### deployment
Manages deployments, cycles, and reports. Handles upload of excel and CSV data into the database.

### asset
Manages assets and asset reports. Handles upload of excel and CSV data into the database.

### reporting

### kpi