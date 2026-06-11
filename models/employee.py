"""
DineStay - Hotel & Restaurant Management System
models/employee.py

Demonstrates:
- Encapsulation: name mangling for __salary
- __str__ and __repr__
- Lambda for sorting employees by salary
- datetime for timestamps
"""

from datetime import datetime


# ─────────────────────────────────────────────
# Employee Class
# OOP Concept: Encapsulation (private __salary)
# ─────────────────────────────────────────────
class Employee:
    """
    Represents a hotel employee.
    Salary is kept private via name mangling.
    """

    def __init__(self, employee_id: int, name: str,
                 designation: str, salary: float, department: str):
        self.employee_id = employee_id
        self.name = name
        self.designation = designation
        self.department = department

        # Encapsulation: name-mangled private salary
        self.__salary = salary

        # datetime: record when the employee was added
        self.joined_on = datetime.now()

    # ── Property for salary (encapsulated) ──
    @property
    def salary(self) -> float:
        return self.__salary

    @salary.setter
    def salary(self, new_salary: float) -> None:
        if new_salary < 0:
            raise ValueError("Salary cannot be negative.")
        self.__salary = new_salary

    # ── Methods ─────────────────────────────
    def add_employee(self) -> None:
        """Print confirmation that this employee was added."""
        print(f"\n  ✅ Employee '{self.name}' added successfully!")
        print(f"     Employee ID  : {self.employee_id}")
        print(f"     Designation  : {self.designation}")
        print(f"     Department   : {self.department}")
        print(f"     Salary       : ₹{self.__salary:,.2f}")
        print(f"     Joined On    : {self.joined_on.strftime('%d-%m-%Y')}")

    def update_employee(self, name: str = None,
                        designation: str = None,
                        salary: float = None,
                        department: str = None) -> None:
        """Update employee details."""
        if name:
            self.name = name
        if designation:
            self.designation = designation
        if salary is not None:
            self.salary = salary      # Uses setter (validates)
        if department:
            self.department = department
        print(f"  ✅ Employee #{self.employee_id} updated successfully.")

    def display_employee(self) -> None:
        """Display a formatted employee card."""
        print("\n" + "=" * 50)
        print(f"  👤 EMPLOYEE DETAILS")
        print("=" * 50)
        print(f"  ID         : {self.employee_id}")
        print(f"  Name       : {self.name}")
        print(f"  Designation: {self.designation}")
        print(f"  Department : {self.department}")
        print(f"  Salary     : ₹{self.__salary:,.2f}")
        print(f"  Joined On  : {self.joined_on.strftime('%d-%m-%Y')}")
        print("=" * 50)

    def to_dict(self) -> dict:
        """Serialize employee to dict for JSON storage."""
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "designation": self.designation,
            "salary": self.__salary,       # Access mangled attribute
            "department": self.department,
            "joined_on": self.joined_on.isoformat(),
        }

    @staticmethod
    def from_dict(data: dict) -> "Employee":
        """Reconstruct an Employee from a dict."""
        e = Employee(
            employee_id=data["employee_id"],
            name=data["name"],
            designation=data["designation"],
            salary=data["salary"],
            department=data["department"],
        )
        e.joined_on = datetime.fromisoformat(data["joined_on"])
        return e

    def __str__(self) -> str:
        return (f"Employee #{self.employee_id}: {self.name} "
                f"| {self.designation} [{self.department}]"
                f" | Salary: ₹{self.__salary:,.2f}")

    def __repr__(self) -> str:
        return (f"Employee(id={self.employee_id}, "
                f"name='{self.name}', dept='{self.department}')")
