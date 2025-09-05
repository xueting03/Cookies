# Documentation for src\main\java\com\example\EmployeeManagementSystem\model\Employee.java

Generated on: 2025-09-05 22:42:15
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
Employee employee = new Employee();
int id = employee.getId();
System.out.println("Employee ID: " + id);
```

## Important Notes
- This function does not require any parameters as it retrieves the ID of the employee directly from the object.\n\n---\n\n# Function: setId

## Description
This function sets the ID of an employee in the Employee Management System.

## Parameters
- id: The unique identifier for the employee.

## Usage Example
```java
Employee employee = new Employee();
employee.setId(12345);
```

## Notes
- This function is crucial for assigning a unique identifier to each employee in the system.
- Make sure to use a valid ID format when calling this function.\n\n---\n\n# setFirstname Function Documentation

## Description
The `setFirstname` function is used to set the first name of an employee in the Employee Management System.

## Parameters
- `firstname`: The first name of the employee to be set.

## Usage Example
```java
Employee employee = new Employee();
employee.setFirstname("John");
```

## Important Notes
- This function should be used to update the first name of an employee in the system.
- Ensure that the `firstname` parameter is a valid string value before calling this function.\n\n---\n\n# setLastname

## Description
This function sets the last name of an employee in the Employee Management System.

## Parameters
- `lastname`: The last name of the employee to be set.

## Usage Example
```java
Employee employee = new Employee();
employee.setLastname("Doe");
```

## Important Notes
- This function should be called after creating an instance of the `Employee` class to set the last name of the employee.\n\n---\n\n# setEmail Function Documentation

## Description
The `setEmail` function is used to set the email address of an employee in the Employee Management System.

## Parameters
- `email`: The email address to be set for the employee.

## Usage Example
```java
Employee employee = new Employee();
employee.setEmail("john.doe@example.com");
```

## Important Notes
- This function should be used to update the email address of an employee in the system.
- Ensure that the email address provided is in a valid format.\n\n---\n\n# Function: getFirstname

## Description
This function returns the first name of the employee.

## Parameters
None

## Usage Example
```java
Employee employee = new Employee();
String firstName = employee.getFirstname();
System.out.println("First Name: " + firstName);
```

## Important Notes
- This function is part of the Employee class in the EmployeeManagementSystem.
- Make sure the Employee object is properly instantiated before calling this function.\n\n---\n\n# getLastname

## Description
This function returns the last name of the employee.

## Parameters
None

## Usage Example
```java
Employee employee = new Employee("John", "Doe", 30, "john.doe@example.com");
String lastName = employee.getLastname();
System.out.println("Last Name: " + lastName);
```

## Important Notes
- This function is part of the Employee class in the Employee Management System.
- Ensure that the Employee object is properly instantiated before calling this function.\n\n---\n\n# Function: getEmail

## Description:
This function returns the email address of the employee.

## Parameters:
None

## Usage Example:
```java
Employee employee = new Employee();
String email = employee.getEmail();
System.out.println("Employee email: " + email);
```

## Important Notes:
- This function assumes that the email address of the employee has been set previously.\n\n---\n\n