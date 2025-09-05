# Documentation for src\main\java\com\example\EmployeeManagementSystem\dto\DtoEmployee.java

Generated on: 2025-09-05 22:41:57
Repository: C:\Users\User\VisualStudio\Employee-Management-Sys\EmployeeManagementSystem
Language: java

---

# Function: getId

## Description
This function returns the ID of the employee.

## Parameters
None

## Usage Example
```java
DtoEmployee employee = new DtoEmployee();
int id = employee.getId();
System.out.println("Employee ID: " + id);
```

## Important Notes
- This function does not require any parameters as it simply retrieves the ID of the employee.\n\n---\n\n# setId Function Documentation

## Description
The `setId` function is used to set the ID of an employee in the DTO (Data Transfer Object) for the Employee Management System.

## Parameters
- id: The ID of the employee to be set.

## Usage Example
```java
DtoEmployee employee = new DtoEmployee();
employee.setId(12345);
```

## Important Notes
- This function should only be used to set the ID of an employee in the DTO.
- Ensure that the ID provided is unique and follows any constraints set by the system.\n\n---\n\n# setFirstname

## Description
This function sets the first name of an employee in the DTO object.

## Parameters
- `firstname`: The first name of the employee to be set.

## Usage Example
```java
DtoEmployee employee = new DtoEmployee();
employee.setFirstname("John");
```

## Important Notes
- This function is part of the DtoEmployee class located in the specified file path.
- Ensure that the parameter `firstname` is a valid string value.\n\n---\n\n# Function: setLastname

## Description
This function sets the last name of an employee in the DTO object.

## Parameters
- `lastname`: The last name of the employee to be set.

## Usage Example
```java
DtoEmployee employee = new DtoEmployee();
employee.setLastname("Doe");
```

## Important Notes
- This function is part of the DtoEmployee class located in the specified file path.
- Ensure that the last name provided is a valid string value.\n\n---\n\n# setEmail Function Documentation

## Description
The `setEmail` function is used to set the email address of an employee in the DTO (Data Transfer Object) class `DtoEmployee`.

## Parameters
- `email`: The email address to be set for the employee.

## Usage Example
```java
DtoEmployee employee = new DtoEmployee();
employee.setEmail("john.doe@example.com");
```

## Important Notes
- This function should be used to update the email address of an employee in the DTO class.
- Ensure that the email address provided is valid and follows the standard email format.\n\n---\n\n# getFirstname

## Description
This function returns the first name of the employee from the DTO object.

## Parameters
None

## Usage Example
```java
DtoEmployee employee = new DtoEmployee();
String firstName = employee.getFirstname();
System.out.println("First Name: " + firstName);
```

## Important Notes
- This function assumes that the DTO object has a valid first name stored in it.\n\n---\n\n# getLastname

## Description
This function retrieves the last name of an employee from the DTO object.

## Parameters
None

## Usage Example
```java
DtoEmployee employee = new DtoEmployee();
String lastName = employee.getLastname();
System.out.println("Last Name: " + lastName);
```

## Important Notes
- This function assumes that the DTO object has been properly initialized with the employee's information.\n\n---\n\n# getEmail Function Documentation

## Description
This function retrieves the email address of the employee from the DtoEmployee object.

## Parameters
None

## Usage Example
```java
DtoEmployee employee = new DtoEmployee();
employee.setEmail("john.doe@example.com");

String email = employee.getEmail();
System.out.println("Employee email: " + email);
```

## Important Notes
- This function assumes that the email address has been previously set using the setEmail method.\n\n---\n\n